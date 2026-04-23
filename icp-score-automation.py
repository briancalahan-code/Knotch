#!/usr/bin/env python3
"""
ICP Scoring Automation — Knotch HubSpot Portal 44523005

Computes four-pillar ICP scores for all tiered companies and pushes
results to HubSpot. Safe to re-run — only updates companies whose
scores have changed.

Scoring model: v3 (2026-04-22)
  - Enterprise Fit (25%): revenue (60%) + employees (40%)
  - Digital Maturity (25%): web traffic (50%) + tech stack (30%) + content proxy (20%)
  - Content Investment (25%): content tech count (70%) + marketing headcount (30%)
  - Engagement (25%): events (50%) + contacts (30%) + deals (20%)

  Fixed penalty model: missing data scores 0, no weight redistribution.
  Data completeness score tracks how much data was available per account.

Usage:
  python3 icp-score-automation.py                    # dry run
  python3 icp-score-automation.py --push             # execute
  python3 icp-score-automation.py --push --tier I    # single tier
"""

import json
import math
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip3 install requests")
    sys.exit(1)

HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")
if not HUBSPOT_API_KEY:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent / ".env")
    HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")

BASE_URL = "https://api.hubapi.com"
BATCH_SIZE = 100
RATE_LIMIT_DELAY = 0.15
MODEL_VERSION = "v3"

SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"
CONTENT_TECH_FILE = SCRIPT_DIR / "content-tech-categories.json"

PROPERTIES = [
    "name",
    "account_tier",
    # Enterprise Fit inputs
    "numberofemployees",
    "annualrevenue",
    # Digital Maturity inputs
    "web_technologies",
    "num_technologies",
    "clay__website_traffic_monthly",
    # Content Investment inputs
    "marketing_headcount",
    # Engagement inputs
    "fy25_event_attendance_count",
    "fy26_event_attendance_count",
    "num_associated_contacts",
    "num_associated_deals",
    # Existing scores (change detection)
    "clay__digital_maturity_score",
    "icp_score_composite",
    "icp_score_last_updated",
    "icp_enterprise_fit_score",
    "icp_content_investment_score",
    "icp_engagement_score",
    "icp_data_completeness",
    "icp_model_version",
]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HubSpot API helpers
# ---------------------------------------------------------------------------


def headers():
    return {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }


def search_companies(filter_groups, limit=100):
    url = f"{BASE_URL}/crm/v3/objects/companies/search"
    all_results = []
    after = 0

    while True:
        payload = {
            "filterGroups": filter_groups,
            "properties": PROPERTIES,
            "limit": limit,
            "after": after,
        }
        resp = requests.post(url, headers=headers(), json=payload)

        if resp.status_code == 429:
            retry = int(resp.headers.get("Retry-After", 10))
            log.warning(f"Rate limited, waiting {retry}s...")
            time.sleep(retry)
            continue

        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        all_results.extend(results)

        paging = data.get("paging", {})
        next_page = paging.get("next", {})
        if next_page.get("after"):
            after = int(next_page["after"])
            time.sleep(RATE_LIMIT_DELAY)
        else:
            break

    return all_results


def batch_update(updates, dry_run=True):
    url = f"{BASE_URL}/crm/v3/objects/companies/batch/update"
    total_success = 0
    total_fail = 0

    batches = [updates[i : i + BATCH_SIZE] for i in range(0, len(updates), BATCH_SIZE)]
    for i, batch in enumerate(batches):
        payload = {"inputs": batch}

        if dry_run:
            log.info(
                f"  [DRY RUN] Batch {i + 1}/{len(batches)}: {len(batch)} companies"
            )
            total_success += len(batch)
            continue

        resp = requests.post(url, headers=headers(), json=payload)
        if resp.status_code == 200:
            total_success += len(batch)
        elif resp.status_code == 429:
            retry = int(resp.headers.get("Retry-After", 10))
            log.warning(f"  Rate limited, waiting {retry}s...")
            time.sleep(retry)
            resp2 = requests.post(url, headers=headers(), json=payload)
            if resp2.status_code == 200:
                total_success += len(batch)
            else:
                total_fail += len(batch)
                log.error(
                    f"  Batch {i + 1} retry FAILED: {resp2.status_code} {resp2.text[:200]}"
                )
        else:
            total_fail += len(batch)
            log.error(f"  Batch {i + 1} FAILED: {resp.status_code} {resp.text[:200]}")

        time.sleep(RATE_LIMIT_DELAY)

        if (i + 1) % 5 == 0 or i == len(batches) - 1:
            log.info(
                f"  Progress: {i + 1}/{len(batches)} batches, {total_success} ok, {total_fail} fail"
            )

    return total_success, total_fail


# ---------------------------------------------------------------------------
# Property management
# ---------------------------------------------------------------------------


def create_property_if_missing(name, label, prop_type, field_type, group, description):
    url = f"{BASE_URL}/crm/v3/properties/companies/{name}"
    resp = requests.get(url, headers=headers())
    if resp.status_code == 200:
        log.info(f"  Property '{name}' already exists")
        return True

    url = f"{BASE_URL}/crm/v3/properties/companies"
    payload = {
        "name": name,
        "label": label,
        "type": prop_type,
        "fieldType": field_type,
        "groupName": group,
        "description": description,
    }
    resp = requests.post(url, headers=headers(), json=payload)
    if resp.status_code in (200, 201):
        log.info(f"  Created property '{name}'")
        return True
    else:
        log.error(
            f"  Failed to create property '{name}': {resp.status_code} {resp.text[:300]}"
        )
        return False


def ensure_properties(dry_run=True):
    log.info("Checking v3 HubSpot properties...")
    new_props = [
        (
            "icp_enterprise_fit_score",
            "ICP Enterprise Fit Score",
            "number",
            "number",
            "ICP v3 Enterprise Fit pillar (0-100). Revenue 60% + Employee count 40%.",
        ),
        (
            "icp_content_investment_score",
            "ICP Content Investment Score",
            "number",
            "number",
            "ICP v3 Content Investment pillar (0-100). Content tech count 70% + Marketing headcount 30%.",
        ),
        (
            "icp_engagement_score",
            "ICP Engagement Score",
            "number",
            "number",
            "ICP v3 Engagement pillar (0-100). Events 50% + Contacts 30% + Deals 20%.",
        ),
        (
            "icp_data_completeness",
            "ICP Data Completeness",
            "number",
            "number",
            "Percentage of available data used in ICP score (0-100). Higher = more data-backed score.",
        ),
        (
            "icp_model_version",
            "ICP Model Version",
            "string",
            "text",
            "Version of the ICP scoring model (e.g. v3).",
        ),
    ]
    if dry_run:
        for name, label, *_ in new_props:
            log.info(f"  [DRY RUN] Would ensure property '{name}'")
        return

    for name, label, prop_type, field_type, description in new_props:
        create_property_if_missing(
            name, label, prop_type, field_type, "companyinformation", description
        )


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def safe_float(val, default=0):
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_float_or_none(val):
    """Returns float or None (for fixed-penalty fields where None != 0)."""
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def load_content_tech_map():
    if not CONTENT_TECH_FILE.exists():
        log.error(f"Missing content tech mapping: {CONTENT_TECH_FILE}")
        log.error("Run Task 1 first — see docs/plans/2026-04-22-icp-scoring-v3-plan.md")
        sys.exit(1)
    with open(CONTENT_TECH_FILE) as f:
        return json.load(f)


def count_content_techs(web_technologies_str, content_map):
    if not web_technologies_str:
        return 0
    techs = [t.strip() for t in web_technologies_str.split(";") if t.strip()]
    return sum(1 for t in techs if t in content_map)


# ---------------------------------------------------------------------------
# Pillar 1: Enterprise Fit (25% of composite)
# ---------------------------------------------------------------------------


def score_revenue(revenue):
    """Log-scale revenue score, capped at $5B. Returns 0-85."""
    if revenue <= 0:
        return 0
    if revenue >= 5_000_000_000:
        return 85
    log_val = math.log10(max(revenue, 1))
    return min(85, max(0, (log_val - 5) / 4.7 * 85))


def score_employees(employees):
    """Enterprise-weighted employee curve. Returns 0-100."""
    if employees >= 100_000:
        return 100
    if employees >= 50_000:
        return 80 + (employees - 50_000) / 50_000 * 20
    if employees >= 10_000:
        return 50 + (employees - 10_000) / 40_000 * 30
    if employees >= 5_000:
        return 30 + (employees - 5_000) / 5_000 * 20
    if employees >= 1_000:
        return 10 + (employees - 1_000) / 4_000 * 20
    return employees / 1_000 * 10


def compute_enterprise_fit(revenue, employees):
    return round(score_revenue(revenue) * 0.60 + score_employees(employees) * 0.40, 1)


# ---------------------------------------------------------------------------
# Pillar 2: Digital Maturity (25% of composite)
# ---------------------------------------------------------------------------


def compute_digital_maturity(web_traffic, tech_count):
    # Web Traffic (50%)
    if web_traffic <= 0:
        traffic_score = 0
    elif web_traffic >= 20_000_000:
        traffic_score = 100
    else:
        log_val = math.log10(max(web_traffic, 1))
        traffic_score = min(100, max(0, (log_val - 4) / 3.3 * 100))

    # Tech Stack Breadth (30%)
    if tech_count >= 600:
        tech_score = 100
    elif tech_count >= 400:
        tech_score = 70 + (tech_count - 400) / 200 * 30
    elif tech_count >= 200:
        tech_score = 40 + (tech_count - 200) / 200 * 30
    else:
        tech_score = tech_count / 200 * 40

    # Content/SEO Proxy (20%)
    content_proxy = min(100, tech_count / 6)

    return round(traffic_score * 0.50 + tech_score * 0.30 + content_proxy * 0.20, 1)


# ---------------------------------------------------------------------------
# Pillar 3: Content Investment (25% of composite)
# ---------------------------------------------------------------------------


def score_content_tech(count):
    """Absolute count of content-related technologies. Returns 0-100."""
    if count >= 30:
        return 100
    if count >= 20:
        return 85 + (count - 20) / 10 * 15
    if count >= 15:
        return 70 + (count - 15) / 5 * 15
    if count >= 10:
        return 50 + (count - 10) / 5 * 20
    if count >= 5:
        return 30 + (count - 5) / 5 * 20
    return count / 5 * 30


def score_marketing_headcount(headcount):
    """Marketing team size. None = fixed penalty (scores 0)."""
    if headcount is None:
        return 0
    if headcount >= 50:
        return 100
    if headcount >= 21:
        return 80 + (headcount - 21) / 29 * 20
    if headcount >= 6:
        return 60 + (headcount - 6) / 15 * 20
    if headcount >= 1:
        return 30 + (headcount - 1) / 5 * 30
    return 0


def compute_content_investment(content_tech_count, marketing_headcount):
    return round(
        score_content_tech(content_tech_count) * 0.70
        + score_marketing_headcount(marketing_headcount) * 0.30,
        1,
    )


# ---------------------------------------------------------------------------
# Pillar 4: Engagement (25% of composite)
# ---------------------------------------------------------------------------


def score_events(fy25_count, fy26_count):
    total = (fy25_count or 0) + (fy26_count or 0)
    if total >= 10:
        return 100
    if total >= 6:
        return 75 + (total - 6) / 4 * 25
    if total >= 3:
        return 50 + (total - 3) / 3 * 25
    if total >= 1:
        return 30 + (total - 1) / 2 * 20
    return 0


def score_contacts(count):
    if count >= 50:
        return 100
    if count >= 31:
        return 80 + (count - 31) / 19 * 20
    if count >= 16:
        return 60 + (count - 16) / 15 * 20
    if count >= 6:
        return 40 + (count - 6) / 10 * 20
    if count >= 2:
        return 20 + (count - 2) / 4 * 20
    return 0


def score_deals(count):
    if count >= 7:
        return 100
    if count >= 4:
        return 80 + (count - 4) / 3 * 20
    if count >= 2:
        return 60 + (count - 2) / 2 * 20
    if count >= 1:
        return 40
    return 0


def compute_engagement(fy25_events, fy26_events, contacts, deals):
    return round(
        score_events(fy25_events, fy26_events) * 0.50
        + score_contacts(contacts) * 0.30
        + score_deals(deals) * 0.20,
        1,
    )


# ---------------------------------------------------------------------------
# Data completeness
# ---------------------------------------------------------------------------


def compute_data_completeness(
    tech_count,
    content_tech_count,
    marketing_hc,
    fy25_events,
    fy26_events,
    contacts,
    deals,
):
    score = 25.0  # Enterprise Fit: always present (revenue + employees at 100%)
    score += 25.0 if tech_count > 0 else 0
    score += 17.5 if content_tech_count > 0 else 0
    score += 7.5 if marketing_hc is not None else 0
    score += 12.5 if ((fy25_events or 0) + (fy26_events or 0)) > 0 else 0
    score += 7.5 if contacts > 0 else 0
    score += 5.0 if deals > 0 else 0
    return round(score, 1)


# ---------------------------------------------------------------------------
# Main scoring loop
# ---------------------------------------------------------------------------


def score_companies(companies, content_map):
    results = []
    missing = {
        "revenue": 0,
        "employees": 0,
        "tech_stack": 0,
        "content_tech": 0,
        "marketing_hc": 0,
        "events": 0,
        "contacts": 0,
        "deals": 0,
    }

    for co in companies:
        props = co.get("properties", {})
        co_id = co["id"]
        name = props.get("name", "unknown")

        # Extract inputs
        revenue = safe_float(props.get("annualrevenue"))
        employees = safe_float(props.get("numberofemployees"))
        web_traffic = safe_float(props.get("clay__website_traffic_monthly"))

        tech_count = safe_float(props.get("num_technologies"))
        if tech_count == 0:
            wt = props.get("web_technologies", "") or ""
            tech_count = len([t for t in wt.split(";") if t.strip()])

        web_techs_str = props.get("web_technologies", "") or ""
        content_tech_count = count_content_techs(web_techs_str, content_map)
        marketing_hc = safe_float_or_none(props.get("marketing_headcount"))

        fy25_events = safe_float(props.get("fy25_event_attendance_count"))
        fy26_events = safe_float(props.get("fy26_event_attendance_count"))
        contacts = safe_float(props.get("num_associated_contacts"))
        deals = safe_float(props.get("num_associated_deals"))

        # Track missing data
        if revenue == 0:
            missing["revenue"] += 1
        if employees == 0:
            missing["employees"] += 1
        if tech_count == 0:
            missing["tech_stack"] += 1
        if content_tech_count == 0:
            missing["content_tech"] += 1
        if marketing_hc is None:
            missing["marketing_hc"] += 1
        if (fy25_events + fy26_events) == 0:
            missing["events"] += 1
        if contacts == 0:
            missing["contacts"] += 1
        if deals == 0:
            missing["deals"] += 1

        # Compute four pillars
        ef = compute_enterprise_fit(revenue, employees)
        dm = compute_digital_maturity(web_traffic, tech_count)
        ci = compute_content_investment(content_tech_count, marketing_hc)
        en = compute_engagement(fy25_events, fy26_events, contacts, deals)

        # Composite (equal weights, no redistribution)
        icp = round(ef * 0.25 + dm * 0.25 + ci * 0.25 + en * 0.25, 1)

        # Data completeness metadata
        dc = compute_data_completeness(
            tech_count,
            content_tech_count,
            marketing_hc,
            fy25_events,
            fy26_events,
            contacts,
            deals,
        )

        # Change detection
        old_icp = safe_float(props.get("icp_score_composite"), -1)
        old_dm = safe_float(props.get("clay__digital_maturity_score"), -1)
        old_version = props.get("icp_model_version", "")
        changed = (
            round(old_icp, 1) != icp
            or round(old_dm, 1) != dm
            or old_version != MODEL_VERSION
        )

        results.append(
            {
                "id": co_id,
                "name": name,
                "tier": props.get("account_tier", "?"),
                "ef_score": ef,
                "dm_score": dm,
                "ci_score": ci,
                "en_score": en,
                "icp_score": icp,
                "data_completeness": dc,
                "content_tech_count": content_tech_count,
                "old_icp": old_icp,
                "old_dm": old_dm,
                "changed": changed,
            }
        )

    return results, missing


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="ICP Scoring v3 — Knotch HubSpot Portal 44523005"
    )
    parser.add_argument(
        "--push", action="store_true", help="Execute changes (default is dry run)"
    )
    parser.add_argument(
        "--tier", choices=["I", "II", "III"], help="Score a single tier (default: all)"
    )
    args = parser.parse_args()

    dry_run = not args.push

    if not HUBSPOT_API_KEY:
        log.error("HUBSPOT_API_KEY not set")
        sys.exit(1)

    # Load content tech classification
    content_map = load_content_tech_map()
    log.info(f"Loaded {len(content_map)} content technology classifications")

    if dry_run:
        log.info("*** DRY RUN MODE — no changes will be made ***\n")
    else:
        log.info("*** LIVE MODE — writing to HubSpot ***\n")

    # Ensure v3 properties exist
    ensure_properties(dry_run=dry_run)

    tiers = [args.tier] if args.tier else ["I", "II", "III"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_results = []
    all_missing = {
        k: 0
        for k in [
            "revenue",
            "employees",
            "tech_stack",
            "content_tech",
            "marketing_hc",
            "events",
            "contacts",
            "deals",
        ]
    }

    for tier in tiers:
        log.info(f"\n{'=' * 60}")
        log.info(f"SCORING TIER {tier}")
        log.info(f"{'=' * 60}")

        companies = search_companies(
            filter_groups=[
                {
                    "filters": [
                        {
                            "propertyName": "account_tier",
                            "operator": "EQ",
                            "value": tier,
                        }
                    ]
                }
            ]
        )
        log.info(f"Found {len(companies)} Tier {tier} companies")

        results, missing = score_companies(companies, content_map)
        all_results.extend(results)
        for k in all_missing:
            all_missing[k] += missing[k]

        changed = [r for r in results if r["changed"]]
        log.info(f"  Scores changed: {len(changed)} / {len(results)}")
        log.info(
            f"  Missing: revenue={missing['revenue']}, employees={missing['employees']}, "
            f"tech={missing['tech_stack']}, content_tech={missing['content_tech']}, "
            f"mktg_hc={missing['marketing_hc']}, events={missing['events']}, "
            f"contacts={missing['contacts']}, deals={missing['deals']}"
        )

        if changed:
            updates = [
                {
                    "id": r["id"],
                    "properties": {
                        "icp_score_composite": str(r["icp_score"]),
                        "clay__digital_maturity_score": str(r["dm_score"]),
                        "icp_enterprise_fit_score": str(r["ef_score"]),
                        "icp_content_investment_score": str(r["ci_score"]),
                        "icp_engagement_score": str(r["en_score"]),
                        "icp_data_completeness": str(r["data_completeness"]),
                        "icp_model_version": MODEL_VERSION,
                        "icp_score_last_updated": now,
                    },
                }
                for r in changed
            ]

            log.info(f"  Pushing {len(updates)} updates...")
            success, fail = batch_update(updates, dry_run=dry_run)
            log.info(f"  Result: {success} success, {fail} fail")
        else:
            log.info("  No updates needed")

    # ---- Summary ----

    high = [r for r in all_results if r["icp_score"] >= 70]
    med = [r for r in all_results if 50 <= r["icp_score"] < 70]
    low = [r for r in all_results if r["icp_score"] < 50]
    changed_total = [r for r in all_results if r["changed"]]

    log.info(f"\n{'=' * 60}")
    log.info(f"SCORING COMPLETE — {len(all_results)} accounts (model {MODEL_VERSION})")
    log.info(f"{'=' * 60}")
    log.info(f"  High (70+):    {len(high)}")
    log.info(f"  Medium (50-69): {len(med)}")
    log.info(f"  Low (<50):     {len(low)}")
    log.info(f"  Changed:       {len(changed_total)}")
    log.info(f"\n  Missing data across all tiers:")
    for k, v in all_missing.items():
        log.info(f"    {k}: {v}")

    # Data completeness distribution
    if all_results:
        dc_vals = [r["data_completeness"] for r in all_results]
        dc_full = sum(1 for d in dc_vals if d == 100)
        dc_high = sum(1 for d in dc_vals if 75 <= d < 100)
        dc_med = sum(1 for d in dc_vals if 50 <= d < 75)
        dc_low = sum(1 for d in dc_vals if d < 50)
        log.info(f"\n  Data Completeness:")
        log.info(f"    100%:   {dc_full}")
        log.info(f"    75-99%: {dc_high}")
        log.info(f"    50-74%: {dc_med}")
        log.info(f"    <50%:   {dc_low}")

    # Top 10
    if all_results:
        top10 = sorted(all_results, key=lambda r: r["icp_score"], reverse=True)[:10]
        log.info(f"\n  Top 10 by ICP Composite:")
        for r in top10:
            delta = ""
            if r["old_icp"] >= 0:
                diff = r["icp_score"] - r["old_icp"]
                if abs(diff) >= 0.1:
                    delta = f" ({'+' if diff > 0 else ''}{diff:.1f})"
            log.info(
                f"    {r['name']}: {r['icp_score']}{delta} "
                f"(T{r['tier']}, EF={r['ef_score']}, DM={r['dm_score']}, "
                f"CI={r['ci_score']}, EN={r['en_score']}, DC={r['data_completeness']}%)"
            )

    if dry_run:
        log.info(f"\n  [DRY RUN — re-run with --push to execute]")

    # Write run log
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"icp-score-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    log_data = {
        "timestamp": now,
        "mode": "dry_run" if dry_run else "live",
        "model_version": MODEL_VERSION,
        "tiers": tiers,
        "total_scored": len(all_results),
        "changed": len(changed_total),
        "distribution": {"high": len(high), "medium": len(med), "low": len(low)},
        "missing_data": all_missing,
        "top_10": [
            {
                "name": r["name"],
                "tier": r["tier"],
                "icp": r["icp_score"],
                "ef": r["ef_score"],
                "dm": r["dm_score"],
                "ci": r["ci_score"],
                "en": r["en_score"],
                "dc": r["data_completeness"],
            }
            for r in sorted(all_results, key=lambda r: r["icp_score"], reverse=True)[
                :10
            ]
        ],
    }
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)
    log.info(f"  Run log: {log_file}")


if __name__ == "__main__":
    main()
