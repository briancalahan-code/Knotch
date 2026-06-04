# Exec Reporting System — Implementation Plan

> **For Claude:** Use parallel subagent execution per the wave table below. No worktrees needed — this is an ops repo, not a code application.

**Goal:** Build a deterministic monthly/quarterly executive sales report system for Pete Davies (Knotch VP Sales). A standalone python3 script calls HubSpot REST API, computes all numbers, and outputs JSON. Claude prompts read the JSON and format the narrative report.

**Architecture:** `compute_report.py` (HubSpot API → deterministic JSON) + two Claude prompts (JSON → formatted report). All shared rules live in `Exec-Report-Data-Spec.md`. Future Google Sheet implements the same spec.

**Tech Stack:** Python 3.10+ (requests, openpyxl, zoneinfo), HubSpot REST API v3, Claude prompts (markdown)

**Test command:** `python3 Projects/Reporting/compute_report.py --mode monthly --quarter Q2 --dry-run` (dry-run prints queries without calling API); `python3 Projects/Reporting/compute_report.py --mode monthly --quarter Q2` (live run, requires HUBSPOT_API_KEY)
**Pre-execution baseline:** No tests — greenfield. QA is running the script and comparing JSON output to HubSpot dashboard numbers.
**Execution mode:** parallel (per wave table)
**MCP servers:** None required for implementation. HubSpot MCP used only for ad-hoc verification during QA.

---

## Discoveries

_Updated by orchestrator at session end. Captures what agents found that the plan didn't anticipate._

---

## Success Criteria

- [ ] `compute_report.py --mode monthly --quarter Q2` produces a JSON file with all Section 1-3 KPIs matching live HubSpot data (verified manually against dashboard view 13149414)
- [ ] `compute_report.py --mode quarterly --quarter Q1` produces a JSON file with all Section 1-6 KPIs, and Bookings total matches the Q1 report PDF ($1,102,500)
- [ ] Monthly prompt (run in Claude) produces a formatted 3-section report with exec summary — all dollar figures match the JSON exactly
- [ ] Quarterly prompt (run in Claude) produces a formatted 6-section report with exec summary — all dollar figures match the JSON, narrative sections are structured (not generic)
- [ ] All timestamps in the report display in Eastern Time
- [ ] `--dry-run` flag prints every HubSpot API call without executing, showing URL + filters (for parity testing with future Apps Script)
- [ ] Script handles pagination correctly (tested with all-open-deals query, which is ~170 records)
- [ ] `initiatives.pete_ptms` in the quarterly JSON output is non-empty (PTM spreadsheet read works)
- [ ] Prompts only run in Claude Code or Claude desktop (bash tool required) — not claude.ai web

---

## Execution Model

**Dependency Graph:**

```
Task 1 (Data Spec) ─────────────────────────────────────────┐
    │                                                        │
Task 2 (Script framework)                                    │
    │                                                        │
Task 3 (Monthly queries: Bookings + Activity + Pipeline)     │
    │                                                        │
Task 4 (Quarterly queries: Market + Seller + Initiatives)    │
    │                                                        │
    ├── Task 5 (Monthly prompt) ──┐                          │
    │                             ├── Task 7 (QA)            │
    └── Task 6 (Quarterly prompt) ┘       │                  │
                                    Task 8 (Docs) ───────────┘
```

**Parallel Waves:**

| Wave   | Tasks          | Dependencies | Gate                                              |
| ------ | -------------- | ------------ | ------------------------------------------------- |
| Wave 1 | Task 1         | None         | Review spec completeness                          |
| Wave 2 | Task 2         | Task 1       | Script runs with `--dry-run`                      |
| Wave 3 | Task 3         | Task 2       | Script produces monthly JSON with real data       |
| Wave 4 | Task 4         | Task 3       | Script produces quarterly JSON with real data     |
| Wave 5 | Task 5, Task 6 | Task 4       | Both prompts written (parallel — different files) |
| Wave 6 | Task 7         | Tasks 5+6    | Numbers match HubSpot dashboard                   |
| Wave 7 | Task 8         | Task 7       | Docs updated                                      |

**Test Gate (between waves):** Since there's no test suite, the gate is:

1. Run `python3 Projects/Reporting/compute_report.py --mode monthly --quarter Q2` (or `--dry-run` for early waves)
2. Check JSON output has expected keys and non-null values
3. For Wave 6: compare dollar totals against HubSpot dashboard

---

## Task 1: Data Specification Document

**Parallelizable with:** None — this is the foundation everything else references.

**Files:**

- Create: `Projects/Reporting/Exec-Report-Data-Spec.md`

**Step 1: Write the fiscal calendar and targets section**

Include the complete FY27 fiscal calendar (Q1-Q4 date boundaries), quarterly bookings targets ($1.1M/$1.1M/$1.2M/$1.2M), IPM targets (250 annual, 24/Q team split), and pipeline target ($25M annual).

```markdown
## Fiscal Calendar

FY27: Feb 1, 2026 – Jan 31, 2027
| Quarter | Start | End | Bookings Target | IPM Target |
|---------|-------|-----|----------------|------------|
| Q1 | 2026-02-01 | 2026-04-30 | $1,100,000 | 24 (Pete 8, Team 16) |
| Q2 | 2026-05-01 | 2026-07-31 | $1,100,000 | 24 (Pete 8, Team 16) |
| Q3 | 2026-08-01 | 2026-10-31 | $1,200,000 | 24 (Pete 8, Team 16) |
| Q4 | 2026-11-01 | 2027-01-31 | $1,200,000 | 24 (Pete 8, Team 16) |
| FY27 | 2026-02-01 | 2027-01-31 | $4,600,000 | 250 |

Pipeline Created Target: $25,000,000 annual
```

**Step 2: Write the HubSpot field mapping section**

Copy field mappings from the Daily Report prompt (pipeline ID, stage IDs, owner IDs) and add the forecast properties discovered during design:

```markdown
## HubSpot Field Mapping

### Pipeline

- `72018330` = New/Expansion (only pipeline tracked)

### Deal Stages

| Stage ID  | Name                    | Order |
| --------- | ----------------------- | ----- |
| 152446547 | IPM                     | 0     |
| 152455272 | Qualification (Stage 1) | 1     |
| 138620983 | Consensus (Stage 2)     | 2     |
| 138620984 | Proposal (Stage 3)      | 3     |
| 138620985 | Procurement (Stage 4)   | 4     |
| 138620988 | Closed Won              | 5     |
| 138669962 | Closed Lost             | 6     |

### Owner IDs

| ID         | Name            | Team    |
| ---------- | --------------- | ------- |
| 693091902  | Don Vanderslice | NB      |
| 349190077  | Lee Fine        | NB      |
| 81700088   | Tim Long        | NB      |
| 87170480   | Pete Davies     | NB      |
| 702586472  | Eli Grant       | Other   |
| 723668113  | David Brown     | Other   |
| 723668771  | Andrew Bolton   | Other   |
| 627390764  | Ben Smith       | Partner |
| 88616151   | Brian Calahan   | Ops     |
| 889074486  | Tommy Shaker    | Other   |
| 758553440  | Ryan Ruxton     | Other   |
| 2110079045 | Carolyn Scott   | Other   |

### Key Properties

| Property                     | Label                      | Type        | Notes                                 |
| ---------------------------- | -------------------------- | ----------- | ------------------------------------- |
| platform_amt                 | Platform Amount            | number      | ALWAYS use this, NEVER amount         |
| manager_forecast             | Manager Forecast           | enumeration | Commit / Best Case / Pipeline / Omit  |
| manager_forecast_amount      | Manager Forecast Amount    | number      | Auto-computed: category × deal amount |
| hs_manual_forecast_category  | Forecast category          | enumeration | IC/seller forecast                    |
| manager*forecast\_\_stage*   | Manager Forecast (Stage)   | enumeration | Stage-level forecast                  |
| ipm_held                     | IPM Held                   | date        | Date IPM was held                     |
| hs_v2_date_entered_152455272 | Date Entered Qualification | datetime    | Timestamp field                       |
| closedate                    | Close Date                 | date        | Date-only field                       |
| dealtype                     | Deal Type                  | enumeration | "New License" = New Biz, else Upsell  |
| closed_lost_reason           | Closed Lost Reason         | enumeration | For Section 4                         |
| hs_tag_ids                   | Deal Tags                  | string      | Semicolon-delimited tag IDs           |
```

**Step 3: Write the query catalog**

Define every HubSpot API query the script will make. Each query gets a unique ID (Q01, Q02, ...) that both the script and prompts reference. For each query, specify:

- Query ID and name
- HubSpot API endpoint
- Filters (exact property names, operators, values)
- Properties to return
- Pagination requirement (yes/no based on expected result count)
- Grouping/aggregation to perform on results

Example format:

```markdown
### Q01: Closed-Won Deals (Current Quarter)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ "72018330"
  - dealstage EQ "138620988"
  - closedate GTE "{quarter_start}" AND closedate LTE "{quarter_end}"
- **Properties:** dealname, dealtype, dealstage, platform_amt, closedate, hubspot_owner_id, manager_forecast, manager_forecast_amount, hs_manual_forecast_category
- **Pagination:** No (expect <20 per quarter)
- **Aggregations:**
  - SUM(platform_amt) → `bookings.closed_won_total`
  - SUM(platform_amt) GROUP BY hubspot_owner_id → `bookings.by_seller`
  - SUM(platform_amt) GROUP BY dealtype → `bookings.by_type`
  - COUNT → `bookings.closed_won_count`
```

Write queries for all sections:

**Monthly queries (Sections 1-3):**

- Q01: Closed-Won deals (current Q) — Bookings total + detail
- Q02: Closed-Won deals (same Q last FY) — YoY comparison
- Q03: Open deals with manager forecast (current Q close dates) — Forecast rollup
- Q04: IPMs held (current Q) — Activity IPMs
- Q05: Deals entering Qualification (current Q) — Pipeline created
- Q06: Sales emails (NB team, current Q) — Activity emails
- Q07: External meetings (NB team, current Q) — Activity meetings
- Q08: Open deals at Proposal+ (current Q close dates) — Late-stage pipeline
- Q09: Open deals at Proposal+ (next Q close dates) — Next Q line-of-sight
- Q10: Open deals at Qualification+ (next Q close dates) — Next Q early pipeline
- Q11: Event Attendance records (current Q) — Event activity count

**Quarterly-only queries (Sections 4-6):**

- Q12: Closed-Lost deals (current Q, Qualification+ only) — Market feedback
- Q13: All open deals at Qualification+ — Seller performance open pipe
- Q14: Sales emails by seller (last month of Q) — Seller activity
- Q15: External meetings by seller (last month of Q) — Seller activity
- Q16: Deals with hygiene tags by seller — Seller hygiene flags
- Q17: PTM spreadsheet read — Initiatives (file read, not API)

**Step 4: Write the computation rules section**

```markdown
## Computation Rules

### Dollar Handling

- Source field: `platform_amt` (NEVER `amount`)
- Null/empty → treat as 0
- Round to nearest dollar (no cents) for all computations
- Display: $1,234,567 in tables, $1.10M in KPI cards
- KPI card rounding: divide by 1,000,000, round to 2 decimal places, append "M"

### Percentage Handling

- 1 decimal place (e.g., 45.2%)
- % to goal: (actual / target) × 100

### Deal Type Classification

- dealtype = "New License" → "New Biz"
- All other values (Cross-sell, Upsell, Consulting, Winback, Partnership) → "Upsell/Cross-sell"
- ACE vs K1: determined by deal name convention (contains "ACE" or "K1"), NOT dealtype

### Closed-Lost Scoping

- EXCLUDE deals lost while at IPM stage (dealstage = 152446547 at time of loss)
- Practical filter: Closed Lost AND hs_v2_date_entered_152455272 IS NOT NULL
  (if they entered Qualification, they were past IPM)

### Manager Forecast Categories

- Expected values: Commit, Best Case, Pipeline, Omit
- If empty/null: exclude from forecast rollup, flag in data quality section
- Fallback: if manager_forecast empty, use hs_manual_forecast_category

### Win Rate

- Numerator: Closed Won in quarter (Qualification+ only)
- Denominator: Closed Won + Closed Lost in quarter (Qualification+ only, i.e. exclude IPM-stage losses)
- By seller: use hubspot_owner_id for grouping

### Coverage Ratio

- Late-stage pipeline $ (Proposal + Procurement, close date in Q) / Quarterly bookings target
- Display as X.Xx (e.g., 2.8x)
```

**Step 5: Write the timezone rules section**

```markdown
## Timezone Rules

- All output timestamps: Eastern Time (ET / America/New_York)
- Python: use `zoneinfo.ZoneInfo("America/New_York")` for all conversions
- HubSpot returns ISO 8601 timestamps — parse with timezone, convert to ET
- Date-only fields (closedate): treat as start-of-day in ET
- Timestamp fields (hs*v2_date_entered*\*, ipm_held, engagement timestamps): convert to ET
- Quarter boundaries in API queries: use date strings "YYYY-MM-DD" for date fields,
  full ISO 8601 "YYYY-MM-DDTHH:MM:SS.000Z" for timestamp fields
  (start of day in ET converted to UTC for the API call)
- Report header: "Generated {weekday}, {month} {day}, {year} at {HH:MM} {AM/PM} ET"
```

**Step 6: Write the JSON output schema**

Define the exact JSON structure `compute_report.py` outputs. This is the contract between the script and the Claude prompts. Every key path the prompts reference must be documented here.

````markdown
## Output JSON Schema

```json
{
  "meta": {
    "mode": "monthly|quarterly",
    "quarter": "Q2",
    "fiscal_year": "FY27",
    "quarter_start": "2026-05-01",
    "quarter_end": "2026-07-31",
    "generated_at": "2026-06-03T14:30:00-04:00",
    "generated_at_display": "Tuesday, June 3, 2026 at 2:30 PM ET"
  },
  "targets": {
    "bookings_quarterly": 1100000,
    "bookings_annual": 4600000,
    "ipms_quarterly": 24,
    "ipms_annual": 250,
    "pipeline_annual": 25000000
  },
  "data_quality": {
    "forecast_coverage_pct": 85.0,
    "forecast_missing_deals": [...],
    "null_platform_amt_deals": [...],
    "past_due_open_deals": [...]
  },
  "bookings": {
    "closed_won_total": 1102500,
    "closed_won_count": 4,
    "quarterly_goal": 1100000,
    "pct_to_goal": 100.2,
    "yoy_prior": 132500,
    "yoy_pct_change": 732.1,
    "by_seller": {"Don Vanderslice": 307500, ...},
    "by_type": {"New Biz": 602500, "Upsell": 500000},
    "deals": [
      {"name": "...", "ae": "...", "type": "K1", "close_date": "...", "arr": 295000}
    ],
    "forecast": {
      "commit": {"count": 3, "total": 800000, "deals": [...]},
      "best_case": {"count": 5, "total": 500000, "deals": [...]},
      "pipeline": {"count": 8, "total": 1200000, "deals": [...]},
      "total": 2500000
    },
    "ic_forecast": {
      "commit": {"count": ..., "total": ...}, ...
    }
  },
  "activity": {
    "ipms": {
      "total": 28,
      "goal": 24,
      "by_seller": {"Pete Davies": 9, "Don Vanderslice": 12, ...},
      "deals": [...]
    },
    "pipeline_created": {
      "total": 4985450,
      "count": 27,
      "by_seller": {...},
      "by_type": {"ACE": 3210000, "K1": 1775450},
      "deals": [...]
    },
    "emails": {
      "total": 850,
      "by_seller": {"Don Vanderslice": 415, ...}
    },
    "meetings": {
      "total": 45,
      "by_seller": {...}
    },
    "events": {
      "count": 12
    }
  },
  "pipeline": {
    "manager_forecast": {
      "commit": {"count": ..., "total": ..., "deals": [...]},
      "best_case": {"count": ..., "total": ..., "deals": [...]},
      "pipeline_cat": {"count": ..., "total": ..., "deals": [...]},
      "total": ...
    },
    "ic_forecast": {...},
    "late_stage_current_q": {
      "total": 3084450,
      "count": 10,
      "deals": [...]
    },
    "coverage_ratio": 2.8,
    "next_q": {
      "late_stage_total": 960000,
      "late_stage_count": 4,
      "early_total": 2500000,
      "deals": [...]
    }
  },
  "market_feedback": {
    "closed_lost": {
      "total": 1875000,
      "count": 23,
      "deals": [...],
      "by_reason": {
        "Not a priority": {"count": 7, "total": 575000},
        ...
      }
    },
    "ace_k1_mix": {
      "created": {"ACE": {"count": 13, "total": 3210000}, "K1": {...}},
      "won": {...},
      "lost": {...},
      "open": {...}
    }
  },
  "seller_performance": {
    "Pete Davies": {
      "bookings": 0,
      "bookings_count": 0,
      "pipeline_created": 1050000,
      "pipeline_count": 3,
      "ipms": 9,
      "win_rate": 0.0,
      "emails_last_month": 178,
      "meetings_last_month": 21,
      "open_pipeline": 1500000,
      "hygiene_flags": 2
    },
    ...
  },
  "initiatives": {
    "ptm_file_date": "2026-05-22",
    "pete_ptms": [
      {"priority": "Q2 Revenue", "tactics": "...", "metrics": "...", "status": "At Risk", "latest_update": "..."}
    ]
  }
}
```
````

````

**Step 7: Write the data quality section**

Document the checks the script performs and how they appear in the JSON:

```markdown
## Data Quality Checks

The script performs these checks and includes results in `data_quality`:

1. **Manager forecast coverage:** Count deals at Proposal+ (stages 138620984, 138620985)
   with close dates in current Q where manager_forecast is null/empty.
   - If coverage < 70%: set `data_quality.forecast_warning = true`
   - Always list missing deals in `data_quality.forecast_missing_deals`

2. **Null platform_amt:** Count deals at Qualification+ with null/empty platform_amt.
   - List in `data_quality.null_platform_amt_deals`

3. **Past-due open deals:** Count open deals where closedate < today.
   - List in `data_quality.past_due_open_deals`
````

**Step 8: Commit**

```bash
git add Projects/Reporting/Exec-Report-Data-Spec.md
git commit -m "Add exec reporting data specification — shared contract for queries, computations, and rules"
```

---

## Task 2: compute_report.py — Framework + HubSpot Client

**Parallelizable with:** None — depends on Task 1 for field mappings.

**Files:**

- Create: `Projects/Reporting/compute_report.py`

**Step 1: Write the CLI argument parser and main entry point**

```python
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
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

def parse_args():
    p = argparse.ArgumentParser(description="Knotch Exec Report Data Engine")
    p.add_argument("--mode", required=True, choices=["monthly", "quarterly"],
                   help="Report mode: monthly (sections 1-3) or quarterly (sections 1-6)")
    p.add_argument("--quarter", required=True, choices=["Q1", "Q2", "Q3", "Q4"],
                   help="Fiscal quarter to report on")
    p.add_argument("--fy", default="FY27",
                   help="Fiscal year (default: FY27)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print API calls without executing")
    p.add_argument("--output", default="/tmp/exec_report_data.json",
                   help="Output JSON path (default: /tmp/exec_report_data.json)")
    return p.parse_args()

def main():
    args = parse_args()
    api_key = os.environ.get("HUBSPOT_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: HUBSPOT_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    config = build_config(args)
    client = HubSpotClient(api_key, dry_run=args.dry_run)

    report = {"meta": build_meta(config), "targets": config["targets"], "data_quality": {}}

    # Sections 1-3 (monthly + quarterly)
    report["bookings"] = compute_bookings(client, config)
    report["activity"] = compute_activity(client, config)
    report["pipeline"] = compute_pipeline(client, config)
    report["data_quality"] = compute_data_quality(client, config)

    # Sections 4-6 (quarterly only)
    if args.mode == "quarterly":
        report["market_feedback"] = compute_market_feedback(client, config)
        report["seller_performance"] = compute_seller_performance(client, config)
        report["initiatives"] = compute_initiatives(config)

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Report written to {args.output}")

if __name__ == "__main__":
    main()
```

**Step 2: Write the configuration builder**

This encodes all the constants from the Data Spec — fiscal calendar, targets, field mappings, owner IDs. Read from `Exec-Report-Data-Spec.md` at design time; hardcode in python at runtime for determinism.

```python
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
LATE_STAGES = ["138620984", "138620985"]  # Proposal + Procurement
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

def build_config(args):
    fy = args.fy
    q = args.quarter
    q_start, q_end = FISCAL_QUARTERS[fy][q]

    # Determine next quarter
    q_num = int(q[1])
    if q_num < 4:
        next_q = f"Q{q_num + 1}"
        next_q_fy = fy
    else:
        next_q = "Q1"
        next_q_fy = f"FY{int(fy[2:]) + 1}"
    next_q_start, next_q_end = FISCAL_QUARTERS.get(next_q_fy, {}).get(next_q, (None, None))

    # Prior year same quarter for YoY
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
        "ptm_path": os.path.join(os.path.dirname(__file__),
                                  "Brian - Copy of FY27 Leadership PTMs.xlsx"),
    }
```

**Note:** The PTM Excel file must exist at `Projects/Reporting/Brian - Copy of FY27 Leadership PTMs.xlsx` for the Initiatives section (Section 6) to work. This file is already present in the repo (confirmed during design). If it moves or is renamed, update the `ptm_path` in `build_config()`.

**Step 3: Write the HubSpot API client class**

Must handle: Bearer auth, POST search requests, pagination (loop until `hasMore=false`), rate limiting (sleep if 429), timezone parsing, dry-run mode.

```python
import requests
import time

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

    def search_engagements(self, object_type, filters, properties, limit=200):
        return self._search(object_type, filters, properties, limit=limit)

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
```

**Step 4: Write helper functions — dollar parsing, timezone conversion, owner mapping**

```python
def parse_dollars(value):
    """Parse platform_amt to int. Null/empty → 0. Round to nearest dollar."""
    if not value:
        return 0
    try:
        return round(float(value))
    except (ValueError, TypeError):
        return 0

def format_dollars_m(value):
    """Format dollar amount as $X.XXM for KPI cards."""
    return f"${value / 1_000_000:.2f}M"

def format_dollars(value):
    """Format dollar amount as $1,234,567 for tables."""
    return f"${value:,.0f}"

def to_et(iso_string):
    """Parse ISO timestamp and convert to ET. Returns datetime in ET."""
    if not iso_string:
        return None
    dt = datetime.fromisoformat(iso_string)
    return dt.astimezone(ET)

def owner_name(owner_id):
    """Map HubSpot owner ID to display name."""
    return OWNERS.get(str(owner_id), f"Unknown ({owner_id})")

def classify_deal_type(dealtype):
    """New License → New Biz, everything else → Upsell."""
    if dealtype == "New License":
        return "New Biz"
    return "Upsell"

def build_meta(config):
    """Build the report metadata header."""
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
```

**Step 5: Verify the framework runs**

```bash
cd /Users/briancalahan/Knotch
python3 Projects/Reporting/compute_report.py --mode monthly --quarter Q2 --dry-run
```

Expected: Prints `[DRY-RUN] POST ...` for each query (none yet — stub functions return empty dicts). No errors.

**Step 6: Commit**

```bash
git add Projects/Reporting/compute_report.py
git commit -m "Add compute_report.py framework — CLI, HubSpot client, config, helpers"
```

---

## Task 3: compute_report.py — Monthly Queries (Sections 1-3)

**Parallelizable with:** None — depends on Task 2 framework.

**Files:**

- Modify: `Projects/Reporting/compute_report.py`

**Step 1: Implement `compute_bookings()`**

```python
def compute_bookings(client, config):
    # Q01: Closed-Won deals (current quarter)
    won_deals = client.search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": "138620988"},
            {"propertyName": "closedate", "operator": "GTE", "value": config["quarter_start"]},
            {"propertyName": "closedate", "operator": "LTE", "value": config["quarter_end"]},
        ],
        properties=["dealname", "dealtype", "platform_amt", "closedate",
                     "hubspot_owner_id", "manager_forecast", "manager_forecast_amount",
                     "hs_manual_forecast_category"],
    )

    # Q02: YoY comparison (same quarter last FY)
    yoy_total = 0
    if config["prior_q_start"]:
        prior_deals = client.search_deals(
            filters=[
                {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
                {"propertyName": "dealstage", "operator": "EQ", "value": "138620988"},
                {"propertyName": "closedate", "operator": "GTE", "value": config["prior_q_start"]},
                {"propertyName": "closedate", "operator": "LTE", "value": config["prior_q_end"]},
            ],
            properties=["platform_amt"],
        )
        yoy_total = sum(parse_dollars(d["properties"].get("platform_amt")) for d in prior_deals)

    # Q03: Open deals with manager forecast (current Q close dates)
    forecast_deals = client.search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "IN", "value": ";".join(OPEN_STAGES)},
            {"propertyName": "closedate", "operator": "GTE", "value": config["quarter_start"]},
            {"propertyName": "closedate", "operator": "LTE", "value": config["quarter_end"]},
        ],
        properties=["dealname", "dealtype", "platform_amt", "closedate",
                     "hubspot_owner_id", "manager_forecast", "manager_forecast_amount",
                     "hs_manual_forecast_category", "dealstage"],
    )

    # Compute aggregations
    closed_won_total = sum(parse_dollars(d["properties"].get("platform_amt")) for d in won_deals)
    goal = config["targets"].get("bookings", 0)
    pct_to_goal = round(closed_won_total / goal * 100, 1) if goal else 0

    by_seller = {}
    by_type = {}
    deal_list = []
    for d in won_deals:
        p = d["properties"]
        amt = parse_dollars(p.get("platform_amt"))
        seller = owner_name(p.get("hubspot_owner_id"))
        dtype = classify_deal_type(p.get("dealtype", ""))
        by_seller[seller] = by_seller.get(seller, 0) + amt
        by_type[dtype] = by_type.get(dtype, 0) + amt
        deal_list.append({
            "id": d["id"],
            "name": p.get("dealname", ""),
            "ae": seller,
            "type": dtype,
            "close_date": p.get("closedate", ""),
            "arr": amt,
        })

    # Manager forecast rollup
    forecast = {"commit": {"count": 0, "total": 0, "deals": []},
                "best_case": {"count": 0, "total": 0, "deals": []},
                "pipeline_cat": {"count": 0, "total": 0, "deals": []},
                "omit": {"count": 0, "total": 0},
                "missing": {"count": 0, "total": 0, "deals": []}}
    for d in forecast_deals:
        p = d["properties"]
        cat = (p.get("manager_forecast") or "").lower().strip()
        mfa = p.get("manager_forecast_amount")
        amt = parse_dollars(mfa if mfa is not None else p.get("platform_amt"))
        deal_info = {"name": p.get("dealname", ""), "ae": owner_name(p.get("hubspot_owner_id")),
                     "arr": parse_dollars(p.get("platform_amt")), "stage": STAGES.get(p.get("dealstage", ""), ""),
                     "close_date": p.get("closedate", ""), "forecast_cat": p.get("manager_forecast", "")}
        if cat == "commit":
            forecast["commit"]["count"] += 1
            forecast["commit"]["total"] += amt
            forecast["commit"]["deals"].append(deal_info)
        elif cat in ("best case", "best_case"):
            forecast["best_case"]["count"] += 1
            forecast["best_case"]["total"] += amt
            forecast["best_case"]["deals"].append(deal_info)
        elif cat == "pipeline":
            forecast["pipeline_cat"]["count"] += 1
            forecast["pipeline_cat"]["total"] += amt
            forecast["pipeline_cat"]["deals"].append(deal_info)
        elif cat == "omit":
            forecast["omit"]["count"] += 1
            forecast["omit"]["total"] += amt
        else:
            forecast["missing"]["count"] += 1
            forecast["missing"]["total"] += parse_dollars(p.get("platform_amt"))
            forecast["missing"]["deals"].append(deal_info)
    forecast["total"] = forecast["commit"]["total"] + forecast["best_case"]["total"] + forecast["pipeline_cat"]["total"]

    yoy_pct = round((closed_won_total - yoy_total) / yoy_total * 100, 1) if yoy_total else None

    return {
        "closed_won_total": closed_won_total,
        "closed_won_count": len(won_deals),
        "quarterly_goal": goal,
        "pct_to_goal": pct_to_goal,
        "yoy_prior": yoy_total,
        "yoy_pct_change": yoy_pct,
        "by_seller": by_seller,
        "by_type": by_type,
        "deals": sorted(deal_list, key=lambda d: d["arr"], reverse=True),
        "forecast": forecast,
    }
```

**Step 2: Implement `compute_activity()`**

Queries: Q04 (IPMs), Q05 (pipeline created), Q06 (sales emails), Q07 (external meetings), Q11 (events).

For deals (IPMs, pipeline created), use `client.search_deals()` as in Step 1.

For engagements, HubSpot v3 CRM API uses these object types:

- **Emails:** `POST /crm/v3/objects/emails/search` — object type string is `"emails"`
- **Meetings:** `POST /crm/v3/objects/meetings/search` — object type string is `"meetings"`

Engagement query skeleton (emails example):

```python
email_results = client.search_engagements(
    "emails",
    filters=[
        {"propertyName": "hs_timestamp", "operator": "GTE", "value": q_start_ms},
        {"propertyName": "hs_timestamp", "operator": "LTE", "value": q_end_ms},
        {"propertyName": "hubspot_owner_id", "operator": "IN",
         "values": NB_TEAM},
    ],
    properties=["hs_timestamp", "hubspot_owner_id"],
)
```

**Important:** `hs_timestamp` for engagements expects **millisecond epoch timestamps**, not ISO strings. Convert quarter boundaries to epoch ms:

```python
from datetime import datetime, timezone
q_start_dt = datetime.strptime(config["quarter_start"], "%Y-%m-%d").replace(tzinfo=ET)
q_start_ms = str(int(q_start_dt.astimezone(timezone.utc).timestamp() * 1000))
```

For **Event Attendance** (custom object `2-62279031`), use the custom object search endpoint:

```python
event_results = client.search_engagements(
    "2-62279031",
    filters=[
        {"propertyName": "event_date", "operator": "GTE", "value": config["quarter_start"]},
        {"propertyName": "event_date", "operator": "LTE", "value": config["quarter_end"]},
    ],
    properties=["event_name", "event_date", "event_status", "event_type"],
)
```

Group all results by seller, compute totals. Return structure matching the JSON schema `activity` key from the Data Spec.

**Step 3: Implement `compute_pipeline()`**

Queries: Q03 (reuse forecast data from bookings or re-query), Q08 (late-stage current Q), Q09 (late-stage next Q), Q10 (early pipeline next Q).

Key computations:

- Manager forecast rollup by category (Commit/Best Case/Pipeline)
- IC forecast rollup by category for comparison
- Late-stage pipeline total and deal list
- Coverage ratio: late-stage $ / quarterly target
- Next Q line-of-sight (Proposal+ deals with close dates in next quarter)

Return structure matching the JSON schema `pipeline` key.

**Step 4: Implement `compute_data_quality()`**

Query open Proposal+ deals, check for:

1. Empty `manager_forecast` → list in `forecast_missing_deals`
2. Null `platform_amt` at Qual+ → list in `null_platform_amt_deals`
3. `closedate` < today and still open → list in `past_due_open_deals`
4. Compute `forecast_coverage_pct` as % of late-stage deals with non-empty manager_forecast

**Step 5: Run the script with live data and spot-check**

```bash
cd /Users/briancalahan/Knotch
python3 Projects/Reporting/compute_report.py --mode monthly --quarter Q2
cat /tmp/exec_report_data.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('Bookings:', d['bookings']['closed_won_total']); print('Pipeline created:', d['activity']['pipeline_created']['total']); print('Late-stage:', d['pipeline']['late_stage_current_q']['total'])"
```

Verify these numbers manually against HubSpot dashboard views 13149414 and 12758563.

**Step 6: Commit**

```bash
git add Projects/Reporting/compute_report.py
git commit -m "Add monthly report queries (bookings, activity, pipeline, data quality)"
```

---

## Task 4: compute_report.py — Quarterly Queries (Sections 4-6)

**Parallelizable with:** None — depends on Task 3 (same file, builds on monthly queries).

**Files:**

- Modify: `Projects/Reporting/compute_report.py`

**Step 1: Implement `compute_market_feedback()`**

Query Q12: Closed-Lost deals in the quarter at Qualification+ (exclude IPM-stage losses).

Filter logic for excluding IPM losses: `dealstage EQ "138669962"` (Closed Lost) AND `closedate` in quarter AND `hs_v2_date_entered_152455272 IS NOT NULL` (means it reached Qualification, so it wasn't an IPM-only loss).

```python
lost_deals = client.search_deals(
    filters=[
        {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
        {"propertyName": "dealstage", "operator": "EQ", "value": "138669962"},
        {"propertyName": "closedate", "operator": "GTE", "value": config["quarter_start"]},
        {"propertyName": "closedate", "operator": "LTE", "value": config["quarter_end"]},
        {"propertyName": "hs_v2_date_entered_152455272", "operator": "HAS_PROPERTY"},
    ],
    properties=["dealname", "dealtype", "platform_amt", "closedate",
                 "hubspot_owner_id", "closed_lost_reason"],
)
```

**ACE/K1 classification** — determined by deal name convention, not dealtype:

```python
def classify_ace_k1(dealname):
    """Classify deal as ACE or K1 based on naming convention."""
    name_upper = (dealname or "").upper()
    if "ACE" in name_upper:
        return "ACE"
    return "K1"
```

Compute:

- Total closed-lost count and $
- Group by `closed_lost_reason` → count + sum per reason
- ACE/K1 mix: use `classify_ace_k1(dealname)` to group across won, lost, and open Qual+ deals
- Deal-level detail list sorted by $ descending

Also pull Closed-Won deals (reuse from bookings) to compute win themes.

**Step 2: Implement `compute_seller_performance()`**

For each seller in NB_TEAM (Don, Lee, Tim, Pete), compute:

- Bookings: closed-won $ and count (from bookings data, filtered by owner)
- Pipeline created: $ and count entering Qualification (from activity data, filtered by owner)
- IPMs: count (from activity data, filtered by owner)
- Win rate: won / (won + lost) at Qual+ (need Closed Lost by owner too)
- Sales emails in last month of quarter
- External meetings in last month of quarter
- Open pipeline at Qual+ $ (current snapshot)
- Hygiene flags: count of deals with non-empty hs_tag_ids

For emails and meetings in last month of quarter: compute the last month's date range.
Example for Q2 (May-Jul): last month = July 1-31.

```python
def last_month_of_quarter(q_start, q_end):
    end_date = date.fromisoformat(q_end)
    start_of_last_month = end_date.replace(day=1)
    return str(start_of_last_month), q_end
```

Query engagements for that date range, filtered by each seller's owner ID.

**Step 3: Implement `compute_initiatives()`**

Read the PTM spreadsheet using openpyxl:

```python
def compute_initiatives(config):
    ptm_path = config["ptm_path"]
    if not os.path.exists(ptm_path):
        return {"ptm_file_date": None, "pete_ptms": [], "error": f"PTM file not found: {ptm_path}"}

    import openpyxl
    wb = openpyxl.load_workbook(ptm_path, data_only=True)

    # Use the most recent month's sheet (first sheet)
    ws = wb[wb.sheetnames[0]]
    file_mod = datetime.fromtimestamp(os.path.getmtime(ptm_path), tz=ET)

    # Find Pete's rows
    pete_rows = []
    in_pete = False
    header_row = None
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=False):
        vals = [c.value for c in row]
        if vals[0] and str(vals[0]).strip() == "Pete":
            in_pete = True
            continue
        elif vals[0] and str(vals[0]).strip() and in_pete:
            break  # Hit next person
        if in_pete:
            pete_rows.append({
                "priority": str(vals[1] or "").strip(),
                "tactics": str(vals[2] or "").strip(),
                "metrics": str(vals[3] or "").strip(),
                "due_date": str(vals[4] or "").strip(),
                "status": str(vals[5] or "").strip(),
                "latest_update": str(vals[6] or "").strip(),  # Most recent week column
            })

    return {
        "ptm_file_date": file_mod.strftime("%Y-%m-%d"),
        "ptm_sheet": wb.sheetnames[0],
        "pete_ptms": [r for r in pete_rows if r["priority"]],
    }
```

**Step 4: Run the full quarterly report and spot-check**

```bash
cd /Users/briancalahan/Knotch
python3 Projects/Reporting/compute_report.py --mode quarterly --quarter Q1
cat /tmp/exec_report_data.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('=== Q1 Quarterly Spot Check ===')
print(f'Bookings: \${d[\"bookings\"][\"closed_won_total\"]:,}')
print(f'  Expected: \$1,102,500 (from Q1 PDF)')
print(f'Closed-Lost: \${d[\"market_feedback\"][\"closed_lost\"][\"total\"]:,}')
print(f'  Expected: \$1,875,000 (from Q1 PDF)')
print(f'Sellers: {list(d[\"seller_performance\"].keys())}')
print(f'PTMs: {len(d[\"initiatives\"][\"pete_ptms\"])} rows')
"
```

The Q1 bookings total MUST be $1,102,500 to match the Q1 PDF. If it doesn't, debug the query filters (date range, pipeline, stage).

**Step 5: Commit**

```bash
git add Projects/Reporting/compute_report.py
git commit -m "Add quarterly report queries (market feedback, seller performance, initiatives)"
```

---

## Task 5: Monthly Exec Report Prompt

**Parallelizable with:** Task 6 (different file).

**Files:**

- Create: `Projects/Reporting/Monthly-Exec-Report-Prompt.md`

**Step 1: Write the prompt header and execution instructions**

```markdown
You are generating a monthly executive sales report for Pete Davies (Head of New Business Sales, Knotch).

## Step 1: Run the data script

Run the compute script to pull fresh data from HubSpot:

\`\`\`bash
python3 Projects/Reporting/compute_report.py --mode monthly --quarter {QUARTER}
\`\`\`

Replace {QUARTER} with the current fiscal quarter (Q1=Feb-Apr, Q2=May-Jul, Q3=Aug-Oct, Q4=Nov-Jan).

The script writes all report data to `/tmp/exec_report_data.json`. Read this file — every dollar figure, count, and percentage in your report MUST come from this JSON. Do NOT compute any numbers yourself.

## Step 2: Read the JSON output

\`\`\`bash
cat /tmp/exec_report_data.json
\`\`\`
```

**Step 2: Write the exec summary formatting template**

Instruct Claude to produce a "3 Things Leadership Should Know" section using data from the JSON, plus 5 KPI cards. Specify the exact JSON keys to pull each number from.

Example:

```markdown
## Step 3: Format the report

### Page 1: Exec Summary

**Header:**
{meta.quarter} {meta.fiscal_year} Monthly Report — New Business
Pete Davies, Head of New Business Sales
{meta.generated_at_display}

**"3 Things Leadership Should Know"**

Draft 3 concise bullet points based on the data. Each should be:

- Data-driven (cite specific dollar amounts, deal names, percentages)
- Forward-looking (what it means for the rest of the quarter)
- Actionable (what needs to happen next)

**KPI Cards:**
| Card | Value | Source Key |
|------|-------|-----------|
| QTD Closed-Won | ${bookings.closed_won_total} formatted as $X.XXM | bookings.closed_won_total |
| % to Q Goal | {bookings.pct_to_goal}% | bookings.pct_to_goal |
| Manager Forecast | ${forecast commit + best_case total} as $X.XXM | bookings.forecast.commit.total + bookings.forecast.best_case.total |
| Late-Stage Pipe | ${pipeline.late_stage_current_q.total} as $X.XXM | pipeline.late_stage_current_q.total |
| Next Q Sight | ${pipeline.next_q.late_stage_total} as $X.XXM | pipeline.next_q.late_stage_total |
```

**Step 3: Write Section 1 (Bookings) formatting template**

Specify exact table formats using JSON key paths. Include the deal-level closed-won table, manager forecast summary, and quarterly revenue tracker.

**Step 4: Write Section 2 (Activity) formatting template**

IPM table, pipeline created table, activity by seller table. All from JSON keys.

**Step 5: Write Section 3 (Pipeline) formatting template**

Forecast summary (IC vs Manager side-by-side), late-stage deals table, next Q deals table, coverage ratio.

Include Pete's forecast framework definitions:

- Commit = 90% confidence ("surprised if it doesn't sign")
- Best Case = 50/50 ("happy if it signs")
- Pipeline = Low probability ("surprised if it does sign")

**Step 6: Write the data quality section**

```markdown
### Data Quality Notes

If data_quality.forecast_coverage_pct < 100:
"⚠️ Manager forecast is {X}% populated for late-stage deals. The following deals are missing a forecast category:"
[List from data_quality.forecast_missing_deals]

If data_quality.null_platform_amt_deals is not empty:
"⚠️ {N} deals at Qualification+ have no Platform Amount set:"
[List]

If data_quality.past_due_open_deals is not empty:
"⚠️ {N} deals have close dates in the past but are still open:"
[List]
```

**Step 7: Commit**

```bash
git add Projects/Reporting/Monthly-Exec-Report-Prompt.md
git commit -m "Add monthly exec report Claude prompt — 3-section format with exec summary"
```

---

## Task 6: Quarterly Exec Report Prompt

**Parallelizable with:** Task 5 (different file).

**Files:**

- Create: `Projects/Reporting/Quarterly-Exec-Report-Prompt.md`

**Step 1: Write the prompt header — same as monthly but with `--mode quarterly`**

Same Step 1/Step 2 as the monthly prompt, but:

```bash
python3 Projects/Reporting/compute_report.py --mode quarterly --quarter {QUARTER}
```

**Step 2: Copy Sections 1-3 formatting from the monthly prompt**

Identical to the monthly prompt's sections. Copy verbatim — both prompts are standalone.

**Step 3: Write Section 4 (Market Feedback) formatting template**

Include:

- Closed-Lost detail table (from `market_feedback.closed_lost.deals`)
- Loss reason rollup table (from `market_feedback.closed_lost.by_reason`)
- For each loss reason, instruct Claude to write a 1-2 sentence "Read" interpretation:
  ```
  For each reason in market_feedback.closed_lost.by_reason, write a brief interpretation:
  - "Not a priority": Buyer doesn't see urgency. ICP/timing miss or weak POV.
  - "No response": Outbound never landed. Check channel and message.
  - "No budget": Came in unqualified or budget pulled. Mostly early-stage.
  - "Timing": Coming back later — re-engagement candidates.
  - "Loss of Champion": Multi-thread depth gap. Single point of failure.
  - "Other": Vague — flag for cleanup. Push to a real reason.
  For any reason not in this list, write a brief data-driven interpretation.
  ```
- ACE/K1 mix tracking table (from `market_feedback.ace_k1_mix`)
- "Most actionable insight" callout box — Claude drafts based on the data patterns

**Step 4: Write Section 5 (Seller Performance) formatting template**

For each seller in `seller_performance`:

```
**[Seller Name]**  [Headline Tag]

R&R:     [Draft based on the data — deal count, pipeline shape, activity pattern]
Goals:   Bookings: ${bookings} ({count} deals). Pipeline created: ${pipeline_created}
         ({pipeline_count} deals). IPMs: {ipms} of {goal}.
Metrics: Emails: {emails_last_month}. Meetings: {meetings_last_month}.
         Open pipe: ${open_pipeline}. Hygiene flags: {hygiene_flags}.
         Win rate: {win_rate}%.
```

Instruct Claude on headline tags:

```
For each seller, write a 3-6 word headline tag that captures their quarter in a nutshell.
Base it on the data patterns — high bookings but low pipeline = "Closing machine; needs pipe."
Zero bookings but strong activity = "Pipeline builder; conversion gap."
Be honest but constructive. These go in Pete's report to leadership.
```

Commission achievement table: build from seller_performance data.

**Step 5: Write Section 6 (Initiatives) formatting template**

Pull from `initiatives.pete_ptms` and format as three sub-tables (Talent, Enablement, GTM).

Instruct Claude to map each PTM row to the appropriate sub-section based on the `priority` field:

- Priorities containing "Revenue", "Hiring", "Perf Mgmt", "Partner" → 6a. Talent
- Priorities containing "Deck", "Collateral", "Objection", "Onboarding" → 6b. Enablement
- Priorities containing "IPM", "ACE", "Pipeline", "Event", "GTM" → 6c. GTM

Note: `"Based on PTM spreadsheet as of {initiatives.ptm_file_date}. Pete should review and edit this section before sharing."`

**Step 6: Write the full report output format specification**

Specify the exact order, headers, and formatting for the complete 6-section report. Include:

- Report header with title, date, source note
- Table of contents (jump links like the Q1 PDF)
- Section numbering matching the Q1 report style
- Footer: "Confidential · Internal Use Only · Pete Davies · Generated {date}"

**Step 7: Commit**

```bash
git add Projects/Reporting/Quarterly-Exec-Report-Prompt.md
git commit -m "Add quarterly exec report Claude prompt — 6-section format with narrative templates"
```

---

## Task 7: QA — Live Data Verification

**Parallelizable with:** None — depends on all prior tasks.

**Files:**

- No new files. This task runs the system end-to-end and verifies numbers.

**Step 1: Run the monthly script for Q2 and verify against HubSpot**

```bash
cd /Users/briancalahan/Knotch
python3 Projects/Reporting/compute_report.py --mode monthly --quarter Q2
```

Open HubSpot dashboard view 13149414 and compare:

- Closed-Won count and total
- Pipeline created count and total
- Open deal count at each stage

If numbers don't match, debug the query filters. Common issues:

- Pipeline filter missing (getting deals from wrong pipeline)
- Date range off by one day
- Using `amount` instead of `platform_amt`

**Step 2: Run the quarterly script for Q1 and verify against the Q1 PDF**

```bash
python3 Projects/Reporting/compute_report.py --mode quarterly --quarter Q1
```

Cross-reference against the Q1 Quarterly Revenue Report PDF:

- Bookings total: expect $1,102,500
- Closed-Lost total: expect $1,875,000 (23 deals, excluding IPM losses)
- IPMs: expect ~28
- Pipeline created: expect $4,985,450 (27 deals)

If bookings total doesn't match $1,102,500, this is a BLOCKER. Debug before proceeding.

**Step 3: Run the monthly prompt in Claude and verify output**

**Shell access required:** These prompts instruct Claude to run `python3` via the Bash tool. This only works in **Claude Code (CLI)** or **Claude desktop** with shell access enabled. It does **NOT** work in claude.ai web (no bash tool). Pete should use Claude desktop or have Brian run it from the CLI.

Open Claude (CLI or desktop). Paste the Monthly-Exec-Report-Prompt.md content. Replace {QUARTER} with Q2.

Verify:

- [ ] Script runs without errors
- [ ] All dollar figures in the report match the JSON file exactly
- [ ] All timestamps display in ET
- [ ] Exec summary has 3 data-driven bullets
- [ ] KPI cards show correct values
- [ ] Tables are formatted and readable
- [ ] Data quality warnings appear (if applicable)

**Step 4: Run the quarterly prompt in Claude for Q1 and verify output**

Same as Step 3, but with the Quarterly prompt and Q1. Verify the additional sections:

- [ ] Section 4 (Market Feedback) has loss reason rollup with "Read" interpretations
- [ ] Section 5 (Seller Performance) has all 4 NB sellers with R&R/Goals/Metrics
- [ ] Section 6 (Initiatives) pulls from the PTM spreadsheet correctly
- [ ] Narrative sections are structured (not generic filler)

**Step 5: Run the dry-run and capture query log for future parity testing**

```bash
python3 Projects/Reporting/compute_report.py --mode quarterly --quarter Q2 --dry-run > /tmp/exec_report_queries.log
```

This log becomes the reference for the future Google Sheet Apps Script — every API call must match.

**Step 6: Document any discrepancies or adjustments needed**

If numbers don't match or prompts need tweaking, fix the issues in the relevant files and re-run. Update the Data Spec if any query definitions changed during QA.

---

## Task 8: Documentation Updates

**Parallelizable with:** None — depends on QA passing.

**Files:**

- Modify: `Enablement/10-Reporting-and-Dashboards.md`
- Modify: `CLAUDE.md`

**Step 1: Update Enablement/10-Reporting-and-Dashboards.md**

Add a new section after "Weekly Insights Report":

```markdown
## Monthly Executive Report

**Frequency:** Monthly (run on 1st business day of each month)

**Audience:** Sales leadership (Pete → Jason/Anda)

**Purpose:** QTD bookings, activity, and pipeline status with exec summary and manager forecast.

**How to run:**

1. Open Claude (CLI or desktop)
2. Paste the contents of `Projects/Reporting/Monthly-Exec-Report-Prompt.md`
3. Replace {QUARTER} with the current fiscal quarter
4. Review output, edit narrative sections, share with leadership

**Sections:** Exec Summary (KPI cards + 3 takeaways), Bookings (QTD), Activity (QTD), Pipeline (Current Q + Next Q)

**Data source:** `Projects/Reporting/compute_report.py` pulls live HubSpot data. All dollar computation is deterministic (python3, not Claude math).

---

## Quarterly Executive Report

**Frequency:** Quarterly (run in first week after quarter close)

**Audience:** Executive team (Jason, Anda) via Pete

**Purpose:** Full quarter review with market feedback, seller assessments, and initiative tracking.

**How to run:** Same as monthly, but use `Projects/Reporting/Quarterly-Exec-Report-Prompt.md` and the script runs with `--mode quarterly`.

**Sections:** Everything in the monthly report PLUS Market Feedback (close-loss analysis), Seller Performance (3-lens assessment), Initiatives (PTM status).
```

**Step 2: Update CLAUDE.md**

Add under "Directory Structure" or a new "Active Project" section:

```markdown
## Active Project: Executive Reporting System

**Status:** Live
**Files:** Projects/Reporting/

- Exec-Report-Data-Spec.md — Shared data contract
- compute_report.py — HubSpot API → deterministic JSON
- Monthly-Exec-Report-Prompt.md — Claude prompt for monthly report
- Quarterly-Exec-Report-Prompt.md — Claude prompt for quarterly report
  **Cadence:** Monthly (sections 1-3), Quarterly (sections 1-6)
  **QA:** Run compute_report.py independently to verify numbers. --dry-run shows API calls without executing.
```

**Step 3: Commit**

```bash
git add Enablement/10-Reporting-and-Dashboards.md CLAUDE.md
git commit -m "Update docs with monthly/quarterly exec reporting cadence and system reference"
```

---

## Recovery State

<!-- Auto-updated during execution. Read this first if resuming after compaction. -->

**Last completed:** {not started}
**Next:** Wave 1, Task 1
**Branch:** main
**Test baseline:** N/A — greenfield, no test suite
**Key decisions:** {none yet}
**Blockers:** {none}
