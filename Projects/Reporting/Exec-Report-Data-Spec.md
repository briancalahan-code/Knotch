# Exec Report Data Specification

> **Shared contract** between `compute_report.py`, Claude prompts, and future Google Sheet Apps Script.
> Every query, filter, computation rule, and output key documented here is authoritative.
> If the script and this spec disagree, fix the script.

---

## Fiscal Calendar

FY27: Feb 1, 2026 -- Jan 31, 2027

| Quarter | Start      | End        | Bookings Target | IPM Target           |
| ------- | ---------- | ---------- | --------------- | -------------------- |
| Q1      | 2026-02-01 | 2026-04-30 | $1,100,000      | 24 (Pete 8, Team 16) |
| Q2      | 2026-05-01 | 2026-07-31 | $1,100,000      | 24 (Pete 8, Team 16) |
| Q3      | 2026-08-01 | 2026-10-31 | $1,200,000      | 24 (Pete 8, Team 16) |
| Q4      | 2026-11-01 | 2027-01-31 | $1,200,000      | 24 (Pete 8, Team 16) |
| FY27    | 2026-02-01 | 2027-01-31 | $4,600,000      | 250                  |

Pipeline Created Target: $25,000,000 annual ($6,250,000 per quarter)

FY26 (for YoY comparison):

| Quarter | Start      | End        |
| ------- | ---------- | ---------- |
| Q1      | 2025-02-01 | 2025-04-30 |
| Q2      | 2025-05-01 | 2025-07-31 |
| Q3      | 2025-08-01 | 2025-10-31 |
| Q4      | 2025-11-01 | 2026-01-31 |

---

## HubSpot Field Mapping

### Pipeline

- `72018330` = New/Expansion (only pipeline tracked in exec reporting)

### Deal Stages

| Stage ID  | Name                    | Order | Category   |
| --------- | ----------------------- | ----- | ---------- |
| 152446547 | IPM                     | 0     | Early      |
| 152455272 | Qualification (Stage 1) | 1     | Qual+      |
| 138620983 | Consensus (Stage 2)     | 2     | Qual+      |
| 138620984 | Proposal (Stage 3)      | 3     | Late-stage |
| 138620985 | Procurement (Stage 4)   | 4     | Late-stage |
| 138620988 | Closed Won              | 5     | Closed     |
| 138669962 | Closed Lost             | 6     | Closed     |

**Stage groupings used in queries:**

- **Open stages:** IPM + Qualification + Consensus + Proposal + Procurement
- **Qual+ (Qualification and above):** Qualification + Consensus + Proposal + Procurement
- **Early stages (Qualification + Consensus):** Qualification + Consensus (excludes late-stage)
- **Late-stage (Proposal+):** Proposal + Procurement

### Owner IDs

| ID         | Name            | Team    | NB Team? |
| ---------- | --------------- | ------- | -------- |
| 693091902  | Don Vanderslice | NB      | Yes      |
| 81700088   | Tim Long        | NB      | Yes      |
| 87170480   | Pete Davies     | NB      | Yes      |
| 702586472  | Eli Grant       | Other   | No       |
| 723668113  | David Brown     | Other   | No       |
| 723668771  | Andrew Bolton   | Other   | No       |
| 627390764  | Ben Smith       | Partner | No       |
| 88616151   | Brian Calahan   | Ops     | No       |
| 889074486  | Tommy Shaker    | Other   | No       |
| 758553440  | Ryan Ruxton     | Other   | No       |
| 2110079045 | Carolyn Scott   | Other   | No       |

### Key Properties

| Property                     | Label                      | Type        | Notes                                                    |
| ---------------------------- | -------------------------- | ----------- | -------------------------------------------------------- |
| amount                       | Amount (ACV)               | number      | PRIMARY dollar field -- auto-calculated from line items  |
| platform_amt                 | Platform Amt               | number      | Secondary -- platform-only, excludes services/consulting |
| manager*forecast\_\_stage*   | Manager Forecast (Stage)   | enumeration | Commit / Best Case / Pipeline / Omit                     |
| manager_forecast_amount      | Manager Forecast Amount    | number      | Auto-computed: category weight x deal amount             |
| hs_manual_forecast_category  | Forecast category          | enumeration | IC/seller forecast (fallback if manager is empty)        |
| ipm_held                     | IPM Held                   | date        | Date IPM was held                                        |
| hs_v2_date_entered_152455272 | Date Entered Qualification | datetime    | Timestamp -- used for pipeline created and CL scope      |
| closedate                    | Close Date                 | date        | Date-only field                                          |
| dealtype                     | Deal Type                  | enumeration | "New License" = New Biz, else Upsell                     |
| closed_lost_reason           | Closed Lost Reason         | enumeration | For Section 4 market feedback                            |
| hs_tag_ids                   | Deal Tags                  | string      | Semicolon-delimited tag IDs (hygiene flags)              |
| dealname                     | Deal Name                  | string      | Used for ACE/K1 classification                           |

---

## Query Catalog

Every HubSpot API query the script makes. Query IDs (Q01-Q17) are referenced by both the script and prompts.

### Monthly Queries (Sections 1-3)

#### Q01: Closed-Won Deals (Current Quarter)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage EQ `138620988`
  - closedate GTE `{quarter_start}`
  - closedate LTE `{quarter_end}`
- **Properties:** dealname, dealtype, amount, platform*amt, closedate, hubspot_owner_id, manager_forecast\_\_stage*, manager_forecast_amount, hs_manual_forecast_category
- **Pagination:** No (expect <20 per quarter)
- **Aggregations:**
  - SUM(amount) -> `bookings.closed_won_total`
  - SUM(amount) GROUP BY hubspot_owner_id -> `bookings.by_seller`
  - SUM(amount) GROUP BY dealtype -> `bookings.by_type`
  - COUNT -> `bookings.closed_won_count`

#### Q02: Closed-Won Deals (Same Quarter Last FY -- YoY)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage EQ `138620988`
  - closedate GTE `{prior_q_start}`
  - closedate LTE `{prior_q_end}`
- **Properties:** amount
- **Pagination:** No
- **Aggregations:**
  - SUM(amount) -> `bookings.yoy_prior`

#### Q03: Open Deals with Forecast (Current Q Close Dates)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage IN `152446547;152455272;138620983;138620984;138620985` (all open stages)
  - closedate GTE `{quarter_start}`
  - closedate LTE `{quarter_end}`
- **Properties:** dealname, dealtype, amount, platform*amt, closedate, hubspot_owner_id, manager_forecast\_\_stage*, manager_forecast_amount, hs_manual_forecast_category, dealstage
- **Pagination:** Yes (could be 50+)
- **Aggregations:**
  - GROUP BY manager_forecast -> SUM(manager_forecast_amount) per category -> `bookings.forecast`
  - GROUP BY hs_manual_forecast_category -> SUM(amount) per category -> `bookings.ic_forecast`

#### Q04: IPMs Held (Current Quarter)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - ipm_held GTE `{quarter_start}`
  - ipm_held LTE `{quarter_end}`
- **Properties:** dealname, dealtype, amount, platform_amt, ipm_held, hubspot_owner_id, dealstage
- **Pagination:** No (expect <40)
- **Aggregations:**
  - COUNT -> `activity.ipms.total`
  - COUNT GROUP BY hubspot_owner_id -> `activity.ipms.by_seller`

#### Q05: Pipeline Created (Deals Entering Qualification in Current Quarter)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - hs_v2_date_entered_152455272 GTE `{quarter_start_ts}` (epoch ms)
  - hs_v2_date_entered_152455272 LTE `{quarter_end_ts}` (epoch ms)
- **Properties:** dealname, dealtype, amount, platform_amt, hs_v2_date_entered_152455272, hubspot_owner_id, dealstage
- **Pagination:** Yes (could be 30+)
- **Note:** `hs_v2_date_entered_*` is a timestamp field -- use epoch milliseconds, not date strings
- **Aggregations:**
  - SUM(amount) -> `activity.pipeline_created.total`
  - COUNT -> `activity.pipeline_created.count`
  - SUM GROUP BY hubspot_owner_id -> `activity.pipeline_created.by_seller`
  - SUM GROUP BY ACE/K1 classification -> `activity.pipeline_created.by_type`

#### Q06: Sales Emails (NB Team, Current Quarter)

- **Endpoint:** POST /crm/v3/objects/emails/search
- **Filters:**
  - hs_timestamp GTE `{quarter_start_ms}` (epoch ms)
  - hs_timestamp LTE `{quarter_end_ms}` (epoch ms)
  - hubspot_owner_id IN `693091902;81700088;87170480` (NB team)
- **Properties:** hs_timestamp, hubspot_owner_id
- **Pagination:** Yes (could be hundreds)
- **Aggregations:**
  - COUNT -> `activity.emails.total`
  - COUNT GROUP BY hubspot_owner_id -> `activity.emails.by_seller`

#### Q07: External Meetings (NB Team, Current Quarter)

- **Endpoint:** POST /crm/v3/objects/meetings/search
- **Filters:**
  - hs_timestamp GTE `{quarter_start_ms}` (epoch ms)
  - hs_timestamp LTE `{quarter_end_ms}` (epoch ms)
  - hubspot_owner_id IN `693091902;81700088;87170480` (NB team)
- **Properties:** hs_timestamp, hubspot_owner_id
- **Pagination:** Yes (could be hundreds)
- **Aggregations:**
  - COUNT -> `activity.meetings.total`
  - COUNT GROUP BY hubspot_owner_id -> `activity.meetings.by_seller`

#### Q08: Late-Stage Deals -- Current Q Close Dates (Proposal+)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage IN `138620984;138620985` (Proposal + Procurement)
  - closedate GTE `{quarter_start}`
  - closedate LTE `{quarter_end}`
- **Properties:** dealname, dealtype, amount, platform*amt, closedate, hubspot_owner_id, manager_forecast\_\_stage*, manager_forecast_amount, hs_manual_forecast_category, dealstage
- **Pagination:** No (expect <15)
- **Aggregations:**
  - SUM(amount) -> `pipeline.late_stage_current_q.total`
  - COUNT -> `pipeline.late_stage_current_q.count`

#### Q09: Late-Stage Deals -- Next Q Close Dates (Proposal+)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage IN `138620984;138620985`
  - closedate GTE `{next_q_start}`
  - closedate LTE `{next_q_end}`
- **Properties:** dealname, dealtype, amount, closedate, hubspot*owner_id, manager_forecast\_\_stage*, dealstage
- **Pagination:** No
- **Aggregations:**
  - SUM(amount) -> `pipeline.next_q.late_stage_total`
  - COUNT -> `pipeline.next_q.late_stage_count`

#### Q10: Early Pipeline -- Next Q Close Dates (Qualification + Consensus Only)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage IN `152455272;138620983` (Qualification + Consensus only -- excludes late-stage to avoid double-counting with Q09)
  - closedate GTE `{next_q_start}`
  - closedate LTE `{next_q_end}`
- **Properties:** dealname, dealtype, amount, closedate, hubspot_owner_id, dealstage
- **Pagination:** Yes
- **Aggregations:**
  - SUM(amount) -> `pipeline.next_q.early_total`
  - Combined with Q09: `pipeline.next_q.qual_plus_total` = late_stage_total + early_total

#### Q10b: Qual+ Pipeline -- Current Q Close Dates

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage IN `152455272;138620983;138620984;138620985` (Qual+)
  - closedate GTE `{quarter_start}`
  - closedate LTE `{quarter_end}`
- **Properties:** amount, hubspot_owner_id
- **Pagination:** Yes
- **Aggregations:**
  - SUM(amount) -> `pipeline.qual_plus_current_q.total`
  - COUNT -> `pipeline.qual_plus_current_q.count`
  - SUM GROUP BY hubspot_owner_id -> `pipeline.qual_plus_current_q.by_seller`

#### Q10c: Next-Q Manager Forecast (Open Deals with Next Q Close Dates)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage IN `152446547;152455272;138620983;138620984;138620985` (all open stages)
  - closedate GTE `{next_q_start}`
  - closedate LTE `{next_q_end}`
- **Properties:** amount, hubspot_owner_id, manager_forecast\_\_stage\_, manager_forecast_amount
- **Pagination:** Yes
- **Aggregations:**
  - SUM(manager_forecast_amount) WHERE category IN (Commit, Best Case) -> `pipeline.next_q.forecast_cbc_total`
  - SUM GROUP BY hubspot_owner_id (Commit + Best Case only) -> `pipeline.next_q.forecast_cbc_by_seller`

#### Q11: Event Attendance (Current Quarter)

- **Endpoint:** POST /crm/v3/objects/2-62279031/search
- **Filters:**
  - event_date GTE `{quarter_start}`
  - event_date LTE `{quarter_end}`
- **Properties:** event_name, event_date, event_status, event_type
- **Pagination:** Yes (could be 100+)
- **Aggregations:**
  - COUNT -> `activity.events.count`

### Quarterly-Only Queries (Sections 4-6)

#### Q12: Closed-Lost Deals (Current Q, Qualification+ Only)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage EQ `138669962` (Closed Lost)
  - closedate GTE `{quarter_start}`
  - closedate LTE `{quarter_end}`
  - hs_v2_date_entered_152455272 HAS_PROPERTY (reached Qualification -- excludes IPM-only losses)
- **Properties:** dealname, dealtype, amount, platform_amt, closedate, hubspot_owner_id, closed_lost_reason
- **Pagination:** No (expect <30)
- **Aggregations:**
  - SUM(amount) -> `market_feedback.closed_lost.total`
  - COUNT -> `market_feedback.closed_lost.count`
  - GROUP BY closed_lost_reason -> count + sum per reason -> `market_feedback.closed_lost.by_reason`

#### Q13: All Open Deals at Qualification+ (Snapshot)

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - dealstage IN `152455272;138620983;138620984;138620985` (Qual+)
- **Properties:** dealname, dealtype, amount, closedate, hubspot_owner_id, dealstage, hs_tag_ids
- **Pagination:** Yes (~170 records)
- **Aggregations:**
  - SUM(amount) GROUP BY hubspot_owner_id -> `seller_performance.{seller}.open_pipeline`
  - COUNT deals with non-empty hs_tag_ids GROUP BY owner -> `seller_performance.{seller}.hygiene_flags`

#### Q14: Sales Emails by Seller (Last Month of Quarter)

- **Endpoint:** POST /crm/v3/objects/emails/search
- **Filters:**
  - hs_timestamp GTE `{last_month_start_ms}` (epoch ms)
  - hs_timestamp LTE `{last_month_end_ms}` (epoch ms)
  - hubspot_owner_id IN `693091902;81700088;87170480`
- **Properties:** hs_timestamp, hubspot_owner_id
- **Pagination:** Yes
- **Aggregations:**
  - COUNT GROUP BY hubspot_owner_id -> `seller_performance.{seller}.emails_last_month`

#### Q15: External Meetings by Seller (Last Month of Quarter)

- **Endpoint:** POST /crm/v3/objects/meetings/search
- **Filters:**
  - hs_timestamp GTE `{last_month_start_ms}` (epoch ms)
  - hs_timestamp LTE `{last_month_end_ms}` (epoch ms)
  - hubspot_owner_id IN `693091902;81700088;87170480`
- **Properties:** hs_timestamp, hubspot_owner_id
- **Pagination:** Yes
- **Aggregations:**
  - COUNT GROUP BY hubspot_owner_id -> `seller_performance.{seller}.meetings_last_month`

#### Q16: Deals with Hygiene Tags by Seller

- **Note:** Derived from Q13 results, not a separate API call
- Deals where hs_tag_ids is non-empty, grouped by owner
- -> `seller_performance.{seller}.hygiene_flags`

#### Q17: PTM Spreadsheet Read (Initiatives)

- **Source:** `Projects/Reporting/Brian - Copy of FY27 Leadership PTMs.xlsx`
- **Method:** openpyxl file read (not HubSpot API)
- **Extract:** Pete's rows from the most recent month's sheet
- **Fields:** Priority, Tactics, Metrics, Due Date, Status, Latest Update
- -> `initiatives.pete_ptms`

### Prior Quarter Activity Queries (QoQ Trending)

These queries mirror Q04-Q07 but target the immediately preceding fiscal quarter (e.g., Q1 when reporting Q2). Used for QoQ trending in Activity by Seller table.

#### Q18: Prior Q Sales Emails (NB Team)

- **Endpoint:** POST /crm/v3/objects/emails/search
- **Filters:**
  - hs_timestamp GTE `{prev_q_start_ms}` (epoch ms)
  - hs_timestamp LTE `{prev_q_end_ms}` (epoch ms)
  - hubspot_owner_id IN `693091902;81700088;87170480` (NB team)
- **Properties:** hs_timestamp, hubspot_owner_id
- **Pagination:** Yes
- **Aggregations:**
  - COUNT -> `activity.prior_q.emails.total`
  - COUNT GROUP BY hubspot_owner_id -> `activity.prior_q.emails.by_seller`

#### Q19: Prior Q External Meetings (NB Team)

- **Endpoint:** POST /crm/v3/objects/meetings/search
- **Filters:**
  - hs_timestamp GTE `{prev_q_start_ms}` (epoch ms)
  - hs_timestamp LTE `{prev_q_end_ms}` (epoch ms)
  - hubspot_owner_id IN `693091902;81700088;87170480` (NB team)
- **Properties:** hs_timestamp, hubspot_owner_id
- **Pagination:** Yes
- **Aggregations:**
  - COUNT -> `activity.prior_q.meetings.total`
  - COUNT GROUP BY hubspot_owner_id -> `activity.prior_q.meetings.by_seller`

#### Q20: Prior Q IPMs Held

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - ipm_held GTE `{prev_q_start_ms}` (epoch ms)
  - ipm_held LTE `{prev_q_end_ms}` (epoch ms)
- **Properties:** hubspot_owner_id
- **Pagination:** No
- **Aggregations:**
  - COUNT -> `activity.prior_q.ipms.total`
  - COUNT GROUP BY hubspot_owner_id -> `activity.prior_q.ipms.by_seller`

#### Q21: Prior Q Pipeline Created

- **Endpoint:** POST /crm/v3/objects/deals/search
- **Filters:**
  - pipeline EQ `72018330`
  - hs_v2_date_entered_152455272 GTE `{prev_q_start_ms}` (epoch ms)
  - hs_v2_date_entered_152455272 LTE `{prev_q_end_ms}` (epoch ms)
- **Properties:** amount, hubspot_owner_id
- **Pagination:** Yes
- **Aggregations:**
  - SUM(amount) -> `activity.prior_q.pipeline_created.total`
  - COUNT -> `activity.prior_q.pipeline_created.count`
  - SUM GROUP BY hubspot_owner_id -> `activity.prior_q.pipeline_created.by_seller`

---

## Computation Rules

### Dollar Handling

- Primary source field: `amount` (ACV -- auto-calculated from line items)
- Secondary: `platform_amt` for platform vs. services breakdown
- Null/empty -> treat as 0
- Round to nearest dollar (no cents) for all computations
- Display in tables: `$1,234,567`
- Display in KPI cards: `$X.XXM` (divide by 1,000,000, round to 2 decimal places)

### Percentage Handling

- 1 decimal place (e.g., 45.2%)
- % to goal: (actual / target) x 100

### Deal Type Classification

- `dealtype = "New License"` -> "New Biz"
- All other values (Cross-sell, Upsell, Consulting, Winback, Partnership) -> "Upsell/Cross-sell" (note: the script returns this exact string)

### Booking Type Classification (for `bookings.by_type`)

- Partnership = owned by Ben Smith (627390764) OR dealtype "Partnership" (takes precedence)
- ACE = deal name contains "ACE" (case-insensitive) AND not Partnership
- Non-ACE = everything else

### ACE vs K1 Classification

- Determined by deal name convention, NOT dealtype
- If deal name contains "ACE" (case-insensitive) -> "ACE"
- Otherwise -> "K1"

### Closed-Lost Scoping

- EXCLUDE deals lost while at IPM stage (never qualified)
- Practical filter: Closed Lost AND `hs_v2_date_entered_152455272` IS NOT NULL (if they entered Qualification, they were past IPM)

### Manager Forecast Categories

- Expected values: Commit, Best Case, Pipeline, Omit
- If empty/null: exclude from forecast rollup, flag in data quality section
- Dollar source: use `manager_forecast_amount` when available; fall back to `amount`
- Fallback: if `manager_forecast__stage_` empty, use `hs_manual_forecast_category` for IC forecast comparison

### Win Rate

- Numerator: Closed Won count in quarter (Qualification+ only -- filter by `hs_v2_date_entered_152455272 HAS_PROPERTY`)
- Denominator: Closed Won + Closed Lost count in quarter (both Qualification+ only -- excludes IPM-stage wins and losses)
- By seller: use hubspot_owner_id for grouping
- Display: 1 decimal place (e.g., 33.3%)

### Coverage Ratio

- Late-stage pipeline $ (Proposal + Procurement, close date in current Q) / Quarterly bookings target
- Display as X.Xx (e.g., 2.8x)

### Last Month of Quarter

- For seller activity metrics (emails, meetings)
- Q1 (Feb-Apr): last month = April 1-30
- Q2 (May-Jul): last month = July 1-31
- Q3 (Aug-Oct): last month = October 1-31
- Q4 (Nov-Jan): last month = January 1-31

---

## Timezone Rules

- All output timestamps: Eastern Time (ET / America/New_York)
- Python: use `zoneinfo.ZoneInfo("America/New_York")` for all conversions
- HubSpot returns ISO 8601 timestamps -- parse with timezone, convert to ET
- Date-only fields (closedate, ipm_held): treat as start-of-day in ET
- Timestamp fields (hs*v2_date_entered*\*, engagement hs_timestamp): convert to ET
- Quarter boundaries in API queries:
  - Date fields: use date strings `YYYY-MM-DD`
  - Timestamp fields (hs*timestamp, hs_v2_date_entered*\*): use epoch milliseconds (start-of-day ET converted to UTC)
- Report header: `Generated {weekday}, {month} {day}, {year} at {HH:MM} {AM/PM} ET`

---

## Output JSON Schema

The exact JSON structure `compute_report.py` outputs. Every key path referenced by prompts is documented here.

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
    "bookings": 1100000,
    "ipms": 24,
    "pipeline": 6250000
  },
  "data_quality": {
    "forecast_coverage_pct": 85.0,
    "forecast_warning": false,
    "forecast_missing_deals": [
      { "name": "...", "ae": "...", "stage": "...", "acv": 0 }
    ],
    "null_platform_amt_deals": [{ "name": "...", "ae": "...", "stage": "..." }],
    "past_due_open_deals": [
      {
        "name": "...",
        "ae": "...",
        "close_date": "...",
        "stage": "...",
        "acv": 0
      }
    ]
  },
  "bookings": {
    "closed_won_total": 1102500,
    "closed_won_count": 4,
    "quarterly_goal": 1100000,
    "pct_to_goal": 100.2,
    "yoy_prior": 132500,
    "yoy_pct_change": 732.1,
    "by_seller": { "Don Vanderslice": 307500 },
    "by_type": { "ACE": 402500, "Non-ACE": 500000, "Partnership": 200000 },
    "deals": [
      {
        "id": "123",
        "name": "...",
        "ae": "...",
        "type": "New Biz",
        "booking_type": "ACE",
        "ace_k1": "ACE",
        "close_date": "2026-03-15",
        "acv": 295000,
        "platform": 295000,
        "services": 0
      }
    ],
    "forecast": {
      "commit": { "count": 3, "total": 800000, "deals": [] },
      "best_case": { "count": 5, "total": 500000, "deals": [] },
      "pipeline_cat": { "count": 8, "total": 1200000, "deals": [] },
      "omit": { "count": 0, "total": 0 },
      "missing": { "count": 2, "total": 150000, "deals": [] },
      "by_seller": { "Pete Davies": 500000, "Don Vanderslice": 800000 },
      "total": 2500000
    },
    "ic_forecast": {
      "commit": { "count": 2, "total": 600000 },
      "best_case": { "count": 3, "total": 400000 },
      "pipeline_cat": { "count": 5, "total": 900000 },
      "missing": { "count": 1, "total": 100000 },
      "total": 1900000
    }
  },
  "activity": {
    "ipms": {
      "total": 28,
      "goal": 24,
      "by_seller": { "Pete Davies": 9, "Don Vanderslice": 12 },
      "deals": []
    },
    "pipeline_created": {
      "total": 4985450,
      "count": 27,
      "goal": 6250000,
      "pct_to_goal": 79.8,
      "by_seller": {},
      "by_type": { "ACE": 3210000, "K1": 1775450 },
      "deals": []
    },
    "emails": {
      "total": 850,
      "by_seller": { "Don Vanderslice": 415 }
    },
    "meetings": {
      "total": 45,
      "by_seller": {}
    },
    "events": {
      "count": 12
    },
    "prior_q": {
      "quarter": "Q1",
      "emails": { "total": 780, "by_seller": { "Don Vanderslice": 390 } },
      "meetings": { "total": 52, "by_seller": {} },
      "ipms": { "total": 28, "by_seller": { "Pete Davies": 9 } },
      "pipeline_created": { "total": 5200000, "count": 25, "by_seller": {} }
    }
  },
  "pipeline": {
    "late_stage_current_q": {
      "total": 3084450,
      "count": 10,
      "by_seller": { "Don Vanderslice": 1200000, "Pete Davies": 884450 },
      "deals": []
    },
    "qual_plus_current_q": {
      "total": 5500000,
      "count": 18,
      "by_seller": { "Don Vanderslice": 2100000, "Pete Davies": 1500000 }
    },
    "coverage_ratio": 2.8,
    "by_seller": { "Don Vanderslice": 2100000, "Pete Davies": 1500000 },
    "next_q": {
      "late_stage_total": 960000,
      "late_stage_count": 4,
      "early_total": 1540000,
      "qual_plus_total": 2500000,
      "by_seller": { "Tim Long": 500000 },
      "forecast_cbc_total": 800000,
      "forecast_cbc_by_seller": { "Tim Long": 300000 },
      "deals": []
    }
  },
  "market_feedback": {
    "closed_lost": {
      "total": 1875000,
      "count": 23,
      "deals": [],
      "by_reason": {
        "Not a priority": { "count": 7, "total": 575000 }
      }
    },
    "ace_k1_mix": {
      "created": { "ACE": { "count": 13, "total": 3210000 }, "K1": {} },
      "won": {},
      "lost": {},
      "open": {}
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
    }
  },
  "initiatives": {
    "ptm_file_date": "2026-05-22",
    "ptm_sheet": "May",
    "pete_ptms": [
      {
        "priority": "Q2 Revenue",
        "tactics": "...",
        "metrics": "...",
        "due_date": "...",
        "status": "At Risk",
        "latest_update": "..."
      }
    ]
  }
}
```

---

## Data Quality Checks

The script performs these checks and includes results in `data_quality`:

1. **Manager forecast coverage:** Count deals at Proposal+ (stages 138620984, 138620985) with close dates in current Q where `manager_forecast` is null/empty.
   - Compute: `forecast_coverage_pct` = (deals with forecast / total late-stage deals) x 100
   - If coverage < 70%: set `forecast_warning = true`
   - Always list missing deals in `forecast_missing_deals`

2. **Null platform_amt:** Count deals at Qualification+ with null/empty `platform_amt`.
   - List in `null_platform_amt_deals`

3. **Past-due open deals:** Count open deals where `closedate` < today.
   - List in `past_due_open_deals`
