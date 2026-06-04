# Monthly Executive Report — Claude Prompt

You are generating a monthly executive sales report for Pete Davies (Head of New Business Sales, Knotch).

**Important:** This prompt requires shell access (Bash tool). It works in Claude Code (CLI), Claude desktop, or Claude Code IDE extensions. It does NOT work in claude.ai web.

---

## Step 1: Run the data script

Run the compute script to pull fresh data from HubSpot:

```bash
python3 Projects/Reporting/compute_report.py --mode monthly --quarter {QUARTER}
```

Replace `{QUARTER}` with the current fiscal quarter:

- Q1 = Feb-Apr
- Q2 = May-Jul
- Q3 = Aug-Oct
- Q4 = Nov-Jan

The script writes all report data to `/tmp/exec_report_data.json`.

## Step 2: Read the JSON output

```bash
cat /tmp/exec_report_data.json
```

**Critical rule:** Every dollar figure, count, and percentage in your report MUST come directly from this JSON. Do NOT compute any numbers yourself. Do NOT round differently than what the JSON provides. Copy numbers exactly.

## Step 3: Format the report

Use the structure below. Replace all `{json.path}` references with the actual values from the JSON.

---

### Report Header

```
{meta.quarter} {meta.fiscal_year} Monthly Sales Report — New Business
Pete Davies, Head of New Business Sales
{meta.generated_at_display}

Data source: HubSpot CRM (live pull)
```

---

### Page 1: Executive Summary

#### 3 Things Leadership Should Know

Draft 3 concise bullet points based on the data. Each should be:

- **Data-driven** — cite specific dollar amounts, deal names, percentages from the JSON
- **Forward-looking** — what it means for the rest of the quarter
- **Actionable** — what needs to happen next

Example tone: "QTD bookings are at $X.XXM (XX% to goal) with $X.XXM in Commit forecast. The gap to goal requires converting [specific deal names] in the next [N] weeks."

#### KPI Cards

Format as a row of 5 cards:

| KPI                     | Value                                                                                           | Source                              |
| ----------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------- |
| QTD Closed-Won          | Format `bookings.closed_won_total` as $X.XXM                                                    | bookings.closed_won_total           |
| % to Q Goal             | `bookings.pct_to_goal`%                                                                         | bookings.pct_to_goal                |
| Manager Forecast (C+BC) | Sum of `bookings.forecast.commit.total` + `bookings.forecast.best_case.total`, format as $X.XXM | bookings.forecast                   |
| Late-Stage Pipeline     | Format `pipeline.late_stage_current_q.total` as $X.XXM                                          | pipeline.late_stage_current_q.total |
| Next Q Line-of-Sight    | Format `pipeline.next_q.late_stage_total` as $X.XXM                                             | pipeline.next_q.late_stage_total    |

Dollar formatting for KPI cards: divide by 1,000,000, round to 2 decimal places, prefix with $, suffix with M. Example: 1102500 → $1.10M.

---

### Section 1: Bookings (QTD)

#### Closed-Won Summary

- QTD Closed-Won: $`bookings.closed_won_total` ({bookings.closed_won_count} deals)
- Quarterly Goal: $`bookings.quarterly_goal`
- % to Goal: `bookings.pct_to_goal`%
- YoY: Prior year same Q was $`bookings.yoy_prior` ({bookings.yoy_pct_change}% change). If `yoy_pct_change` is null, write "No prior year data available."

#### Closed-Won Detail Table

| Deal | AE  | Type | Close Date | Platform ARR |
| ---- | --- | ---- | ---------- | ------------ |

Populate from `bookings.deals[]`. Format ARR as $XXX,XXX. Sort by ARR descending (already sorted in JSON).

#### Bookings by Type

| Type | Amount | % of Total |
| ---- | ------ | ---------- |

Populate from `bookings.by_type`. Calculate % from total.

#### Manager Forecast Summary

| Category  | # Deals | $ Total                   | Top 3 Deals                                             |
| --------- | ------- | ------------------------- | ------------------------------------------------------- |
| Commit    |         |                           | List top 3 by ARR from `bookings.forecast.commit.deals` |
| Best Case |         |                           | List top 3 from `bookings.forecast.best_case.deals`     |
| Pipeline  |         |                           | List top 3 from `bookings.forecast.pipeline_cat.deals`  |
| **Total** |         | `bookings.forecast.total` |                                                         |

If `bookings.forecast.missing.count` > 0:

> ⚠️ {count} deals totaling ${total} have no manager forecast category set.

**Forecast Framework:**

- **Commit** = 90% confident in amount and close date ("surprised if it doesn't sign")
- **Best Case** = 50/50 probability ("happy if it signs")
- **Pipeline** = Low probability ("surprised if it does sign")

---

### Section 2: Activity (QTD)

#### IPM Summary

- IPMs Held: `activity.ipms.total` of `activity.ipms.goal` goal
- By Seller:

| Seller | IPMs |
| ------ | ---- |

Populate from `activity.ipms.by_seller`.

#### IPM Detail Table

| Deal | AE  | Type | Platform Amt | IPM Held Date |
| ---- | --- | ---- | ------------ | ------------- |

Populate from `activity.ipms.deals[]`.

#### Pipeline Created

- Total: $`activity.pipeline_created.total` (`activity.pipeline_created.count` deals)
- ACE: $`activity.pipeline_created.by_type.ACE` | K1: $`activity.pipeline_created.by_type.K1`

| Seller | Pipeline Created $ | # Deals |
| ------ | ------------------ | ------- |

Populate from `activity.pipeline_created.by_seller` (show $ and derive count from deals).

#### Pipeline Created Detail

| Deal | AE  | Type | Created Date | Platform Amt | Current Stage |
| ---- | --- | ---- | ------------ | ------------ | ------------- |

Populate from `activity.pipeline_created.deals[]`. Sort by ARR descending (already sorted).

#### Activity by Seller

| Seller | Emails | Meetings | IPMs (Actual/Goal) | Pipe Created $ |
| ------ | ------ | -------- | ------------------ | -------------- |

Populate from `activity.emails.by_seller`, `activity.meetings.by_seller`, `activity.ipms.by_seller`, `activity.pipeline_created.by_seller`.

#### Event Activity

Events this quarter: `activity.events.count`

---

### Section 3: Pipeline (Current Q + Next Q)

#### Late-Stage Deals — Current Quarter

Total late-stage (Proposal + Procurement): $`pipeline.late_stage_current_q.total` (`pipeline.late_stage_current_q.count` deals)

Coverage ratio: `pipeline.coverage_ratio`x (late-stage $ / quarterly goal)

| Deal | AE  | Type | Stage | Close Date | Platform ARR | Manager Forecast |
| ---- | --- | ---- | ----- | ---------- | ------------ | ---------------- |

Populate from `pipeline.late_stage_current_q.deals[]`.

#### Forecast Comparison (IC vs Manager)

| Category  | IC Forecast                               | Manager Forecast                       | Delta      |
| --------- | ----------------------------------------- | -------------------------------------- | ---------- |
| Commit    | `bookings.ic_forecast.commit.total`       | `bookings.forecast.commit.total`       | difference |
| Best Case | `bookings.ic_forecast.best_case.total`    | `bookings.forecast.best_case.total`    | difference |
| Pipeline  | `bookings.ic_forecast.pipeline_cat.total` | `bookings.forecast.pipeline_cat.total` | difference |
| **Total** | `bookings.ic_forecast.total`              | `bookings.forecast.total`              | difference |

_Pete's commentary placeholder:_ [Space for Pete to add his narrative overlay on the forecast]

#### Next Quarter Line-of-Sight

- Late-stage (Proposal+): $`pipeline.next_q.late_stage_total` (`pipeline.next_q.late_stage_count` deals)
- Early pipeline (Qual+): $`pipeline.next_q.early_total`

| Deal | AE  | Stage | Close Date | Platform ARR |
| ---- | --- | ----- | ---------- | ------------ |

Populate from `pipeline.next_q.deals[]`.

---

### Data Quality Notes

Check each condition and include if applicable:

**If** `data_quality.forecast_coverage_pct` < 100:

> ⚠️ Manager forecast is `{forecast_coverage_pct}`% populated for late-stage deals. The following deals are missing a forecast category:

| Deal | AE  | Stage | Platform ARR |
| ---- | --- | ----- | ------------ |

Populate from `data_quality.forecast_missing_deals[]`.

**If** `data_quality.null_platform_amt_deals` is not empty:

> ⚠️ `{count}` deals at Qualification+ have no Platform Amount set:

List deal names and AEs.

**If** `data_quality.past_due_open_deals` is not empty:

> ⚠️ `{count}` deals have close dates in the past but are still open:

| Deal | AE  | Close Date | Stage | Platform ARR |
| ---- | --- | ---------- | ----- | ------------ |

---

### Footer

```
Confidential · Internal Use Only
Pete Davies · Head of New Business Sales · Knotch
Generated {meta.generated_at_display}
```
