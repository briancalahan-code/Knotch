# Quarterly Executive Report — Claude Prompt

You are generating a quarterly executive sales report for Pete Davies (Head of New Business Sales, Knotch). This is the full 6-section report shared with leadership (Jason Lee, Anda Gansca).

**Important:** This prompt requires shell access (Bash tool). It works in Claude Code (CLI), Claude desktop, or Claude Code IDE extensions. It does NOT work in claude.ai web.

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

Use the structure below. Replace all `{json.path}` references with the actual values from the JSON.

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
1. Bookings (QTD)
2. Activity (QTD)
3. Pipeline (Current Q + Next Q)
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

For a quarterly report, the tone should be retrospective + forward-looking. Example: "Q1 closed at $X.XXM (XX% to goal). [Key insight about the quarter]. Heading into Q2, [what needs to change/continue]."

#### KPI Summary

Format as a grid with Current Q and Next Q columns:

| KPI                     | Current Q                                                                                       | Next Q                                                |
| ----------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Closed-Won              | Format `bookings.closed_won_total` as $X.XXM (`bookings.pct_to_goal`% to goal)                  | —                                                     |
| Total Pipeline (Qual+)  | Format `pipeline.qual_plus_current_q.total` as $X.XXM                                           | Format `pipeline.next_q.qual_plus_total` as $X.XXM    |
| Late-Stage Pipeline     | Format `pipeline.late_stage_current_q.total` as $X.XXM                                          | Format `pipeline.next_q.late_stage_total` as $X.XXM   |
| Manager Forecast (C+BC) | Sum of `bookings.forecast.commit.total` + `bookings.forecast.best_case.total`, format as $X.XXM | Format `pipeline.next_q.forecast_cbc_total` as $X.XXM |

#### KPI by Seller

| Seller          | Closed-Won | Pipeline (Current Q) | Pipeline (Next Q) | Forecast (C+BC) |
| --------------- | ---------- | -------------------- | ----------------- | --------------- |
| Don Vanderslice |            |                      |                   |                 |
| Tim Long        |            |                      |                   |                 |
| Pete Davies     |            |                      |                   |                 |
| **Team Total**  |            |                      |                   |                 |

Populate from `bookings.by_seller`, `pipeline.qual_plus_current_q.by_seller` (current Q), `pipeline.next_q.by_seller` (next Q), and `bookings.forecast.by_seller` (current Q) / `pipeline.next_q.forecast_cbc_by_seller` (next Q). Filter to NB team only (Don, Tim, Pete).

Dollar formatting for KPI cards: divide by 1,000,000, round to 2 decimal places, prefix with $, suffix with M. Example: 1102500 -> $1.10M.

---

### Section 1: Bookings (QTD)

#### Closed-Won Summary

- Q Closed-Won: $`bookings.closed_won_total` ({bookings.closed_won_count} deals)
- Quarterly Goal: $`bookings.quarterly_goal`
- % to Goal: `bookings.pct_to_goal`%
- YoY: Prior year same Q was $`bookings.yoy_prior` ({bookings.yoy_pct_change}% change). If `yoy_pct_change` is null, write "No prior year data available."

#### Closed-Won Detail Table

| Deal | AE  | Type | Close Date | ACV |
| ---- | --- | ---- | ---------- | --- |

Populate from `bookings.deals[]`. Format ARR as $XXX,XXX. Sort by ARR descending (already sorted in JSON).

#### Bookings by Type

| Type        | Amount | % of Total |
| ----------- | ------ | ---------- |
| ACE         |        |            |
| Non-ACE     |        |            |
| Partnership |        |            |

Populate from `bookings.by_type`. ACE = deal name contains "ACE". Partnership = deals owned by Ben Smith (627390764) or dealtype "Partnership". Non-ACE = everything else. Calculate % from total.

#### Manager Forecast Summary

| Category  | # Deals | $ Total                   | Top 3 Deals                                             |
| --------- | ------- | ------------------------- | ------------------------------------------------------- |
| Commit    |         |                           | List top 3 by ARR from `bookings.forecast.commit.deals` |
| Best Case |         |                           | List top 3 from `bookings.forecast.best_case.deals`     |
| Pipeline  |         |                           | List top 3 from `bookings.forecast.pipeline_cat.deals`  |
| **Total** |         | `bookings.forecast.total` |                                                         |

If `bookings.forecast.missing.count` > 0:

> Warning: {count} deals totaling ${total} have no manager forecast category set.

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

#### Pipeline Created

- Total: $`activity.pipeline_created.total` (`activity.pipeline_created.count` deals)
- Quarterly Goal: $`activity.pipeline_created.goal` — % to Goal: `activity.pipeline_created.pct_to_goal`%
- ACE: $`activity.pipeline_created.by_type.ACE` | K1: $`activity.pipeline_created.by_type.K1`

| Seller | Pipeline Created $ | # Deals |
| ------ | ------------------ | ------- |

Populate from `activity.pipeline_created.by_seller`.

#### Pipeline Created Detail

| Deal | AE  | Type | Created Date | ACV | Current Stage |
| ---- | --- | ---- | ------------ | --- | ------------- |

Populate from `activity.pipeline_created.deals[]`. Sort by ARR descending (already sorted).

#### Activity by Seller (Current Q vs Prior Q)

| Seller | Emails (Current Q) | Emails (Prior Q) | Meetings (Current Q) | Meetings (Prior Q) | IPMs (Actual/Goal) | Pipe Created $ |
| ------ | ------------------ | ---------------- | -------------------- | ------------------ | ------------------ | -------------- |

Populate current Q from the respective `activity.*` sub-keys. Populate prior Q from `activity.prior_q.*` sub-keys. If `activity.prior_q` is absent (e.g., Q1 of first tracked FY), omit the Prior Q columns.

#### Event Activity

Events this quarter: `activity.events.count`

---

### Section 3: Pipeline (Current Q + Next Q)

#### Late-Stage Deals — Current Quarter

Total late-stage (Proposal + Procurement): $`pipeline.late_stage_current_q.total` (`pipeline.late_stage_current_q.count` deals)

Coverage ratio: `pipeline.coverage_ratio`x (late-stage $ / quarterly goal)

| Deal | AE  | Type | Stage | Close Date | ACV | Manager Forecast |
| ---- | --- | ---- | ----- | ---------- | --- | ---------------- |

Populate from `pipeline.late_stage_current_q.deals[]`.

#### Next Quarter Line-of-Sight

- Late-stage (Proposal+): $`pipeline.next_q.late_stage_total` (`pipeline.next_q.late_stage_count` deals)
- Early pipeline (Qual+): $`pipeline.next_q.early_total`

| Deal | AE  | Stage | Close Date | ACV |
| ---- | --- | ----- | ---------- | --- |

Populate from `pipeline.next_q.deals[]`.

---

### Section 4: Market Feedback

#### Closed-Lost Summary

- Total closed-lost (Qualification+ only): $`market_feedback.closed_lost.total` (`market_feedback.closed_lost.count` deals)
- Note: Excludes deals lost at IPM stage (never qualified).

#### Closed-Lost Detail Table

| Deal | AE  | Type | Close Date | ACV | Loss Reason |
| ---- | --- | ---- | ---------- | --- | ----------- |

Populate from `market_feedback.closed_lost.deals[]`. Sort by ARR descending (already sorted).

#### Loss Reason Rollup

| Reason | # Deals | $ Lost | Read |
| ------ | ------- | ------ | ---- |

Populate counts and totals from `market_feedback.closed_lost.by_reason`.

For the "Read" column, write a 1-2 sentence interpretation for each reason:

- **Not a priority**: Buyer doesn't see urgency. ICP/timing miss or weak point of view.
- **No response**: Outbound never landed. Check channel and message.
- **No budget**: Came in unqualified or budget was pulled. Mostly early-stage.
- **Timing**: Coming back later — re-engagement candidates.
- **Loss of Champion**: Multi-thread depth gap. Single point of failure.
- **Went with competitor**: Product-market fit question. Note which competitor if known.
- **Not specified**: Vague — flag for cleanup. Push AEs to select a real reason.

For any reason not listed above, write a brief data-driven interpretation.

#### Most Actionable Insight

Based on the loss reason data, draft a callout box:

> **Most actionable insight:** [One specific observation from the data with a recommended action. Example: "7 of 23 losses ($575K) were 'Not a priority' — this is an ICP/timing signal. Consider tightening qualification criteria at the IPM stage to filter earlier."]

#### ACE vs K1 Mix Tracking

| Type | Created (Q)        | Won (Q) | Lost (Q) | Open (Qual+) |
| ---- | ------------------ | ------- | -------- | ------------ |
| ACE  | {count} / ${total} |         |          |              |
| K1   | {count} / ${total} |         |          |              |

Populate from `market_feedback.ace_k1_mix`. Show both count and dollar total per cell.

Write a 1-2 sentence observation about the ACE/K1 conversion pattern. Example: "ACE pipeline is building ($X.XXM created) but conversion remains a gap — 0 ACE wins vs X K1 wins. Watch for Q2 ACE progression."

---

### Section 5: Seller Performance

For each seller in `seller_performance` (Pete Davies, Don Vanderslice, Tim Long), write a 3-lens assessment:

```
**[Seller Name]**  [Headline Tag]

R&R:     [Draft 2-3 sentences based on the data — deal ownership patterns, pipeline shape,
          activity level, engagement quality. Be specific: cite deal counts, dollar amounts.]

Goals:   Bookings: ${bookings} ({bookings_count} deals)
         Pipeline created: ${pipeline_created} ({pipeline_count} deals)
         IPMs: {ipms} of 24 goal (team) / 8 goal (Pete)

Metrics: Emails (last month): {emails_last_month}
         Meetings (last month): {meetings_last_month}
         Open pipeline (Qual+): ${open_pipeline}
         Hygiene flags: {hygiene_flags}
         Win rate: {win_rate}%
```

**Headline tags:** Write a 3-6 word headline that captures this seller's quarter. Base it on data patterns:

- High bookings + low pipeline = "Closing machine; needs pipe"
- Zero bookings + strong activity = "Pipeline builder; conversion gap"
- High IPMs + low conversion = "Door-opener; qualification drag"
- Balanced across metrics = "Consistent performer; steady state"

Be honest but constructive — these go in Pete's report to leadership.

#### Commission Achievement Table

| Component               | Team (rollup) | Tim Long | Don Vanderslice | Pete Davies | Ben Smith |
| ----------------------- | ------------- | -------- | --------------- | ----------- | --------- | --- |
| Direct New Biz Bookings |               |          |                 |             |           | —   |
| Pipeline Created — ACE  |               |          |                 |             |           |     |
| Pipeline Created — K1   |               |          |                 |             |           |     |
| IPMs                    |               |          |                 |             |           |     |
| Win Rate                |               |          |                 |             |           |     |

Populate from `seller_performance` data. Ben Smith is Partner channel — show bookings only if available from the overall bookings data.

**Data source note:** Seller assessments use HubSpot activity data (emails, meetings, deal records). Granola meeting quality data is available for Pete's meetings only — Don/Lee/Tim Granola coverage is incomplete. R&R narratives reflect HubSpot data patterns, not meeting quality observations.

---

### Section 6: Initiatives

Based on PTM spreadsheet as of `{initiatives.ptm_file_date}`.

> **Note:** Pete should review and edit this section before sharing. Initiative statuses are extracted from the PTM spreadsheet and may need context that isn't captured in the data.

Map each PTM row from `initiatives.pete_ptms[]` to the appropriate sub-section based on the `priority` field:

#### 6a. Talent

Priorities containing: Revenue, Hiring, Perf Mgmt, Partner, Talent, AE, AD, VDL

| Initiative | Q Status | Next Q Goal | Notes |
| ---------- | -------- | ----------- | ----- |

#### 6b. Enablement

Priorities containing: Deck, Collateral, Objection, Onboarding, Enablement, Training

| Initiative | Q Status | Next Q Goal | Notes |
| ---------- | -------- | ----------- | ----- |

#### 6c. GTM

Priorities containing: IPM, ACE, Pipeline, Event, GTM, Territory, ICP, Stage, Reporting

| Initiative | Q Status | Next Q Goal | Notes |
| ---------- | -------- | ----------- | ----- |

For each row:

- **Initiative** = `priority` + `tactics` (combined into a descriptive title)
- **Q Status** = `status` field
- **Next Q Goal** = Draft a 1-sentence forward-looking goal based on the current status and metrics
- **Notes** = `latest_update` field

If a PTM row doesn't clearly fit any category, place it in 6c. GTM.

PTM sheet used: `{initiatives.ptm_sheet}`

---

### Data Quality Notes

Check each condition and include if applicable:

**If** `data_quality.forecast_coverage_pct` < 100:

> Warning: Manager forecast is `{forecast_coverage_pct}`% populated for late-stage deals. The following deals are missing a forecast category:

| Deal | AE  | Stage | ACV |
| ---- | --- | ----- | --- |

Populate from `data_quality.forecast_missing_deals[]`.

**If** `data_quality.null_platform_amt_deals` is not empty:

> Warning: `{count}` deals at Qualification+ have no Platform Amount set:

List deal names and AEs.

**If** `data_quality.past_due_open_deals` is not empty:

> Warning: `{count}` deals have close dates in the past but are still open:

| Deal | AE  | Close Date | Stage | ACV |
| ---- | --- | ---------- | ----- | --- |

---

### Footer

```
Confidential · Internal Use Only
Pete Davies · Head of New Business Sales · Knotch
{meta.quarter} {meta.fiscal_year} Quarterly Revenue Report
Generated {meta.generated_at_display}
```
