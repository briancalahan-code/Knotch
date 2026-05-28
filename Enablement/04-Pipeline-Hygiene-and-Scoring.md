# Pipeline Hygiene and Scoring

**Audience:** Sellers, Sales Managers, RevOps | **Topics:** hygiene tags, pipeline scoring, deal health, dashboard, stale, zombie | **Last Updated:** May 2026

---

## Overview

Pipeline hygiene is the foundation of accurate forecasting, effective deal management, and accountability across the sales organization. Knotch uses a structured hygiene framework within HubSpot to surface pipeline risk in real time, flag unhealthy deals, and drive consistent stage progression and deal health standards.

The **Deal Pipeline Hygiene Dashboard** (HubSpot Dashboard ID: 19333613) provides a centralized view of hygiene metrics, enabling managers and individual contributors to identify and resolve pipeline issues systematically. In tandem with the **Pipeline Score Report**, the hygiene framework creates an objective, data-driven approach to deal management and pipeline quality.

---

## Ten Hygiene Tags

Hygiene tags are automated signals that flag deals falling below defined health standards. Each tag has a clear definition, business impact, and resolution path.

### 1. No Amount

**Definition:** Deal has no dollar value assigned.

**Why it matters:** Deals without amounts skew forecast accuracy and obscure true pipeline value. An unvalued opportunity cannot be prioritized or tracked toward revenue goals.

**How to clear:**

- Assess the contract scope and typical pricing for similar deals in the same stage
- If full scope is unknown, estimate conservatively based on available information
- Work with the buyer to confirm deal size
- Input best estimate in the **Amount** field in HubSpot

**Timeline:** Resolve within 1-2 weeks of deal creation.

---

### 2. Stalled Deal

**Definition:** Deal has remained in the same stage for 45+ consecutive days with no stage progression.

**Why it matters:** Stalled deals indicate lack of forward momentum, often signaling buyer hesitation, internal organizational delays, or dead-end opportunities. Stalled deals consume rep attention without advancing the pipeline.

**How to clear:**

- Assess the reason for stall (e.g., internal approval pending, buyer resource constraints, missing information)
- Take a concrete action: schedule a next meeting, escalate internally, or clarify decision criteria
- Advance the deal to the next stage once the blocking issue is resolved
- Alternatively, close the deal as Lost if resolution is not feasible

**Timeline:** Weekly review required; resolution within 2 weeks of tag assignment.

---

### 3. Zombie

**Definition:** Deal has had zero logged activity (calls, meetings, emails, notes) for 45+ consecutive days.

**Why it matters:** Deals with no recent engagement are effectively abandoned. No activity indicates the deal is not moving or may never close. Zombie deals obscure true pipeline health.

**How to clear:**

- Re-engage the buyer immediately: schedule a call, send a check-in email, or request a meeting
- Log the interaction in HubSpot
- If buyer is unresponsive, close the deal as Lost
- If re-engagement succeeds, log all subsequent interactions consistently

**Timeline:** Respond within 1 week of tag assignment.

---

### 4. No Recent Activity

**Definition:** Deal has no logged activity in 21+ consecutive days.

**Why it matters:** Regular activity demonstrates deal momentum and keeps the buyer engaged. A 21+ day gap suggests the deal may be forgotten or deprioritized.

**How to clear:**

- Log a call, email, or meeting with the buyer
- For outbound activity, document what you communicated and next steps
- Ensure the activity is logged at the deal level in HubSpot

**Timeline:** Address within 1 week of tag assignment.

---

### 5. No Contacts

**Definition:** Deal has zero associated contacts.

**Why it matters:** Without contact associations, there is no clear buyer to engage, no way to track communication, and no foundation for a buying committee. This is a critical blocker.

**How to clear:**

- Identify at least one contact at the buying organization
- Create or find the contact record in HubSpot
- Associate the contact to the deal
- Confirm the contact's role, department, and seniority

**Timeline:** Resolve before moving beyond Qualification stage.

---

### 6. Single Threaded

**Definition:** Deal has only one associated contact.

**Why it matters:** Single-threaded deals are fragile. If the one contact leaves, loses interest, or is overruled, the deal collapses. Multithreading reduces risk and accelerates consensus.

**How to clear:**

- Identify additional stakeholders involved in the buying decision (e.g., champion, influencer, technical evaluator, approver)
- Map the buying committee structure with at least 2-3 contacts per deal
- Ensure contacts at different levels and departments are represented
- Document each contact's role and level

**Timeline:** Resolve before moving to Consensus stage. No deal advances past Qualification with single threading.

---

### 7. Stale Next Steps

**Definition:** The **Next Step Date** field has passed without an update to the next step or date.

**Why it matters:** Stale next steps indicate broken commitments or lack of deal momentum. They also render forecasting inaccurate—if next steps aren't current, the forecast cannot be trusted.

**How to clear:**

- Review the previous next step and its outcome
- Take action on the step if it was missed, or document why it was not necessary
- Update the **Next Step** field with the new action and expected date
- Set the **Next Step Date** to a future date with realistic timing

**Timeline:** Update weekly during pipeline reviews.

---

### 8. Past-Due Close

**Definition:** Deal's **Close Date** is in the past.

**Why it matters:** Past-due close dates are forecasting errors. They muddy the pipeline and create false urgency or false security. Past-due closes must be either resolved immediately or closed out.

**How to clear:**

- Determine the actual close timeline with the buyer
- Update **Close Date** to a realistic future date based on the buying cycle stage and agreed-upon timeline
- Alternatively, close the deal as Won or Lost
- If updating, ensure the new date aligns with stage progression and next steps

**Timeline:** Resolve within 48 hours of identification.

---

### 9. IPM Stale

**Definition:** Deal has been in **IPM** stage for **14+ days** without advancing to Qualification.

**Why it matters:** IPM is a decision gate, not a holding pen. If the first meeting happened and you haven't advanced or killed the deal within two weeks, either the deal isn't real or you're not driving urgency. Stale IPM deals inflate early pipeline and mask prospecting gaps.

**How to clear:**

- Complete your post-meeting assessment: is this worth spending time on in the next 6 weeks?
- If yes, capture Situation and Pain (SPICED), identify a coach or champion, and move to Qualification
- If no, close as Lost with a close reason

**Timeline:** Resolve within 1 week of tag assignment.

---

### 10. No Line Items

**Definition:** Deal is past IPM stage (Qualification or later) with **zero associated line items**.

**Why it matters:** Line items define what you're selling. A deal in Qualification or beyond without line items has no defined scope, which means no accurate amount, no clear proposal path, and unreliable forecasting. Line items should be added as soon as the product scope is understood.

**How to clear:**

- Add line items to the deal record reflecting the products/services being proposed
- Ensure the line item total aligns with the deal amount

**Timeline:** Resolve before advancing past Qualification.

---

## Dashboard Layout and Usage

The **Deal Pipeline Hygiene Dashboard** provides a comprehensive, at-a-glance view of pipeline health across the organization and by individual rep.

### Dashboard Structure

**Row 1: Summary Metrics**

- Tag Counts bar chart: Visual breakdown of all ten hygiene tags and deal count per tag
- Pipeline Overview KPI: Total open deals, total pipeline value, average deal size, and overall hygiene score

**Row 2: Distribution by Role**

- Hygiene tags by Deal Owner: Rep-level performance on hygiene
- No Contacts: Count and list of deals lacking contact associations

**Row 3: Financial Risk**

- Past-Due Close: Count, rep attribution, and list of deals with overdue close dates
- No Amount: Count, rep attribution, and list of deals without values

**Row 4: Activity and Stage Risk**

- No Recent Activity: Count and list of deals without activity in 21+ days
- Stalled Deals: Count and list of deals in same stage 45+ days

**Row 5: Engagement Risk**

- Zombie Deals: Count and list of deals with 45+ days zero activity
- Stale Next Steps: Count and list of deals with expired next step dates

**Row 6: Multithreading**

- Single-Threaded Deals: Count and list of deals with only one contact

### How to View the Dashboard

1. In HubSpot, navigate to **Reporting > Dashboards**
2. Search for or select **Deal Pipeline Hygiene** (Dashboard ID: 19333613)
3. Use the **Deal Owner** filter to view your own deals or drill into a specific rep's portfolio
4. Use the **Pipeline Stage** filter to focus on a specific stage (e.g., Proposal, Procurement)
5. Click any deal name to jump to the deal record for immediate action

### How to Update and Clear Tags

Hygiene tags are **automatically assigned and cleared based on deal field values**. You do not manually assign or remove tags.

**To clear a tag:**

1. Click the deal name from the dashboard
2. Update the relevant field(s):
   - No Amount → Input a value in the **Amount** field
   - Stalled Deal → Advance the **Stage**
   - Zombie → Log an activity (call, meeting, email)
   - No Recent Activity → Log an activity
   - No Contacts → Add a contact association
   - Single Threaded → Add additional contact associations
   - Stale Next Steps → Update **Next Steps** and **Next Step Date** fields
   - Past-Due Close → Update **Close Date** to a future date
3. The tag automatically clears when the condition is resolved
4. No manual tag removal is necessary

---

## Pipeline Score Report Methodology

The **Pipeline Score Report** assigns an objective health score (0–100) to each deal based on quantified deal characteristics. This score identifies at-risk deals, highlights high-value deals requiring intervention, and provides data-driven deal prioritization.

### Scoring Inputs

Each deal's score is calculated from:

- **Stage progression:** Advancement timing and velocity through pipeline stages
- **Activity recency:** Frequency and recency of logged interactions (calls, meetings, emails, notes)
- **Contact count:** Number of contacts associated and breadth of buying committee
- **Deal completeness:** Presence and accuracy of key fields (amount, close date, next steps, industry, etc.)
- **Close date proximity:** Alignment of close date with stage and expected sales cycle length
- **Deal amount:** Larger, clearer deal scopes score higher

### Score Interpretation

- **80–100:** Healthy deal, strong momentum, minimal risk. On track to close.
- **60–79:** Good progress, minor gaps to address (e.g., one stale next step, limited contacts). Monitor for regression.
- **40–59:** Caution zone. Multithreading gaps, stale activity, or unclear scope. Requires active management and intervention.
- **0–39:** High risk. Multiple hygiene issues, no clear path to close, or deal may be unwinnable. Reassess viability.

### Automated Flags

The Pipeline Score Report auto-flags deals meeting these criteria:

- **Stale:** No activity 15+ days → Score penalty and flag
- **Overdue:** Close date passed → Critical flag
- **Single-threaded:** Only one contact → Fragility flag
- **Incomplete:** 2+ key fields missing → Data quality flag
- **High Value at Risk:** Deal size $250K+ with score <50 → Executive attention flag

### Manager Insights

The Pipeline Score Report auto-generates insights for each manager, including:

- Reps with the most at-risk deals requiring coaching
- High-value deals ($250K+) with score <50 and recommended interventions
- Reps excelling at multithreading, activity, or deal completion
- Pipeline trend analysis (improving vs. declining score trends week-over-week)

---

## Weekly Pipeline Scrub Cadence

Maintaining pipeline health requires consistent, structured review. Every Friday, each AE should dedicate 15 minutes to a **Pipeline Scrub** covering every open deal in their portfolio.

### Weekly Pipeline Scrub Checklist (15 minutes)

For each open deal:

- [ ] **Amount**: Is a best estimate entered? Does it reflect current scope?
- [ ] **Stage**: Is the current stage accurate? Should it advance or be reassessed?
- [ ] **Forecast**: Is the forecast classification (Commit, Best Case, Pipeline) aligned with deal health and probability?
- [ ] **Next Step**: Is the next step clear, actionable, and dated?
- [ ] **Next Step Date**: Does the date reflect a realistic timeline? Is it in the future?
- [ ] **Activity**: Have I logged this week's interactions (calls, emails, meetings)?
- [ ] **Close Date**: Is it realistic for the current stage and sales cycle?
- [ ] **Contacts**: Are 2+ contacts associated? Does the committee span decision-making levels?

### Dashboard Hygiene Check

After reviewing individual deals:

1. Pull up the **Deal Pipeline Hygiene Dashboard**
2. Filter to your own deals
3. Confirm no deals are tagged with hygiene issues
4. If tags appear, address them immediately or document a resolution plan
5. Validate the deal count and total pipeline value are accurate

### Friday Timing

Pipeline scrubs should be completed by **close of business Friday** each week. This ensures:

- Hygiene is current for Monday pipeline reviews
- Forecast is accurate for the upcoming week
- No deal surprises bubble up unexpectedly

---

## Leadership Standards: Zero Tolerance for Hygiene Issues

Knotch leadership expects **zero hygiene flags at all times** for deals in active pursuit. This standard:

- Ensures pipeline accuracy and forecast reliability
- Demonstrates accountability and deal discipline
- Accelerates deal progression by forcing clarity and action
- Reduces forecast surprises and pipeline volatility

**Pipeline reviews** reference the Deal Pipeline Hygiene Dashboard as the primary source of truth. Deals with unresolved hygiene tags are de-prioritized in forecast discussion and require manager intervention and resolution plans.

---

## Implementation Checklist

- [ ] Access the Deal Pipeline Hygiene Dashboard (ID: 19333613)
- [ ] Review your own deals on the dashboard this week
- [ ] Resolve any open hygiene tags on your deals
- [ ] Complete your first Friday Pipeline Scrub (15 min, every open deal)
- [ ] Join the weekly Pipeline Review (timing to be shared by your manager)

---

## Support and Questions

Reach out to your manager or the RevOps team with questions on:

- How to resolve a specific hygiene tag
- Dashboard access or filter issues
- Pipeline Score methodology or a specific deal's score
- Pipeline Scrub timing or cadence

---

## Related Documents

- **Deal Process and SPICED** (03) — Pipeline stages and exit criteria that hygiene tags monitor
- **Reporting and Dashboards** (10) — Dashboard access, report cadences, leadership metrics
- **Seller Quick Reference** (12) — Hygiene tag summary and weekly scrub checklist
