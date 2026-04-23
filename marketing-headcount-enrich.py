#!/usr/bin/env python3
"""
Marketing Headcount Enrichment — Knotch HubSpot Portal 44523005

Fills marketing_headcount for companies missing it using Apollo's
departmental_head_count.marketing field via org enrichment API.

Usage:
  python3 marketing-headcount-enrich.py                    # dry run
  python3 marketing-headcount-enrich.py --push             # execute
"""

import json
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: pip3 install requests")
    sys.exit(1)

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY")

HUBSPOT_BASE = "https://api.hubapi.com"
APOLLO_BASE = "https://api.apollo.io"
BATCH_SIZE = 100
RATE_LIMIT_DELAY = 0.15

SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


def hs_headers():
    return {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }


def search_companies_missing_mktg_hc():
    """Find all tiered companies where marketing_headcount is empty."""
    url = f"{HUBSPOT_BASE}/crm/v3/objects/companies/search"
    all_results = []

    for tier in ["I", "II", "III"]:
        after = 0
        while True:
            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "account_tier",
                                "operator": "EQ",
                                "value": tier,
                            },
                            {
                                "propertyName": "marketing_headcount",
                                "operator": "NOT_HAS_PROPERTY",
                            },
                        ]
                    }
                ],
                "properties": ["name", "domain", "marketing_headcount", "account_tier"],
                "limit": 100,
                "after": after,
            }
            resp = requests.post(url, headers=hs_headers(), json=payload)
            if resp.status_code == 429:
                time.sleep(int(resp.headers.get("Retry-After", 10)))
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

        log.info(
            f"  Tier {tier}: {len([r for r in all_results if r['properties'].get('account_tier') == tier])} missing marketing_headcount"
        )

    return all_results


def enrich_apollo_batch(domains):
    """Enrich up to 10 domains via Apollo bulk org enrichment."""
    url = f"{APOLLO_BASE}/api/v1/organizations/bulk_enrich"
    payload = {"api_key": APOLLO_API_KEY, "domains": domains}
    resp = requests.post(url, json=payload)

    if resp.status_code == 429:
        retry = int(resp.headers.get("Retry-After", 10))
        log.warning(f"  Apollo rate limited, waiting {retry}s...")
        time.sleep(retry)
        resp = requests.post(url, json=payload)

    if resp.status_code != 200:
        log.error(f"  Apollo error: {resp.status_code} {resp.text[:200]}")
        return {}

    data = resp.json()
    results = {}
    orgs = data.get("organizations", [])
    for org in orgs:
        if not org:
            continue
        domain = (
            (org.get("primary_domain") or org.get("website_url") or "")
            .replace("https://", "")
            .replace("http://", "")
            .rstrip("/")
        )
        dept = org.get("departmental_head_count") or {}
        mktg = dept.get("marketing")
        if domain and mktg is not None:
            results[domain.lower()] = int(mktg)

    return results


def batch_update_hubspot(updates, dry_run=True):
    """Push updates to HubSpot in batches of 100."""
    url = f"{HUBSPOT_BASE}/crm/v3/objects/companies/batch/update"
    total_ok = 0
    total_fail = 0

    batches = [updates[i : i + BATCH_SIZE] for i in range(0, len(updates), BATCH_SIZE)]
    for i, batch in enumerate(batches):
        if dry_run:
            log.info(
                f"  [DRY RUN] Batch {i + 1}/{len(batches)}: {len(batch)} companies"
            )
            total_ok += len(batch)
            continue

        resp = requests.post(url, headers=hs_headers(), json={"inputs": batch})
        if resp.status_code == 200:
            total_ok += len(batch)
        elif resp.status_code == 429:
            time.sleep(int(resp.headers.get("Retry-After", 10)))
            resp2 = requests.post(url, headers=hs_headers(), json={"inputs": batch})
            if resp2.status_code == 200:
                total_ok += len(batch)
            else:
                total_fail += len(batch)
                log.error(f"  Batch {i + 1} retry failed: {resp2.status_code}")
        else:
            total_fail += len(batch)
            log.error(f"  Batch {i + 1} failed: {resp.status_code} {resp.text[:200]}")
        time.sleep(RATE_LIMIT_DELAY)

    return total_ok, total_fail


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Enrich marketing headcount via Apollo"
    )
    parser.add_argument(
        "--push", action="store_true", help="Execute (default: dry run)"
    )
    args = parser.parse_args()
    dry_run = not args.push

    if not HUBSPOT_API_KEY:
        log.error("Missing HUBSPOT_API_KEY")
        sys.exit(1)
    if not APOLLO_API_KEY:
        log.error("Missing APOLLO_API_KEY")
        sys.exit(1)

    if dry_run:
        log.info("*** DRY RUN MODE ***\n")
    else:
        log.info("*** LIVE MODE — writing to HubSpot ***\n")

    # Step 1: Pull companies missing marketing_headcount
    log.info("Finding companies missing marketing_headcount...")
    companies = search_companies_missing_mktg_hc()
    log.info(f"Total missing: {len(companies)}")

    # Build domain -> company mapping
    domain_map = {}
    no_domain = []
    for co in companies:
        props = co.get("properties", {})
        domain = (props.get("domain") or "").strip().lower()
        if domain:
            domain_map[domain] = {
                "id": co["id"],
                "name": props.get("name", "unknown"),
                "tier": props.get("account_tier", "?"),
            }
        else:
            no_domain.append(props.get("name", "unknown"))

    log.info(f"  With domains: {len(domain_map)}")
    log.info(f"  No domain (skipping): {len(no_domain)}")

    # Step 2: Enrich via Apollo in batches of 10
    log.info("\nEnriching via Apollo...")
    domains = list(domain_map.keys())
    enriched = {}
    apollo_miss = []

    for i in range(0, len(domains), 10):
        batch = domains[i : i + 10]
        batch_num = i // 10 + 1
        total_batches = (len(domains) + 9) // 10

        results = enrich_apollo_batch(batch)

        for d in batch:
            if d in results:
                enriched[d] = results[d]
            else:
                apollo_miss.append(d)

        found = len(results)
        log.info(f"  Batch {batch_num}/{total_batches}: {found}/{len(batch)} found")
        time.sleep(0.5)

    log.info(f"\nApollo results: {len(enriched)} found, {len(apollo_miss)} missed")

    # Step 3: Push to HubSpot
    updates = []
    for domain, mktg_hc in enriched.items():
        co = domain_map[domain]
        updates.append(
            {
                "id": co["id"],
                "properties": {"marketing_headcount": str(mktg_hc)},
            }
        )

    if updates:
        log.info(f"\nPushing {len(updates)} marketing headcount values to HubSpot...")
        ok, fail = batch_update_hubspot(updates, dry_run=dry_run)
        log.info(f"  Result: {ok} ok, {fail} fail")
    else:
        log.info("\nNo updates to push")

    # Summary
    log.info(f"\n{'=' * 60}")
    log.info("MARKETING HEADCOUNT ENRICHMENT COMPLETE")
    log.info(f"{'=' * 60}")
    log.info(f"  Companies missing marketing_headcount: {len(companies)}")
    log.info(f"  No domain (skipped): {len(no_domain)}")
    log.info(f"  Apollo enriched: {len(enriched)}")
    log.info(f"  Apollo missed: {len(apollo_miss)}")
    log.info(f"  HubSpot updates: {len(updates)}")

    if enriched:
        vals = list(enriched.values())
        log.info(
            f"  Marketing HC range: {min(vals)} - {max(vals)} (median: {sorted(vals)[len(vals) // 2]})"
        )

    if dry_run:
        log.info(f"\n  [DRY RUN — re-run with --push to execute]")

    # Write log with Apollo misses for Clay follow-up
    LOG_DIR.mkdir(exist_ok=True)
    log_file = (
        LOG_DIR / f"mktg-hc-enrich-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    )
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "mode": "dry_run" if dry_run else "live",
        "total_missing": len(companies),
        "no_domain": no_domain,
        "apollo_enriched": len(enriched),
        "apollo_missed_domains": apollo_miss,
        "apollo_missed_companies": [
            {
                "domain": d,
                "name": domain_map[d]["name"],
                "tier": domain_map[d]["tier"],
                "id": domain_map[d]["id"],
            }
            for d in apollo_miss
        ],
        "hubspot_updates": len(updates),
    }
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)
    log.info(f"  Log (includes Apollo misses for Clay): {log_file}")


if __name__ == "__main__":
    main()
