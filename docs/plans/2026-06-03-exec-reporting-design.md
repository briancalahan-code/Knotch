# Exec Reporting System — Design Doc

**Date:** June 3, 2026
**Author:** Brian Calahan (GTM Evolved)
**For:** Pete Davies (Head of New Business Sales, Knotch)
**Status:** Design approved, ready for implementation planning

---

## Problem

Pete needs structured monthly and quarterly executive reports. The current state:

- **Daily:** GTM Daily Update runs via Claude prompt → Slack DM (working)
- **Weekly:** Deal Arena summaries + Deal Hygiene per seller (working)
- **Monthly:** Pete's "Sales Sync" deck exists but is manual, inconsistent
- **Quarterly:** Q1 report was a one-off 17-page PDF (Cowork artifact, May 4). Not repeatable.
- **Revenue vs. Quota reporting:** Listed as "No artifact" in the Q1 report's open asks

Pete wants to reduce the quarterly report from 17 pages/10 sections to a focused 6-section structure, and add a monthly cadence with 3 core sections.

## Constraints

1. **Number determinism:** Reports must produce identical dollar figures every run for the same time period. Claude's LLM math is probabilistic — all computation must happen in python3.
2. **Prompt ↔ Google Sheet parity:** A future Google Sheet + Apps Script version must produce the exact same numbers. Both implementations must follow the same Data Specification.
3. **Timezone:** All dates in Eastern Time (ET). HubSpot returns full ISO timestamps with timezone. No UTC assumptions.
4. **Terminology:** "Bookings" not "revenue" for all sales reporting.
5. **Audience:** Tiered — exec summary for Jason/Anda (page 1), detail sections for Pete's working use.
6. **Narrative:** Hybrid — Claude drafts commentary, Pete reviews and edits before sharing.

## Architecture

```
Exec-Report-Data-Spec.md              ← Shared contract (queries, filters, computation rules)
        |
compute_report.py                     ← Standalone python3 script
  - Calls HubSpot REST API directly     (HUBSPOT_API_KEY env var)
  - Implements every query from spec
  - Computes all aggregations
  - Handles pagination + timezone
  - Outputs report_data.json
        |
        ├── Monthly-Exec-Report-Prompt.md    ← Claude reads JSON, formats 3-section report
        ├── Quarterly-Exec-Report-Prompt.md  ← Claude reads JSON, formats 6-section report
        └── Future: apps-script/             ← Google Sheet, same computation logic, adds charts
```

### Execution Flow

1. Pete or Brian runs the Claude prompt (CLI, desktop, or claude.ai)
2. Claude runs: `python3 Projects/Reporting/compute_report.py --mode monthly --quarter Q2`
3. Script calls HubSpot API, computes everything, writes `/tmp/exec_report_data.json`
4. Claude reads the JSON — all numbers are exact, computed in python3
5. Claude formats the report: tables, exec summary, narrative commentary
6. Pete reviews, edits narrative sections, shares with leadership

### QA Pathway

The script is independently testable:

```bash
# Run without Claude — verify numbers match HubSpot
python3 compute_report.py --mode monthly --quarter Q2

# Dry run — show queries without executing
python3 compute_report.py --mode quarterly --quarter Q2 --dry-run

# Compare with Google Sheet (future)
python3 compute_report.py --mode monthly --quarter Q2 --output parity_test.json
# → Feed same JSON to Apps Script → compare number-by-number
```

## Deliverables

| #   | File                                                 | Purpose                                                                         | Est. Lines |
| --- | ---------------------------------------------------- | ------------------------------------------------------------------------------- | ---------- |
| 1   | `Projects/Reporting/Exec-Report-Data-Spec.md`        | Shared contract: every query, filter, computation, rounding rule, date boundary | ~300       |
| 2   | `Projects/Reporting/compute_report.py`               | Standalone script: HubSpot API → deterministic JSON output                      | ~400       |
| 3   | `Projects/Reporting/Monthly-Exec-Report-Prompt.md`   | Claude prompt: runs script, formats 3-section report + exec summary             | ~200       |
| 4   | `Projects/Reporting/Quarterly-Exec-Report-Prompt.md` | Claude prompt: runs script, formats 6-section report + exec summary             | ~350       |

Future parallel track:
| 5 | `Projects/Reporting/apps-script/` | Google Sheet: same computation, adds charts/graphs/conditional formatting | TBD |

## Report Structure

### Monthly Report (3 sections + exec summary)

Run monthly. Covers QTD data for Bookings, Activity, and Pipeline.

### Quarterly Report (6 sections + exec summary)

Run quarterly. Includes all monthly sections plus Market Feedback, Seller Performance, and Initiatives.

---

### Page 1: Exec Summary (Both Monthly + Quarterly)

**"3 Things Leadership Should Know"** — Claude-drafted callout box. Pete edits before sharing. Modeled after the Q1 report's "Three things the exec team should hear first" section.

**KPI Cards:**

| Card                                  | Computation                                                                               | Source Fields                                        |
| ------------------------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| QTD Closed-Won                        | SUM(platform_amt) WHERE dealstage=138620988 AND closedate in quarter                      | platform_amt, dealstage, closedate                   |
| % to Quarterly Goal                   | Closed-Won $ / quarterly target × 100                                                     | Computed / hardcoded target                          |
| Manager Forecast (Commit + Best Case) | SUM(manager_forecast_amount) WHERE manager_forecast IN (Commit, Best Case) AND close in Q | manager_forecast, manager_forecast_amount, closedate |
| Late-Stage Pipeline                   | SUM(platform_amt) WHERE dealstage IN (Proposal, Procurement) AND closedate in Q           | platform_amt, dealstage, closedate                   |
| Next Q Line-of-Sight                  | SUM(platform_amt) WHERE dealstage IN (Proposal, Procurement) AND closedate in next Q      | platform_amt, dealstage, closedate                   |

---

### Section 1: Bookings (QTD)

**Monthly + Quarterly**

**Purpose:** Track closed-won revenue against quarterly goal with forecast visibility.

**KPIs:**

| Metric                  | Computation                                                                  | Notes                           |
| ----------------------- | ---------------------------------------------------------------------------- | ------------------------------- |
| Closed-Won ARR (QTD)    | SUM(platform_amt) WHERE Closed Won in Q                                      | Always platform_amt, not amount |
| Quarterly Goal          | Hardcoded per Q ($1.1M Q2, $1.2M Q3, $1.2M Q4)                               | From FY27 plan                  |
| % to Goal               | Closed-Won / Goal × 100                                                      |                                 |
| YoY Comparison          | Same query for same Q last FY                                                | FY26 Q2 = May-Jul 2025          |
| Manager Forecast Rollup | Group by manager_forecast category → SUM(manager_forecast_amount)            | Commit / Best Case / Pipeline   |
| IC Forecast Rollup      | Group by hs_manual_forecast_category → SUM(platform_amt)                     | For delta with manager          |
| Bookings by Type        | SUM(platform_amt) GROUP BY dealtype → "New License" = New Biz, else = Upsell |                                 |
| Bookings by Seller      | SUM(platform_amt) GROUP BY hubspot_owner_id                                  | Map IDs to names                |

**Tables:**

1. **Closed-Won Detail:** Deal Name | AE | Type (ACE/K1) | Close Date | Platform ARR
2. **Manager Forecast Summary:** Category | # Deals | $ Total | Key Deals (top 3 by $)
3. **Quarterly Revenue Tracker:** Period | FY26 Actual | FY27 Goal | FY27 Actual/Forecast | % to Goal | YoY Δ | Notes

**Data Quality Check:** Count deals at Proposal+ missing manager_forecast. If >0, list them with: Deal Name | AE | Platform Amt | Stage.

---

### Section 2: Activity (QTD)

**Monthly + Quarterly**

**Purpose:** Track leading indicators (IPMs, pipeline creation, outreach) against goals.

**KPIs:**

| Metric                      | Computation                                                     | Notes                         |
| --------------------------- | --------------------------------------------------------------- | ----------------------------- |
| IPMs Held (QTD)             | COUNT WHERE ipm_held in quarter, pipeline=72018330              | By seller                     |
| IPM Goal                    | 24/quarter team (Pete 8, Team 16)                               | From PTMs                     |
| Pipeline Created ($)        | SUM(platform_amt) WHERE hs_v2_date_entered_152455272 in quarter | Deals entering Qualification  |
| Pipeline by Type            | GROUP BY dealtype on created deals                              | ACE vs K1 split               |
| Pipeline by Seller          | GROUP BY hubspot_owner_id                                       |                               |
| Sales Emails (NB Team)      | COUNT engagements type=EMAIL, owner IN [Don, Lee, Tim, Pete]    | QTD                           |
| External Meetings (NB Team) | COUNT engagements type=MEETING, same owners                     | QTD                           |
| Event Activity              | COUNT Event Attendance records WHERE event_date in quarter      | From custom object 2-62279031 |

**Tables:**

1. **IPM Detail:** Deal Name | AE | Type | Platform Amt | IPM Held Date
2. **Pipeline Created Detail:** Deal Name | AE | Type | Created Date | Platform Amt | Current Stage
3. **Activity by Seller:** Seller | Emails | Meetings | IPMs (Actual/Goal) | Pipe Created $

**IPM Source Note:** IPMs counted from ipm_held deal property. Confidence note if sources disagree (same caveat as Q1 report).

---

### Section 3: Pipeline (Current Q + Next Q)

**Monthly + Quarterly**

**Purpose:** Forecast current quarter attainment and build next-quarter visibility.

**KPIs:**

| Metric                       | Computation                                                                       | Notes                 |
| ---------------------------- | --------------------------------------------------------------------------------- | --------------------- |
| Manager Forecast — Commit    | SUM(manager_forecast_amount) WHERE manager_forecast=Commit, closedate in Q        | 90% confidence        |
| Manager Forecast — Best Case | Same, manager_forecast=Best Case                                                  | 50/50                 |
| Manager Forecast — Pipeline  | Same, manager_forecast=Pipeline                                                   | Low probability       |
| Manager Forecast — Total     | Sum of above three                                                                | Pete's real number    |
| IC Forecast — Total          | SUM(platform_amt) grouped by hs_manual_forecast_category                          | For comparison        |
| Late-Stage $                 | SUM(platform_amt) WHERE dealstage IN (Proposal, Procurement), closedate in Q      |                       |
| Coverage Ratio               | Late-Stage $ / Quarterly Goal                                                     | Shows pipe vs. target |
| Next Q Line-of-Sight         | SUM(platform_amt) WHERE dealstage IN (Qual+), closedate in next Q                 | Early visibility      |
| Next Q Late-Stage            | SUM(platform_amt) WHERE dealstage IN (Proposal, Procurement), closedate in next Q |                       |

**Tables:**

1. **Late-Stage Deals (Current Q):** Deal | AE | Type | Stage | Close Date | Platform ARR | Manager Forecast Category
2. **Late-Stage Deals (Next Q):** Same columns
3. **Forecast Summary:** Shows IC vs Manager forecast side by side with delta

**Forecast Framework (display in report):**

- **Commit** = 90% confident in both amount and close date ("surprised if it doesn't sign")
- **Best Case** = 50/50 probability ("happy if it signs")
- **Pipeline** = Low probability ("surprised if it does sign")

**Pete's commentary placeholder:** Space for Pete to write his narrative overlay on the forecast (e.g., "Forecast shows $1.36M but my actual confidence is $1.1M — here's why...")

---

### Section 4: Market Feedback (Quarterly Only)

**Purpose:** Close-loss analysis, win themes, product mix tracking, competitive signals.

**KPIs:**

| Metric                   | Computation                                       | Notes                    |
| ------------------------ | ------------------------------------------------- | ------------------------ |
| Closed-Lost Count        | COUNT WHERE Closed Lost in Q, Qualification+ only | Exclude IPM-stage losses |
| Closed-Lost $            | SUM(platform_amt) same filter                     |                          |
| Loss by Reason           | GROUP BY closed_lost_reason → COUNT + SUM         |                          |
| Win Count + $            | COUNT + SUM WHERE Closed Won in Q                 |                          |
| ACE vs K1 Mix — Won      | GROUP BY dealtype on Closed Won                   |                          |
| ACE vs K1 Mix — Lost     | GROUP BY dealtype on Closed Lost                  |                          |
| ACE vs K1 Mix — Pipeline | GROUP BY dealtype on open Qual+ deals             | Tracks conversion gap    |

**Tables:**

1. **Closed-Lost Detail:** Deal | AE | Closed Date | ARR | Loss Reason (sorted by $ desc)
2. **Loss Reason Rollup:** Reason | # Deals | $ Lost | "Read" (Claude-drafted narrative per reason)
3. **ACE/K1 Tracking:** Type | Created Q | Won Q | Lost Q | Open | Net (supply vs leakage view from Q1 report)

**Narrative (Claude-drafted, Pete-edits):**

- "Most actionable insight: [data-driven observation]" callout box
- Per-reason "Read" column: 1-2 sentence interpretation (e.g., "Not a priority = buyer doesn't see urgency. ICP/timing miss or weak POV.")
- ACE/K1 mix analysis (tracks the gap identified in Q1: "100% of Q1 wins were K1; ACE pipeline not converting yet")

---

### Section 5: Seller Performance (Quarterly Only)

**Purpose:** Per-seller assessment across three lenses (R&R, Goals, Metrics). Matches Q1 report Section 9 format.

**Sellers assessed:** Pete Davies, Don Vanderslice, Lee Fine, Tim Long (NB team)

**KPIs per seller:**

| Metric                      | Computation                                               |
| --------------------------- | --------------------------------------------------------- |
| Bookings (Closed-Won $)     | SUM(platform_amt) WHERE Closed Won in Q, by owner         |
| Bookings Deal Count         | COUNT same                                                |
| Pipeline Created $          | SUM(platform_amt) entering Qualification in Q, by owner   |
| Pipeline Deal Count         | COUNT same                                                |
| IPMs Held                   | COUNT WHERE ipm_held in Q, by owner                       |
| IPM Goal                    | Pete: 8/Q, Team member: ~5-6/Q                            |
| Win Rate                    | Won / (Won + Lost) at Qualification+ in Q, by owner       |
| Sales Emails (monthly)      | COUNT engagements type=EMAIL in last month of Q, by owner |
| External Meetings (monthly) | COUNT engagements type=MEETING in last month, by owner    |
| Open Pipeline (Qual+) $     | SUM(platform_amt) open deals, by owner                    |
| Hygiene Flags               | COUNT deals with hs_tag_ids populated, by owner           |

**Format per seller (3-lens assessment):**

```
[Seller Name]  [Headline Tag]   ← e.g., "Carrying the team; pipeline machine"

R&R:     [Role posture, deal ownership style, engagement quality]
Goals:   [Bookings, pipeline, IPMs vs. targets — specific numbers]
Metrics: [Activity counts, meeting volume, hygiene status, open pipeline]
```

**Headline tags** — Claude drafts based on data patterns. Examples from Q1:

- Pete: "Leadership lift; personal book light"
- Don: "Carrying the team; pipeline machine"
- Lee: "Strong contact depth; zero conversion"
- Tim: "EY win, but Q2 trial"

**Commission Achievement Table:**

| Component                | Team (rollup) | Tim | Don | Lee | Pete | Ben Smith |
| ------------------------ | ------------- | --- | --- | --- | ---- | --------- |
| Direct New Biz Bookings  | $             | $   | $   | $   | $    | —         |
| Partner New Biz Bookings | $             | —   | —   | —   | —    | $         |
| Pipeline Created — ACE   | deals / $     |     |     |     |      |           |
| Pipeline Created — K1    | deals / $     |     |     |     |      |           |
| IPMs                     | count         |     |     |     |      |           |
| Win Rate                 | %             |     |     |     |      |           |

**Data source note:** Seller assessments use HubSpot activity data (emails, meetings, deal records). Granola meeting quality data is available for Pete's meetings only — Don/Lee/Tim Granola coverage is incomplete. This is noted explicitly in the report.

---

### Section 6: Initiatives (Quarterly Only)

**Purpose:** Status tracking on talent, enablement, and GTM initiatives. Matches Q1 report Sections 8a/8b/8c.

**Source:** PTM spreadsheet (`Projects/Reporting/Brian - Copy of FY27 Leadership PTMs.xlsx`) — Pete's rows extracted via python3 (openpyxl). Claude reads the latest statuses and formats them.

**Sub-sections:**

**6a. Talent**
| Initiative | Q Status | Next Q Goal | Notes |
|-----------|----------|-------------|-------|
| Hiring (AE, AD, VDL) | [from PTMs] | [from PTMs] | |
| Performance management | [from PTMs] | | |
| Partner role development | [from PTMs] | | |

**6b. Enablement**
| Initiative | Q Status | Next Q Goal | Notes |
|-----------|----------|-------------|-------|
| GTM deck for IPMs | [from PTMs] | | |
| Objection handling / proof points | | | |
| New-hire onboarding | | | |

**6c. GTM**
| Initiative | Q Status | Next Q Goal | Notes |
|-----------|----------|-------------|-------|
| ICP model / territory | | | |
| Event motion | | | |
| Deal efficiency tools | | | |
| Stage gating | | | |
| Reporting cadence | | | |

**Automation level:** Script reads the PTM spreadsheet and extracts Pete's rows. Claude formats the table and drafts status notes from the latest weekly column. Pete reviews and edits. Timestamp: "Based on PTM spreadsheet as of [file modification date]."

---

## Data Specification (Key Rules)

Full spec goes in `Exec-Report-Data-Spec.md`. Summary of critical rules:

### Fiscal Calendar

```
FY27: Feb 1, 2026 – Jan 31, 2027
Q1: Feb 1, 2026 – Apr 30, 2026
Q2: May 1, 2026 – Jul 31, 2026
Q3: Aug 1, 2026 – Oct 31, 2026
Q4: Nov 1, 2026 – Jan 31, 2027
```

### Quarterly Targets (FY27)

```
Bookings:  Annual $4.6M  |  Q1 $1.1M  |  Q2 $1.1M  |  Q3 $1.2M  |  Q4 $1.2M
IPMs:      Annual 250    |  ~24/Q team (Pete 8, Team 16)
Pipeline:  Annual $25M
```

### Timezone Rules

- **All timestamps displayed in Eastern Time (ET)**
- HubSpot returns ISO timestamps with timezone info — use the timezone provided
- Python3 script converts all timestamps to ET using `zoneinfo.ZoneInfo("America/New_York")`
- Date-only fields (closedate): treat as midnight ET on that date
- Timestamp fields (hs*v2_date_entered*\*, ipm_held): convert from HubSpot timezone to ET
- Report header includes generation time in ET

### HubSpot Field Mapping

```
Pipeline:        72018330 = New/Expansion (only pipeline tracked)
Stages:          152446547=IPM, 152455272=Qualification, 138620983=Consensus,
                 138620984=Proposal, 138620985=Procurement,
                 138620988=Closed Won, 138669962=Closed Lost

Dollar Field:    platform_amt (NEVER amount)
Manager Forecast: manager_forecast (category), manager_forecast_amount (computed $)
IC Forecast:     hs_manual_forecast_category
Forecast Stage:  manager_forecast__stage_

NB Team Owners:  693091902=Don, 349190077=Lee, 81700088=Tim, 87170480=Pete
Full Team:       + 702586472=Eli, 723668113=David Brown, 723668771=Bolton,
                 627390764=Ben Smith, 88616151=Brian, 889074486=Tommy,
                 758553440=Ryan, 2110079045=Carolyn

Deal Types:      "New License" = New Biz. Everything else = Upsell/Cross-sell.
                 Track ACE vs K1 via deal naming or dealtype sub-categories.
```

### Computation Rules

- Always use `platform_amt`, never `amount`. If null/empty, treat as 0.
- Dollar amounts: rounded to nearest dollar (no cents). Display as $1,234,567 in tables, $1.10M in KPI cards.
- Percentages: 1 decimal place (e.g., 45.2%).
- Closed-Lost analysis **excludes IPM-stage losses** (deals lost while still at IPM stage — they never qualified). Per Q1 convention.
- Manager Forecast categories expected: Commit, Best Case, Pipeline, Omit (verify actual values in HubSpot property options).
- Pagination: mandatory on all HubSpot API queries. If `hasMore=true`, fetch next page with offset. Never assume a single page contains all results.
- Rounding in KPI cards: $X.XXM format (e.g., $1.10M, $3.08M). Round to nearest $10K for M display.

### Data Quality Checks

The script includes data quality validation:

1. Count deals at Proposal+ with empty manager_forecast → include in report as a warning
2. Count deals with null platform_amt at Qualification+ → flag for cleanup
3. Count deals with closedate in the past but still open → flag as past-due
4. If manager_forecast coverage < 70% of late-stage deals, include banner: "⚠️ Manager forecast is [X]% populated. Forecast figures may be incomplete."

---

## Prior Art

| Existing Asset                       | Disposition                                                                                             |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| GTM Daily Report Prompt              | **Reused** — query patterns, field mappings, and HubSpot references copied into Data Spec               |
| Deal Arena Weekly Summary Prompt     | **Referenced** — narrative style guide informs seller performance section                               |
| Q1 Quarterly Revenue Report (PDF)    | **Template** — section structure, table formats, callout box style, headline tags all modeled from this |
| Seller Hygiene Prompt                | **Referenced** — hygiene tag system used in seller performance scoring                                  |
| Enablement/10 Reporting & Dashboards | **Updated** — will add monthly/quarterly cadence entries after build                                    |
| FY27 Leadership PTMs spreadsheet     | **Data source** — Initiatives section reads Pete's PTMs from this file                                  |

## Risks & Validated Dimensions

### Validated (Stress Test PASS)

- **Scale:** ~25 HubSpot queries per quarterly report is well within API limits
- **Existing patterns:** Daily/Weekly prompts prove the HubSpot MCP + Claude workflow works
- **Content model:** Q1 report provides a proven template for all 6 sections
- **Forecast data:** manager_forecast, manager_forecast_amount, and hs_manual_forecast_category all exist in HubSpot

### Mitigated Risks

| Risk                         | Mitigation                                                                  |
| ---------------------------- | --------------------------------------------------------------------------- |
| Claude math is probabilistic | All computation in python3 script — Claude never sums dollars               |
| Prompt ↔ Google Sheet drift  | Shared Data Spec + python3 script logic ports to Apps Script                |
| Fiscal Q date boundaries     | Explicit boundary table in Data Spec + python3 handles all date math in ET  |
| Manager forecast gaps        | Data quality check flags missing forecasts; falls back to IC forecast       |
| Granola is Pete-only         | Seller assessments use HubSpot activity data only; Granola limitation noted |
| PTM spreadsheet is manual    | Timestamped; Pete reviews Initiatives section before sharing                |
| Report timing/staleness      | Snapshot timestamp in report header; run on fixed schedule                  |

### Accepted Risks

- **Narrative quality:** Claude drafts commentary that may be generic. Pete must review/edit before sharing. Structured templates reduce this risk but don't eliminate it.
- **PTM format changes:** If the Excel spreadsheet structure changes (new columns, merged cells), the python3 reader may break. Mitigated by keeping the Excel format stable.
- **Historical data gaps:** YoY comparison requires FY26 data in HubSpot. If FY26 deals were deleted or stages changed retroactively, YoY numbers may be inaccurate. Accept this limitation.

## Google Sheet (Future Parallel Track)

When built, the Google Sheet will:

- Implement the same Data Spec queries via Apps Script + HubSpot REST API
- Add visual charts: bookings waterfall, pipeline by stage (bar), forecast funnel, seller comparison
- Add conditional formatting: red/yellow/green on % to goal, forecast categories
- Tabs: Monthly Summary, Quarterly Summary, Raw Data (audit trail), Config
- Parity test: before launch, run both python3 script and Apps Script on same data snapshot, compare every number query-by-query
