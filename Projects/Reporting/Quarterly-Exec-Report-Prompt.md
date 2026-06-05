# Quarterly Executive Report — Claude Prompt

You are generating a quarterly executive sales report for Pete Davies (Head of New Business Sales, Knotch). This is the full 6-section report shared with leadership (Jason Lee, Anda Gansca).

**Important:** This prompt requires shell access (Bash tool). It works in Claude Code (CLI), Claude desktop, or Claude Code IDE extensions. It does NOT work in claude.ai web.

**Scope:** All deal data should be filtered to NB team owners only (currently Don Vanderslice and Pete Davies). Departed team members (Tim Long, Lee Fine) should appear in historical data if they have activity in the reporting period.

---

## Step 1: Run the data script

Run the compute script to pull fresh data from HubSpot:

```bash
python3 Projects/Reporting/compute_report.py --mode quarterly --quarter {QUARTER}
```

Replace `{QUARTER}` with the fiscal quarter to report on:

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

Use the structure below. Filter all deal-level data to NB team owners only (check `seller_performance` keys for active NB members; also include any departed members with data in the period from `bookings.by_seller`, `activity.ipms.by_seller`, etc.).

---

### Report Header

```
{meta.quarter} {meta.fiscal_year} Quarterly Revenue Report — New Business
Pete Davies, Head of New Business Sales
{meta.generated_at_display}

Data source: HubSpot CRM (live pull)
```

### Table of Contents

```
1. Bookings
2. Activity
3. Pipeline (Next Q)
4. Market Feedback
5. Seller Performance
6. Initiatives
```

---

### Page 1: Executive Summary

#### 3 Things Leadership Should Know

Draft 3 concise bullet points based on the data. Each should be:

- **Data-driven** — cite specific dollar amounts, deal names, percentages from the JSON
- **Forward-looking** — what it means for the next quarter
- **Actionable** — what needs to happen

For a quarterly report, the tone should be retrospective + forward-looking. Include AoV and QoQ bookings change. Example: "Q1 NB bookings: $X.XXM (XX% to goal), AoV $XXX,XXX, down XX% QoQ. [Key insight]. Heading into Q2, [what needs to happen]."

#### KPI Summary

| KPI                    | Current Q (Actual)                                  | Next Q                                                          |
| ---------------------- | --------------------------------------------------- | --------------------------------------------------------------- |
| NB Bookings            | `bookings.closed_won_total` NB-filtered (% to goal) | —                                                               |
| AoV                    | `bookings.aov` NB-filtered                          | —                                                               |
| QoQ Change             | `bookings.qoq_pct_change`% vs `bookings.qoq_prior`  | —                                                               |
| Total Pipeline (Qual+) | —                                                   | `pipeline.next_q.qual_plus_total` NB-filtered                   |
| Late-Stage (Proposal+) | —                                                   | `pipeline.next_q.late_stage_total` NB-filtered                  |
| Manager Forecast       | —                                                   | `pipeline.next_q.forecast.weighted_total` NB-filtered (vs goal) |

#### KPI by Seller

| Seller | Q Bookings | Pipe Created | IPMs | Next Q Pipeline | Next Q Coverage |
| ------ | ---------- | ------------ | ---- | --------------- | --------------- |

Populate from `bookings.by_seller`, `activity.pipeline_created.by_seller`, `activity.ipms.by_seller`, `pipeline.next_q.by_seller`. Filter to NB team. Include departed members if they have data.

Next Q Coverage = seller's next Q pipeline / `seller_targets.bookings_quarterly`.

Per-seller goals from `seller_targets`: $275K bookings/Q, $1.1M pipe created/Q, 24 IPMs/Q, $4.4M open pipeline, 29% win rate.

Dollar formatting for KPI cards: divide by 1,000,000, round to 2 decimal places, prefix with $, suffix with M. Example: 1102500 -> $1.10M.

---

### Section 1: Bookings

#### Closed-Won Summary (NB Team)

- Q Closed-Won (NB): Sum NB team sellers from `bookings.by_seller` ({count} deals), AoV: `bookings.aov`
- Quarterly Goal: $`bookings.quarterly_goal`
- % to Goal: computed from NB total vs goal
- QoQ: Prior Q was $`bookings.qoq_prior` (`bookings.qoq_pct_change`% change)

#### Closed-Won Detail Table

| Deal | AE  | Type | Close Date | ACV |
| ---- | --- | ---- | ---------- | --- |

Populate from `bookings.deals[]`, filtered to NB team owners. Format ACV as $XXX,XXX. Sort by ACV descending.

#### Bookings by Type (NB Only)

| Type    | Amount | % of Total |
| ------- | ------ | ---------- |
| ACE     |        |            |
| Non-ACE |        |            |

Compute from NB-filtered deals using their `booking_type` field.

#### Manager Forecast

| Category  | # Deals                                | $ Pipeline                                | $ Manager Forecast                        | Weight |
| --------- | -------------------------------------- | ----------------------------------------- | ----------------------------------------- | ------ |
| Commit    | `bookings.forecast.commit.count`       | `bookings.forecast.commit.pipeline`       | `bookings.forecast.commit.weighted`       | 90%    |
| Best Case | `bookings.forecast.best_case.count`    | `bookings.forecast.best_case.pipeline`    | `bookings.forecast.best_case.weighted`    | 50%    |
| Pipeline  | `bookings.forecast.pipeline_cat.count` | `bookings.forecast.pipeline_cat.pipeline` | `bookings.forecast.pipeline_cat.weighted` | 10%    |
| **Total** |                                        | `bookings.forecast.pipeline_total`        | `bookings.forecast.weighted_total`        |        |

If `bookings.forecast.missing.count` > 0:

> Warning: {count} deals totaling ${pipeline} have no manager forecast category set.

---

### Section 2: Activity

#### Summary (NB Team, QoQ)

| Metric | Current Q | Prior Q | QoQ |
| ------ | --------- | ------- | --- |

Show totals (not by person) for: Emails, Meetings, IPMs, Pipeline Created. Current Q from `activity.*` totals, Prior Q from `activity.prior_q.*` totals. QoQ = percentage change. If `activity.prior_q` is absent, omit Prior Q and QoQ columns.

#### IPMs

| Seller | IPMs | Goal | % to Goal |
| ------ | ---- | ---- | --------- |

Populate from `activity.ipms.by_seller`, filtered to NB team (include departed if present). Goal = `seller_targets.ipms_quarterly` (24 per person). Team total row with team goal = NB sellers × 24.

#### Pipeline Created

| Seller | Created | Goal | % to Goal |
| ------ | ------- | ---- | --------- |

Populate from `activity.pipeline_created.by_seller`, filtered to NB team. Goal = `seller_targets.pipeline_created_quarterly` ($1.1M per person). Team total row.

_Below table: ACE: $`activity.pipeline_created.by_type.ACE` | K1: $`activity.pipeline_created.by_type.K1`_

#### Events

| Event | Attended | Invited | No Show | Viewed Replay | Total |
| ----- | -------- | ------- | ------- | ------------- | ----- |

Populate from `activity.events.by_event`. One row per event, status counts across columns. Add **Total** row from `activity.events.by_status`. Add **Prior Q** row from `activity.prior_q.events.by_status` (if present). Add **QoQ** row showing percentage change per status.

---

### Section 3: Pipeline — Next Quarter

_NB-owned deals only. Show only the next quarter's pipeline (not current Q)._

- Total Pipeline (Qual+): `pipeline.next_q.qual_plus_total` NB-filtered
- Quarterly Bookings Goal: `targets.bookings` (next Q)
- Coverage: NB pipeline / goal
- Late-Stage (Proposal+): `pipeline.next_q.late_stage_total` NB-filtered ({count} deals)

#### Manager Forecast vs Goal

| Category  | # Deals | $ Pipeline                                | $ Manager Forecast                        | Weight |
| --------- | ------- | ----------------------------------------- | ----------------------------------------- | ------ |
| Commit    |         |                                           |                                           | 90%    |
| Best Case |         |                                           |                                           | 50%    |
| Pipeline  |         |                                           |                                           | 10%    |
| **Total** |         | `pipeline.next_q.forecast.pipeline_total` | `pipeline.next_q.forecast.weighted_total` |        |

NB-filtered weighted forecast vs `targets.bookings`: show as percentage.

If `pipeline.next_q.forecast.by_category.missing.count` > 0:

> Warning: {count} deals totaling ${pipeline} have no manager forecast category set.

#### Next Q Deal Table

| Deal | AE  | Stage | Close Date | ACV | Forecast |
| ---- | --- | ----- | ---------- | --- | -------- |

Populate from `pipeline.next_q.deals[]`, filtered to NB team owners. Include forecast category from `pipeline.late_stage_current_q.deals[]` where available.

---

### Section 4: Market Feedback

#### Closed-Lost Summary (NB Team)

- Total closed-lost (NB, Qualification+ only): filter `market_feedback.closed_lost.deals[]` to NB team owners
- Note: Excludes deals lost at IPM stage (never qualified).

#### Closed-Lost Detail Table

| Deal | AE  | ACV | Loss Reason |
| ---- | --- | --- | ----------- |

Populate from `market_feedback.closed_lost.deals[]`, filtered to NB team. Sort by ACV descending.

#### Loss Reason Rollup

| Reason | # Deals | $ Lost | Read |
| ------ | ------- | ------ | ---- |

Compute from NB-filtered losses. For the "Read" column:

- **Not a priority**: Buyer doesn't see urgency. ICP/timing miss or weak point of view.
- **No response**: Outbound never landed. Check channel and message.
- **No budget**: Came in unqualified or budget was pulled. Mostly early-stage.
- **Timing**: Coming back later — re-engagement candidates.
- **Loss of Champion**: Multi-thread depth gap. Single point of failure.
- **Other**: Vague — flag for cleanup. Push AEs to select a real reason.

> **Most actionable insight:** [One specific observation from the NB loss data with a recommended action.]

#### ACE vs K1 Mix Tracking

| Type | Created (Q)        | Won (Q) | Lost (Q) | Open (Qual+) |
| ---- | ------------------ | ------- | -------- | ------------ |
| ACE  | {count} / ${total} |         |          |              |
| K1   | {count} / ${total} |         |          |              |

Populate from `market_feedback.ace_k1_mix`. Write a 1-2 sentence observation about the ACE/K1 conversion pattern.

---

### Section 5: Seller Performance

Per-seller targets from `seller_targets`:

| Target           | Per Seller/Q                       |
| ---------------- | ---------------------------------- |
| Bookings         | $275,000 ($1.1M/yr)                |
| Pipeline Created | $1,100,000 (4x quarterly bookings) |
| IPMs             | 24                                 |
| Open Pipeline    | $4,400,000 (4x annual bookings)    |
| Win Rate         | 29%                                |

For each seller in `seller_performance`, write a headline tag and 2-3 sentence R&R narrative, then show the metrics table:

**Headline tags:** 3-6 words capturing the seller's quarter:

- High bookings + low pipeline = "Closing machine; needs pipe"
- Zero bookings + strong activity = "Pipeline builder; conversion gap"
- High IPMs + low conversion = "Door-opener; qualification drag"

**Metrics table per seller:**

| Metric          | Actual                       | Goal       | %   |
| --------------- | ---------------------------- | ---------- | --- |
| Bookings        | `bookings` ({count})         | $275,000   |     |
| Pipe Created    | `pipeline_created` ({count}) | $1,100,000 |     |
| IPMs            | `ipms`                       | 24         |     |
| Win Rate        | `win_rate`%                  | 29%        |     |
| Open Pipeline   | `open_pipeline`              | $4,400,000 |     |
| Next Q Coverage | NB next Q pipeline / $275K   | 4.0x       |     |

Include departed members (Tim Long, Lee Fine) if they have data in the period — show abbreviated metrics, note "Departed."

Be honest but constructive — these go in Pete's report to leadership.

---

### Section 6: Initiatives

Based on PTM spreadsheet as of `{initiatives.ptm_file_date}`.

> **Note:** Pete should review and edit this section before sharing.

Map each PTM row from `initiatives.pete_ptms[]` to the appropriate sub-section:

#### 6a. Talent

Priorities containing: Revenue, Hiring, Perf Mgmt, Partner, Talent, AE, AD, VDL

#### 6b. Enablement

Priorities containing: Deck, Collateral, Objection, Onboarding, Enablement, Training

#### 6c. GTM

Priorities containing: IPM, ACE, Pipeline, Event, GTM, Territory, ICP, Stage, Reporting

| Initiative | Q Status | Next Q Goal | Notes |
| ---------- | -------- | ----------- | ----- |

PTM sheet used: `{initiatives.ptm_sheet}`

---

### Data Quality Notes

Check each condition and include if applicable:

**If** `data_quality.forecast_coverage_pct` < 100:

> Warning: Manager forecast is {forecast_coverage_pct}% populated for late-stage deals.

**If** `data_quality.null_platform_amt_deals` is not empty:

> Warning: {count} deals at Qualification+ have no Platform Amount set.

**If** `data_quality.past_due_open_deals` is not empty:

> Warning: {count} deals have close dates in the past but are still open.

---

### Footer

```
Confidential · Internal Use Only
Pete Davies · Head of New Business Sales · Knotch
{meta.quarter} {meta.fiscal_year} Quarterly Revenue Report
Generated {meta.generated_at_display}
```
