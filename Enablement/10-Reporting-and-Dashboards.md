# Reporting and Dashboards

**Audience:** Sellers, Sales Managers, RevOps | **Topics:** dashboard, reports, metrics, pipeline health, leadership, weekly insights | **Last Updated:** May 2026

This guide covers Knotch's reporting infrastructure, designed to keep sales leadership and individual contributors aligned on pipeline health, performance, and opportunities for action.

---

## Deal Pipeline Hygiene Dashboard (HubSpot)

**Location:** HubSpot Portal 44523005 | Dashboard ID: 19333613

**Audience:** Sales leadership (VP Sales, Sales Managers), individual AEs for self-service pipeline monitoring

**Purpose:** Real-time visibility into deal quality and immediate action items across the entire pipeline.

### Dashboard Layout

The hygiene dashboard displays **11 reports across 6 rows**, each auto-refreshing with live HubSpot data:

**Row 1: Health Overview**

- Tag Counts (bar chart): Count of deals flagged with each hygiene tag
- Pipeline Overview KPI: Current total open deals (snapshot: 173 deals)

**Row 2: Contact & Engagement Gaps**

- Hygiene by Rep (stacked): Breaks down hygiene flags by deal owner for quick accountability
- No Contacts: Deals with zero contacts assigned (critical blocker)

**Row 3: Timing Risks**

- Past-Due Close: Deals where close date has already passed (forecast accuracy issue)
- No Amount: Deals missing deal amount

**Row 4: Activity & Momentum**

- No Recent Activity: Deals with no activity logged in 21+ days (stalled momentum)
- Stalled: Deals in same stage for 45+ days without progression (urgency signal)

**Row 5: Neglect & Decay**

- Zombie: Deals showing zero activity for 45+ days (at risk of being lost)
- Stale Next Steps: Next step date is in the past but deal is still open (process breakdown)

**Row 6: Single-Threaded Risk**

- Single-Threaded: Deals at Qualification stage or later with only one contact (concentration risk)

### Using the Dashboard

**Quick Filter:** All reports include a quick filter by Deal Owner. Use this to view only your own deals.

**For Individual Contributors (Weekly Review):**

1. Navigate to the hygiene dashboard
2. Filter by your name
3. Review each report for flags on your deals
4. Resolve flags immediately (add contacts, log activity, update close dates, etc.)
5. Goal: **Zero flags** on your active deals

**For Sales Managers (Daily/Weekly Monitoring):**

- Monitor hygiene by rep to identify coaching opportunities
- No Contacts and Single-Threaded flags often indicate insufficient discovery or early-stage deals needing account mapping
- Past-Due Close and Stale Next Steps suggest forecast accuracy issues or stalled negotiations
- Use as a starting point for 1:1 conversations and rep-level coaching

**Exclusions:** All reports exclude Closed Won and Closed Lost deals (historical data tracked separately).

---

## Pipeline Score Reports

**Frequency:** Generated periodically with updated scoring across the entire pipeline

**Purpose:** Predictive health scoring to prioritize effort and identify deals at risk before they stall.

### Scoring Methodology

Each deal receives a **score from 0–100** based on six components:

1. **Stage Progression Weight** (30%): How far deal has advanced through sales cycle; later stages weighted higher
2. **Activity Recency** (25%): Recency of logged interactions (calls, meetings, emails); older = lower score
3. **Contact Count** (15%): Number of contacts assigned to deal relative to stage; below-stage minimums lower score
4. **Deal Completeness** (15%): Percentage of SPICED fields and buying roles populated
5. **Close Date Proximity** (10%): Days until close date; farther away = slightly lower score for short-term deals
6. **Deal Amount** (5%): Larger deals receive marginal boost to prioritize high-value opportunities

### Flag System

Deals receive colored flags based on risk factors:

- **Stale (Red):** No logged activity in 15+ days. Immediate attention required.
- **Overdue (Yellow):** Close date has passed. Requires re-forecasting or resolution.
- **Single-Threaded (Orange):** Only one contact on deal at Qualification stage or later. Risk of deal loss if contact leaves.
- **Incomplete (Black):** Two or more required fields missing (e.g., no amount, no close date, insufficient SPICED detail). Update deal record.
- **High Value at Risk (Blue):** Deal is $250K+ in amount with a score below 50. Escalate to management for intervention.

### Report Organization

Reports are **organized by rep** with the following sections:

**Summary Metrics:**

- Deal count (total open deals)
- Pipeline value ($)
- Average score (rep-level health indicator)

**Highlighted Sections:**

- **Top 5 Deals to Prioritize:** Highest-scoring deals with biggest opportunity for near-term close
- **Top 5 At-Risk Deals:** Lowest-scoring deals with highest probability of stalling or slipping

**Manager Insights Section:**

- Coaching recommendations based on rep's flag distribution
- Suggested conversations around specific deals
- Patterns observed (e.g., activity logging gaps, contact coverage issues, forecast accuracy)

### Using Pipeline Scores

**For Individual Contributors:**

- Review your report weekly alongside your hygiene dashboard
- Prioritize high-score deals for active advancement
- Action at-risk deals: add contacts, log recent activity, clarify next steps

**For Sales Managers:**

- Use manager insights to tailor coaching conversations
- Monitor high-value-at-risk flags closely
- Identify patterns in rep performance (e.g., activity logging, deal qualification consistency)

---

## Weekly Insights Report

**Frequency:** Weekly

**Audience:** Sales leadership, VPs, Sales Managers

**Purpose:** Executive view of sales motion, performance vs. targets, and rep-by-rep accountability.

### Metrics Tracked

**Bookings:** Closed Won revenue ($) vs. weekly/monthly target

**IPMs (Initiated Pipeline Meetings):** Meetings set and held vs. monthly target (6/month per rep = key activity leading indicator)

**Pipeline Creation:** New pipeline value created ($) vs. weekly/monthly target

**Breakdown:** All three metrics are reported by individual rep and in aggregate

**Platform vs. Services Split:** Revenue tracked separately by product line to monitor sales mix and product momentum

### Strategic Observations

Report includes weekly commentary with analysis of:

- Wins and momentum (which reps driving bookings, which products trending)
- Pipeline creation health (whether new business funnel is being fed)
- IPM execution vs. target (leading activity indicator for future pipeline)
- Slippage or forecast changes week-over-week
- Recommendations for priority focus areas

---

## Leadership Metrics (Dashboards & Reviews)

### Weekly Cadence

**Activity Tracking:**

- Calls, meetings, emails logged vs. target
- Broken out by rep
- Used to validate that activity aligns with forecasted outcomes

**Pipeline Movement:**

- Deals advanced (stage progression)
- Deals created (new pipeline value)
- Deals closed (revenue)

### Monthly Cadence

**ARR Tracking:** Annual Recurring Revenue booked and cumulative vs. plan

**Revenue vs. Plan:** Monthly revenue vs. fiscal target, cumulative actuals vs. forecast

## Monthly Executive Report

**Frequency:** Monthly (run on 1st business day of each month)

**Audience:** Sales leadership (Pete -> Jason/Anda)

**Purpose:** QTD bookings, activity, and pipeline status with exec summary and manager forecast.

**How to run:**

1. Open Claude (CLI or desktop — requires shell access)
2. Paste the contents of `Projects/Reporting/Monthly-Exec-Report-Prompt.md`
3. Replace `{QUARTER}` with the current fiscal quarter (Q1=Feb-Apr, Q2=May-Jul, Q3=Aug-Oct, Q4=Nov-Jan)
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

---

### Fiscal Year Targets (Historical & Current)

- **FY24 Actual:** $6.0M
- **FY25 Actual:** $8.0M
- **FY26 Target:** $11.5M

These targets cascade into individual rep quotas ($1.1M each) and monthly bookings targets.

---

## How Sellers Should Use Reporting

### 1. Friday Pipeline Scrub (15 minutes)

**When:** Every Friday before EOD
**What to do:**

1. Open the Deal Pipeline Hygiene dashboard
2. Filter by your name
3. Review each hygiene flag on your deals
4. For every flagged deal, resolve the issue:
   - No Amount → Add deal amount
   - No Contacts → Add at least one contact and assign a buying role
   - No Recent Activity or Stalled → Log a recent call/meeting, or update next step
   - Single-Threaded → Map additional contacts and assign roles
   - Past-Due Close → Update close date or move to closed pipeline
   - Stale Next Steps → Schedule the next step and update the date
5. Refresh dashboard to confirm flags resolved

**Why:** This single 15-minute habit eliminates 90% of deal hygiene issues and keeps forecast accurate.

### 2. Weekly: Review Pipeline Score Report

**When:** Once per week (often Tuesday or Wednesday)
**What to do:**

1. Pull your pipeline score report
2. Review your summary metrics and average score
3. Focus on your Top 5 Deals to Prioritize (high score, close to close date)
4. Take action on your Top 5 At-Risk Deals (low score, flag warnings)
5. Read the Manager Insights section for coaching clues

**Why:** Highest-scoring deals are most likely to close near-term and deserve concentrated effort. At-risk deals need intervention before they slip.

### 3. Before Every Pipeline Review (with Manager)

**Checklist:**

- [ ] All deal basics are current (no past-due close dates; next steps are in the future)
- [ ] Zero hygiene flags on your deals
- [ ] Buyer roles assigned for all contacts on every deal (no contact should sit unassigned)
- [ ] Forecast categories reflect your honest assessment of deal probability (don't sandbag or overstate)

**Why:** This ensures credibility in forecasting, makes reviews more productive, and prevents surprises.

### 4. After Every Meeting (1-Hour Window)

**Otter.ai records every external meeting and auto-creates the meeting record in HubSpot with the transcript attached. Granola runs as your live note-taker. After the meeting, you have a 1-hour window to:**

1. Finalize your Granola notes into the standard meeting template (notes auto-publish to Client Meetings folder and attach to contact/account/deal in HubSpot after the window)
2. Verify the Otter meeting record landed on the correct deal in HubSpot
3. Add any new contacts discovered, and assign each a buying role in the Buying Group
4. Update SPICED fields if you learned something about Situation, Pain, Impact, Critical Event, or Decision Criteria
5. Update the Buying Group org chart if reporting lines or roles became clearer
6. Reassess and update Next Step and Next Step Date
7. Use Claude to speed this up -- ask it to pull your Granola notes, suggest SPICED updates, or identify missing contacts

**Why:** Otter and Granola automate most of the logging, but the 1-hour refinement window is where you add the strategic context that makes the data actionable for coaching and forecasting. After the hour, notes are published -- treat it as a hard deadline.

---

## Accessing Dashboards & Reports in HubSpot

**Path:** Reports > Dashboards > Deal Pipeline Hygiene (or your manager will share direct links)

**Portal:** 44523005

If you don't have access or reports aren't loading, contact your Sales Manager or the Sales Operations team.

---

## Related Documents

- **Pipeline Hygiene and Scoring** (04) — Hygiene tag definitions that dashboards surface
- **Deal Process and SPICED** (03) — Pipeline stages and forecast categories that reports track
- **Seller Quick Reference** (12) — Weekly dashboard review checklist
