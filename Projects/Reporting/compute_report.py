#!/usr/bin/env python3
"""
Exec Report Data Engine — Knotch

Standalone script that calls HubSpot REST API, computes all report KPIs,
and outputs a deterministic JSON file. Claude prompts consume this JSON
to format the narrative report.

Usage:
  python3 compute_report.py --mode monthly --quarter Q2
  python3 compute_report.py --mode quarterly --quarter Q1 --dry-run
  python3 compute_report.py --mode monthly --quarter Q2 --output /tmp/my_report.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")

# --- Fiscal Calendar ---

FISCAL_QUARTERS = {
    "FY27": {
        "Q1": ("2026-02-01", "2026-04-30"),
        "Q2": ("2026-05-01", "2026-07-31"),
        "Q3": ("2026-08-01", "2026-10-31"),
        "Q4": ("2026-11-01", "2027-01-31"),
    },
    "FY26": {
        "Q1": ("2025-02-01", "2025-04-30"),
        "Q2": ("2025-05-01", "2025-07-31"),
        "Q3": ("2025-08-01", "2025-10-31"),
        "Q4": ("2025-11-01", "2026-01-31"),
    },
}

QUARTERLY_TARGETS = {
    "FY27": {
        "Q1": {"bookings": 1100000, "ipms": 24, "pipeline": 6250000},
        "Q2": {"bookings": 1100000, "ipms": 24, "pipeline": 6250000},
        "Q3": {"bookings": 1200000, "ipms": 24, "pipeline": 6250000},
        "Q4": {"bookings": 1200000, "ipms": 24, "pipeline": 6250000},
    }
}

# --- HubSpot Field Mapping ---

PIPELINE_ID = "72018330"

STAGES = {
    "152446547": "IPM",
    "152455272": "Qualification",
    "138620983": "Consensus",
    "138620984": "Proposal",
    "138620985": "Procurement",
    "138620988": "Closed Won",
    "138669962": "Closed Lost",
}

LATE_STAGES = ["138620984", "138620985"]
QUAL_PLUS = ["152455272", "138620983", "138620984", "138620985"]
OPEN_STAGES = ["152446547", "152455272", "138620983", "138620984", "138620985"]

OWNERS = {
    "693091902": "Don Vanderslice",
    "349190077": "Lee Fine",
    "81700088": "Tim Long",
    "87170480": "Pete Davies",
    "702586472": "Eli Grant",
    "723668113": "David Brown",
    "723668771": "Andrew Bolton",
    "627390764": "Ben Smith",
    "88616151": "Brian Calahan",
    "889074486": "Tommy Shaker",
    "758553440": "Ryan Ruxton",
    "2110079045": "Carolyn Scott",
}

NB_TEAM = ["693091902", "349190077", "81700088", "87170480"]


# --- HubSpot API Client ---


class HubSpotClient:
    BASE = "https://api.hubapi.com"

    def __init__(self, api_key, dry_run=False):
        self.headers = {
            "Authorization": f"Bearer {api_key}" if api_key else "",
            "Content-Type": "application/json",
        }
        self.dry_run = dry_run
        self._call_count = 0

    def search_deals(self, filters, properties, sorts=None, limit=200):
        return self._search("deals", filters, properties, sorts, limit)

    def search_objects(self, object_type, filters, properties, sorts=None, limit=200):
        return self._search(object_type, filters, properties, sorts, limit)

    def _search(self, object_type, filters, properties, sorts=None, limit=200):
        url = f"{self.BASE}/crm/v3/objects/{object_type}/search"
        body = {
            "filterGroups": [{"filters": filters}],
            "properties": properties,
            "limit": min(limit, 200),
        }
        if sorts:
            body["sorts"] = sorts

        if self.dry_run:
            print(f"[DRY-RUN] POST {url}")
            print(f"  Filters: {json.dumps(filters, indent=2)}")
            print(f"  Properties: {properties}")
            return []

        all_results = []
        after = None
        while True:
            if after:
                body["after"] = after
            self._call_count += 1
            resp = requests.post(url, headers=self.headers, json=body, timeout=30)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 10))
                print(f"  Rate limited, sleeping {retry_after}s...", file=sys.stderr)
                time.sleep(retry_after)
                continue

            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            all_results.extend(results)

            paging = data.get("paging", {}).get("next", {})
            after = paging.get("after")
            if not after:
                break

        return all_results


# --- Helper Functions ---


def parse_dollars(value):
    if not value:
        return 0
    try:
        return round(float(value))
    except (ValueError, TypeError):
        return 0


def to_et(iso_string):
    if not iso_string:
        return None
    dt = datetime.fromisoformat(iso_string)
    return dt.astimezone(ET)


def owner_name(owner_id):
    return OWNERS.get(str(owner_id), f"Unknown ({owner_id})")


def classify_deal_type(dealtype):
    if dealtype == "New License":
        return "New Biz"
    return "Upsell"


def classify_ace_k1(dealname):
    name_upper = (dealname or "").upper()
    if "ACE" in name_upper:
        return "ACE"
    return "K1"


def date_to_epoch_ms(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=ET)
    return str(int(dt.astimezone(timezone.utc).timestamp() * 1000))


def end_of_day_epoch_ms(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59, tzinfo=ET
    )
    return str(int(dt.astimezone(timezone.utc).timestamp() * 1000))


def last_month_of_quarter(q_start, q_end):
    end_date = date.fromisoformat(q_end)
    start_of_last_month = end_date.replace(day=1)
    return str(start_of_last_month), q_end


# --- Configuration ---


def build_config(args):
    fy = args.fy
    q = args.quarter
    q_start, q_end = FISCAL_QUARTERS[fy][q]

    q_num = int(q[1])
    if q_num < 4:
        next_q = f"Q{q_num + 1}"
        next_q_fy = fy
    else:
        next_q = "Q1"
        next_q_fy = f"FY{int(fy[2:]) + 1}"
    next_q_start, next_q_end = FISCAL_QUARTERS.get(next_q_fy, {}).get(
        next_q, (None, None)
    )

    prior_fy = f"FY{int(fy[2:]) - 1}"
    prior_q_start, prior_q_end = FISCAL_QUARTERS.get(prior_fy, {}).get(q, (None, None))

    return {
        "mode": args.mode,
        "quarter": q,
        "fiscal_year": fy,
        "quarter_start": q_start,
        "quarter_end": q_end,
        "next_q": next_q,
        "next_q_start": next_q_start,
        "next_q_end": next_q_end,
        "prior_q_start": prior_q_start,
        "prior_q_end": prior_q_end,
        "targets": QUARTERLY_TARGETS.get(fy, {}).get(q, {}),
        "dry_run": args.dry_run,
        "ptm_path": os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Brian - Copy of FY27 Leadership PTMs.xlsx",
        ),
    }


def build_meta(config):
    now = datetime.now(ET)
    return {
        "mode": config["mode"],
        "quarter": config["quarter"],
        "fiscal_year": config["fiscal_year"],
        "quarter_start": config["quarter_start"],
        "quarter_end": config["quarter_end"],
        "generated_at": now.isoformat(),
        "generated_at_display": now.strftime("%A, %B %d, %Y at %I:%M %p ET"),
    }


# --- Section Compute Functions (stubs — filled in Task 3 & 4) ---


def compute_bookings(client, config):
    return {}


def compute_activity(client, config):
    return {}


def compute_pipeline(client, config):
    return {}


def compute_data_quality(client, config):
    return {}


def compute_market_feedback(client, config):
    return {}


def compute_seller_performance(client, config):
    return {}


def compute_initiatives(config):
    return {}


# --- Main ---


def parse_args():
    p = argparse.ArgumentParser(description="Knotch Exec Report Data Engine")
    p.add_argument(
        "--mode",
        required=True,
        choices=["monthly", "quarterly"],
        help="Report mode: monthly (sections 1-3) or quarterly (sections 1-6)",
    )
    p.add_argument(
        "--quarter",
        required=True,
        choices=["Q1", "Q2", "Q3", "Q4"],
        help="Fiscal quarter to report on",
    )
    p.add_argument("--fy", default="FY27", help="Fiscal year (default: FY27)")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print API calls without executing",
    )
    p.add_argument(
        "--output",
        default="/tmp/exec_report_data.json",
        help="Output JSON path (default: /tmp/exec_report_data.json)",
    )
    return p.parse_args()


def main():
    args = parse_args()
    api_key = os.environ.get("HUBSPOT_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: HUBSPOT_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    config = build_config(args)
    client = HubSpotClient(api_key, dry_run=args.dry_run)

    report = {
        "meta": build_meta(config),
        "targets": config["targets"],
        "data_quality": {},
    }

    report["bookings"] = compute_bookings(client, config)
    report["activity"] = compute_activity(client, config)
    report["pipeline"] = compute_pipeline(client, config)
    report["data_quality"] = compute_data_quality(client, config)

    if args.mode == "quarterly":
        report["market_feedback"] = compute_market_feedback(client, config)
        report["seller_performance"] = compute_seller_performance(client, config)
        report["initiatives"] = compute_initiatives(config)

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
