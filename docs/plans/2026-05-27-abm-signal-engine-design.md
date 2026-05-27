# ABM Signal Engine — Design Document

**Date:** 2026-05-27
**Author:** Brian Calahan (GTM Evolved)
**Client:** Knotch
**HubSpot Portal:** 44523005
**Scope:** Full — brainstorm, stress-tested, COO-requested

---

## Problem Statement

Knotch's COO asked: "How close to implementing [a modern ABM engine] are we?" referencing the Growth Unhinged 7-step framework. The answer: Knotch has ~65% of the infrastructure built but lacks the signal aggregation, account-level awareness tracking, and activation routing that turn raw CRM data into an ABM motion.

**Knotch is an ideal ABM candidate:**

- Small TAM (1,702 tiered accounts) — every account can be individually managed
- High ACV ($130K+ average, $167K Tier I) — ABM economics work above $50K ACV
- Long sales cycle (60-150 days) — multiple signal touchpoints before close
- Enterprise buyers with multi-person committees — signals accumulate across contacts

---

## Design Decision: Approach B — "Signal Engine"

Three approaches were evaluated:

| Approach             | Cost         | Timeline        | Coverage | Verdict                                           |
| -------------------- | ------------ | --------------- | -------- | ------------------------------------------------- |
| A: Foundation        | $0/mo        | 2-3 weeks       | 65%      | Viable quick win but no visitor ID or attribution |
| **B: Signal Engine** | **$1-2K/mo** | **10-12 weeks** | **85%**  | **Recommended — highest ROI per dollar**          |
| C: Full ABM Stack    | $4-6K/mo     | 12-16 weeks     | 100%     | Earn this after B proves out                      |

**Why B:** Website visitor ID is the single highest-ROI signal source. Fills the ICP v3 engagement gap (907 zeroes). At $140K ACV, 1-2 additional signal-attributed deals/year justify the cost 6-15x over.

---

## Architecture

### Core Concept: Account Awareness Stages

A new company-level property that tracks where each account sits in the awareness funnel. This is **separate from** contact-level Lead Status and Lifecycle Stage.

```
Contact-level:  Lead Status    (Cold → Attempted → Connected → Meeting Booked → Open Opp)
                Lifecycle Stage (Cold Prospect → MQL → SQL → Opportunity → Customer)

Account-level:  Awareness Stage (Unaware → Aware → Engaged → Active → In Pipeline)  ← NEW
```

**Awareness Stage definitions:**

| Stage       | Definition              | Trigger                                                                                   |
| ----------- | ----------------------- | ----------------------------------------------------------------------------------------- |
| Unaware     | No signals detected     | Default for all accounts                                                                  |
| Aware       | Passive signal detected | Website visit identified OR email opened OR event invited                                 |
| Engaged     | Active signal detected  | Event attended OR form submitted OR 3+ website visits in 30 days OR Connected Lead Status |
| Active      | Multi-signal engagement | 2+ signal types detected within 30 days OR Meeting Booked Lead Status                     |
| In Pipeline | Deal created            | Any associated deal enters IPM stage or beyond                                            |

**Transition rules:**

- Forward transitions: automatic via Signal Score thresholds
- Backward transitions (decay): stage downgrades after 90 days of no new signals (Active → Engaged → Aware). In Pipeline only downgrades when deal closes lost AND no other active deals exist.
- Exclusions: contacts with Lead Status = Left Company, Junk, or Bad Fit do NOT contribute to account-level awareness calculation

### Signal Score (0-100)

New company property computed from cross-object data. Determines awareness stage transitions and activation routing.

**Weights (launch configuration — rebalanced per stress test):**

| Signal Source           | Weight | Data Source                                            | Coverage at Launch                    |
| ----------------------- | ------ | ------------------------------------------------------ | ------------------------------------- |
| Lead Status Progression | 30%    | Max numeric Lead Status across company contacts        | ~100% (all contacts have Lead Status) |
| Event Attendance        | 20%    | Count + recency of Event Attendance records            | ~17% (907/1,092 accounts at zero)     |
| Deal Activity           | 25%    | Active deal count + pipeline score + stage progression | ~7% (81 accounts with open deals)     |
| Contact Depth           | 15%    | Associated contact count (absolute, not growth)        | ~100%                                 |
| Website Engagement      | 10%    | Visitor-identified page views (2+ pages, 30+ seconds)  | 0% at launch, builds over time        |

**Weight evolution:** As event data coverage improves past 50% of tiered accounts, Event Attendance weight increases to 30% and Lead Status decreases to 20%. This rebalancing is a manual config change reviewed quarterly.

**Computation method: External Python script**

Knotch does not have Operations Hub, so Signal Score and Awareness Stage are computed by an external Python script modeled on the existing `icp-score-automation.py`. The script:

- Runs on a scheduled cron (every 6 hours)
- Reads contact Lead Status, Event Attendance records, deal data, and contact counts via HubSpot API
- Computes weighted Signal Score per company
- Derives Awareness Stage from Signal Score thresholds
- Writes results to 3 HubSpot company properties via API batch update

**Latency:** 6-hour refresh cycle. Acceptable given the weekly sales review cadence — signals do not need to be real-time to drive ABM activation. Slack alerts fire on property change (after the script writes), so routing is near-real-time once the score updates.

**Script template:** `icp-score-automation.py` already solves the analogous problem of cross-object aggregation → company property writes. The Signal Score script will follow the same patterns: paginated API reads, in-memory computation, batch property writes, error handling, and logging.

**Future upgrade path:** If Knotch adds Operations Hub Professional ($800/mo) or Enterprise ($2,000/mo), the script logic can migrate to custom code actions inside HubSpot workflows for real-time computation. See "Operations Hub Upgrade Path" section below for details.

**Output properties (3 new company properties):**

| Property                | Internal Name             | Type     | Values                                       |
| ----------------------- | ------------------------- | -------- | -------------------------------------------- |
| ABM Awareness Stage     | `abm_awareness_stage`     | Dropdown | Unaware, Aware, Engaged, Active, In Pipeline |
| ABM Signal Score        | `abm_signal_score`        | Number   | 0-100                                        |
| ABM Signal Last Updated | `abm_signal_last_updated` | Date     | Timestamp of last computation                |

### Signal Sources

**Existing (recycled — zero build cost):**

| Signal                 | Source Asset                                | How It Feeds ABM                                                                                                      |
| ---------------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Outreach progression   | Lead Status (5 values)                      | Numeric conversion: Cold=1, Attempted=2, Connected=3, Meeting Booked=4, Open Opp=5. Max across company contacts.      |
| Event engagement       | Event Attendance object (4,464 records)     | Count of records with event_status=Attended or Registered. Recency bonus: events in last 90 days weighted 2x.         |
| Deal health            | 10 hygiene tags + Pipeline Score (0-100)    | Active deal exists = base score. Pipeline Score >60 = healthy signal. 3+ hygiene tags = negative signal (suppresses). |
| Buying committee depth | Buying Roles (11 defined) + contact count   | 3+ distinct roles filled = strong buying signal. Contact count per company.                                           |
| Stakeholder authority  | Seniority auto-assignment (9 levels, 99.4%) | VP+ seniority contact at account = weighted 2x in Lead Status progression.                                            |
| ICP fit                | ICP v3 scoring (8 properties)               | Score determines activation tier thresholds. Not a signal input — it is the routing backbone.                         |
| Data freshness         | Enrichment tracking (source + date)         | `last_enrichment_date` > 90 days = stale flag. Triggers re-enrichment before activation.                              |
| Pipeline position      | Forecast categories (5 values)              | Commit/Best Case deals suppress top-of-funnel activation (don't spam accounts about to close).                        |
| Corporate hierarchy    | Parent-child associations (6 active)        | Signal at child (Activision) can optionally warm parent (Microsoft). Configurable per association.                    |

**New (build required):**

| Signal                         | Source                                | Build Effort                                              | Monthly Cost              |
| ------------------------------ | ------------------------------------- | --------------------------------------------------------- | ------------------------- |
| Website visitor identification | RB2B or Warmly                        | Integration setup + quality filters                       | $500-1K/mo                |
| Job change detection           | Apollo weekly enrichment (title diff) | Workflow or script comparing before/after jobtitle        | $0 (uses existing Apollo) |
| Lead Status numeric conversion | Hidden workflow                       | New contact workflow: Lead Status → `lead_status_numeric` | $0                        |

### Visitor ID Quality Filters (Stress Test Fix)

Raw visitor-identified contacts enter HubSpot but are gated before feeding signals:

| Filter           | Threshold                                                           | Rationale                               |
| ---------------- | ------------------------------------------------------------------- | --------------------------------------- |
| Page views       | 2+ pages in session                                                 | Eliminates bounce traffic               |
| Time on site     | 30+ seconds                                                         | Eliminates bot/accidental visits        |
| Company match    | Must match existing company OR be ICP-relevant industry             | Prevents noise from non-target visitors |
| Domain exclusion | Exclude knotch.com, competitors, job boards, personal email domains | Standard ABM hygiene                    |

Contacts below threshold: created in HubSpot (for data completeness), Lead Status = Cold, but do NOT increment Signal Score or trigger alerts.

### Routing & Activation (3-Tier)

Signal routing follows existing territory assignment (80% geography). No new ownership logic needed.

| Tier                        | ICP Score | Signal Threshold  | Activation                                                                                                                                    |
| --------------------------- | --------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tier I** (291 accounts)   | 70+       | Signal Score ≥ 40 | Slack alert to owning AE with account brief (signal type, contact details, suggested action). AE does manual, personalized outreach.          |
| **Tier II** (433 accounts)  | 50-69     | Signal Score ≥ 55 | Auto-enroll champion-persona contact in nurture sequence (Apollo). Auto-add to next event invite list. Slack digest (weekly, not per-signal). |
| **Tier III** (978 accounts) | <50       | Signal Score ≥ 70 | Auto-enroll in content drip (HubSpot email sequence). No Slack alert. Monthly batch review only.                                              |

**Alert fatigue prevention:**

- Tier I: max 1 Slack alert per account per 7 days (even if multiple signals fire)
- Tier II: weekly digest only, no real-time alerts
- Tier III: no alerts at all — fully automated
- All tiers: suppress alerts for accounts with Forecast Category = Commit or Closed (don't interrupt active close)

### ICP v3 Integration

The Signal Score feeds back into ICP v3's engagement pillar, closing the biggest data gap:

**Current state:** Engagement pillar = 25% of ICP composite. Scored on events (50%), contacts (30%), deals (20%). 907/1,092 accounts score 0 on events.

**After Signal Engine:** Signal Score replaces the raw event count in the engagement pillar calculation. This gives every account a non-zero engagement score once Signal Score populates, even accounts with no event attendance. The `icp-score-automation.py` script is updated to read `abm_signal_score` as the engagement input.

**Update trigger:** ICP v3 scoring runs quarterly or on-demand. After Signal Engine launches, run an ad-hoc ICP refresh to reflect new engagement data.

### Job Change Detection

Apollo enriches 10,500 contacts weekly. When `jobtitle` changes between enrichment runs:

1. Workflow or script detects title change (compare `jobtitle` to stored `previous_jobtitle` snapshot)
2. New title evaluated: does it match an ICP-relevant persona? (Demand Gen, Digital Marketing, Marketing, Brand, MarTech)
3. If yes AND contact is at a Tier I/II account: Slack alert to AE — "Champion moved! [Contact] is now [New Title] at [Company]. Previously [Old Title]."
4. If the contact CHANGED COMPANIES: even higher signal — they are a potential warm intro at their new company

**Implementation:** Add a `previous_jobtitle` contact property. Before Apollo enrichment runs, snapshot current titles. After enrichment, diff against snapshot. This can be a pre/post step in the existing enrichment automation or a separate scheduled script.

### Attribution Reporting

New dashboard tracking the signal → pipeline conversion chain:

| Metric                        | Definition                                                                           | Target                        |
| ----------------------------- | ------------------------------------------------------------------------------------ | ----------------------------- |
| Signal-to-Aware conversion    | % of signal-touched accounts that reach Aware stage                                  | Baseline TBD (first quarter)  |
| Aware-to-IPM conversion       | % of Aware+ accounts that generate an IPM within 90 days                             | 15% (target)                  |
| Signal-attributed pipeline    | Total pipeline value from deals where account was Aware+ before deal creation        | Track from Week 1             |
| Signal-attributed wins        | Closed Won revenue where account passed through signal pipeline                      | Track (expect 6-12 month lag) |
| Visitor-to-contact conversion | % of visitor-identified companies that become known contacts with Lead Status > Cold | 10-20% (industry benchmark)   |

---

## Recycling Map: 16 Existing Assets → ABM Components

| #   | Existing Asset                       | Current Use               | ABM Function                                                 | Modification Needed             |
| --- | ------------------------------------ | ------------------------- | ------------------------------------------------------------ | ------------------------------- |
| 1   | Lead Status (5 values)               | Contact outreach tracking | Contact-level awareness proxy → feeds Signal Score (30%)     | Add numeric conversion workflow |
| 2   | Lifecycle Stages (9 values)          | Funnel position           | Gate triggers for routing rules                              | None                            |
| 3   | Event Attendance (4,464 records)     | Event tracking            | Engagement signal → feeds Signal Score (20%)                 | None (read existing data)       |
| 4   | ICP v3 (8 properties)                | Account prioritization    | Tier routing backbone (determines activation playbook)       | Update engagement pillar input  |
| 5   | Persona workflows (8 personas)       | Contact classification    | Buying committee intelligence + visitor classification       | None                            |
| 6   | Seniority workflows (9 levels)       | Contact classification    | Authority scoring (VP+ = 2x weight) + visitor classification | None                            |
| 7   | 10 Hygiene Tags                      | Deal health monitoring    | Negative pipeline signals (3+ tags = suppress)               | None                            |
| 8   | Pipeline Score (0-100)               | Deal quality scoring      | Deal health input to Signal Score                            | None                            |
| 9   | Buying Roles (11 roles)              | Contact categorization    | Multi-threading depth signal                                 | None                            |
| 10  | RSVP Workflow (ID 1819563370)        | Event intake + Slack      | Template for signal routing (Slack pattern)                  | Clone for ABM alerts            |
| 11  | Apollo Weekly Enrichment             | Data freshness            | Job change detection (title diff)                            | Add pre/post snapshot           |
| 12  | Enrichment Tracking (source + date)  | Audit trail               | Data freshness signal (>90 days = stale)                     | None                            |
| 13  | Territory Assignment                 | Account ownership         | Signal routing destinations                                  | None                            |
| 14  | Forecast Categories (5 values)       | Revenue forecasting       | Alert suppression (Commit/Closed = suppress)                 | None                            |
| 15  | Parent-Child Associations (6 active) | Corporate hierarchy       | Cross-account signal propagation                             | None                            |
| 16  | Persona + Seniority Workflows        | Auto-classification       | Real-time visitor classification                             | None                            |

**Net-new build:** 3 properties, 1 numeric conversion workflow, 1 Signal Score computation (script or workflow), 3 routing workflows, 1 job change detection workflow/script, visitor ID integration, 2 dashboards.

---

## Phased Timeline (10-12 Weeks)

### Phase 0: Prerequisites (Week 0 — before build starts)

- [x] Confirm HubSpot Operations Hub tier → **No Operations Hub.** Architecture uses external Python script (6-hour cron). Upgrade path documented.
- [ ] Resolve CRM Ownership cleanup status with Jason Lee (prerequisite for routing accuracy)
- [ ] Get Knotch website traffic volume (determines visitor ID vendor pricing)
- [ ] Privacy review: confirm visitor ID tool compliance with Knotch's customer geography (GDPR/CCPA)

### Phase 1: Foundation (Weeks 1-4)

Build the score, the stage, and the routing.

| Week | Deliverable                                                                                                                                                                                                               |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Create 3 new company properties (`abm_awareness_stage`, `abm_signal_score`, `abm_signal_last_updated`). Create `lead_status_numeric` contact property + conversion workflow. Create `previous_jobtitle` contact property. |
| 2    | Build Signal Score computation script (Python, modeled on `icp-score-automation.py`). Configure 6-hour cron. Test against 100 accounts with known signal profiles.                                                        |
| 3    | Build Awareness Stage updater workflow. Build Signal→Slack routing workflow (Tier I alerts). Test end-to-end: signal change → score update → stage transition → Slack alert.                                              |
| 4    | Build weekly Signal Digest workflow (Tier II). Build Account Signal Dashboard. Run full Signal Score computation across all 1,092 tiered accounts. QA: validate scores against manual assessment of 20 accounts.          |

### Phase 2: Integration (Weeks 5-8)

Add external signal sources and activation sequences.

| Week | Deliverable                                                                                                                                                         |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 5    | Visitor ID vendor selected, contract signed, HubSpot integration configured. Quality filters implemented (2+ pages, 30+ seconds, domain exclusions).                |
| 6    | Visitor ID live. Test: confirm persona/seniority workflows fire on visitor-created contacts. Confirm quality filters gate Signal Score correctly.                   |
| 7    | Build Job Change Detection (pre/post Apollo snapshot + diff logic). Build 3-tier activation sequences (Tier I manual, Tier II auto-nurture, Tier III content drip). |
| 8    | Integration testing: all signal sources → Signal Score → Awareness Stage → routing → activation. Fix edge cases.                                                    |

### Phase 3: Intelligence (Weeks 9-12)

Connect ABM data to ICP scoring and attribution.

| Week | Deliverable                                                                                                                         |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 9    | Update `icp-score-automation.py` to read `abm_signal_score` as engagement input. Run ad-hoc ICP v3 refresh. Validate score changes. |
| 10   | Build Attribution Dashboard (signal → IPM → deal chain). Define measurement framework and targets.                                  |
| 11   | Rep training: walkthrough of Signal Dashboard, Slack alerts, and activation playbooks. Feedback collection.                         |
| 12   | First Signal Review: assess data quality, alert volume, false positive rate. Tune thresholds. Document ops runbook.                 |

### Ongoing (Post-Launch)

- Weekly: Monitor alert volume and rep response rates (target: >60% of Tier I alerts get rep action within 48 hours)
- Monthly: QA 20 Signal Scores against manual assessment. Tune weights if needed.
- Quarterly: Rebalance Signal Score weights based on data coverage changes. Re-run ICP v3 scoring.
- 6-month gate: Review signal-to-IPM conversion. If <10% of Aware+ accounts convert, revisit signal sources and thresholds. If visitor ID tool conversion is below 5%, evaluate kill criteria.
- Ops budget: 2-4 hours/week ongoing maintenance

---

## Prior Art

| Source                                                           | Disposition                                                                                                                                         |
| ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Growth Unhinged ABM framework (7 steps + 13-step signal process) | Adapted — Knotch's small TAM and existing HubSpot infrastructure make several steps redundant (TAM mapping done, CRM cleanup done via hygiene tags) |
| ICP v3 scoring model and script (`icp-score-automation.py`)      | Extended — Signal Score feeds into engagement pillar, script updated as template for Signal Score computation                                       |
| RSVP workflow (ID 1819563370)                                    | Cloned — Slack notification pattern reused for Signal routing                                                                                       |
| Event Attendance backfill (4,464 records)                        | Recycled — becomes primary engagement signal source                                                                                                 |

---

## Risks & Validated Dimensions

### Validated (stress test PASS)

| Dimension           | Finding                                                                                       |
| ------------------- | --------------------------------------------------------------------------------------------- |
| **Scale**           | 1,702 accounts is well within HubSpot capacity. Architecture holds to 3,500+ accounts.        |
| **Asset recycling** | 16 existing assets map cleanly to ABM functions. No replacements needed.                      |
| **ROI math**        | Conservative (1-2 deals) at $140K ACV produces 6-15x return against $12-24K annual tool cost. |

### Mitigated risks (stress test CONDITIONAL)

| Risk                                   | Mitigation                                                                                                                                                                       |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No Operations Hub                      | External Python script (6-hour cron) replaces real-time workflow. Acceptable latency for weekly review cadence. Upgrade path documented.                                         |
| CRM Ownership cleanup blocking routing | Phase 0 prerequisite. Signal Score + Awareness Stage can ship without it; routing cannot.                                                                                        |
| Event data coverage (83% at zero)      | Rebalanced weights: Event Attendance at 20% (not 40%) at launch. Increases as coverage grows.                                                                                    |
| Visitor ID noise                       | Quality filters: 2+ pages, 30+ seconds, domain exclusions. Below-threshold contacts do not feed signals.                                                                         |
| Alert fatigue                          | Tier-based throttling: max 1 alert/account/7 days (Tier I), weekly digest (Tier II), no alerts (Tier III).                                                                       |
| Stale Awareness Stages                 | 90-day decay logic: Active → Engaged → Aware after 90 days of no new signals.                                                                                                    |
| Rep adoption                           | Training week (Week 11). First Signal Review (Week 12). Threshold tuning based on feedback.                                                                                      |
| Privacy/compliance                     | Phase 0 prerequisite: privacy review before visitor ID procurement.                                                                                                              |
| Score gaming                           | Signal Score is computed from system-generated data (Lead Status, events, activity), not rep-entered fields. Contact creation alone does not increment score without engagement. |

### Accepted trade-offs

| Trade-off                                | Rationale                                                                                      |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------- |
| No third-party intent data (Bombora, G2) | Deferred to Approach C. Prove signal-to-IPM conversion with owned data first.                  |
| No ad platform integration               | Deferred to Approach C. Manual audience uploads viable at 1,702 accounts.                      |
| No multi-touch attribution model         | Simple first-touch signal attribution in Phase 3. Full attribution requires 6+ months of data. |
| External script vs. real-time workflow   | Acceptable latency (6-hour refresh if script-based) given weekly sales review cadence.         |

---

## Kill Criteria

If after 6 months of operation:

- Signal-to-IPM conversion < 5% of Aware+ accounts → reassess signal sources and thresholds
- Visitor ID tool conversion (visitor → known contact with engagement) < 3% → cancel visitor ID subscription
- Rep alert response rate < 30% → alerts are noise, redesign activation model
- Zero signal-attributed closed-won deals → ABM motion is not driving revenue, pause and analyze

---

## Operations Hub Upgrade Path

Knotch currently runs Sales Hub Enterprise without Operations Hub. The Signal Engine is designed to work without it using external scripts. If Knotch adds Operations Hub in the future, here is what it unlocks:

### What Operations Hub Adds

| Tier             | Monthly Cost | Key ABM Capabilities                                                       |
| ---------------- | ------------ | -------------------------------------------------------------------------- |
| **Professional** | ~$800/mo     | Custom code actions in workflows, data sync, data quality automation       |
| **Enterprise**   | ~$2,000/mo   | Everything in Pro + advanced data quality, datasets, calculated properties |

### Specific Signal Engine Upgrades with Operations Hub

**1. Real-Time Signal Score (replaces 6-hour cron script)**

Custom code actions let you run JavaScript inside HubSpot workflows. The Signal Score computation moves from an external Python script to a workflow that fires on property changes:

- Trigger: any contact's Lead Status changes, Event Attendance record created, deal stage changes, or new contact associated to company
- Custom code action: reads associated contacts, events, and deals; computes weighted score; writes to company properties
- Result: Signal Score updates in seconds instead of every 6 hours

**2. Real-Time Awareness Stage Transitions**

With custom code, the Awareness Stage workflow can evaluate Signal Score immediately after it updates and transition the stage in the same workflow execution. This creates a true event-driven pipeline:

```
Signal event → Score recomputation → Stage transition → Slack alert
(all within one workflow execution, <30 seconds end-to-end)
```

**3. Data Quality Automation**

Operations Hub Professional includes automated data quality tools:

- Auto-fix formatting issues (capitalization, phone formats) before they enter the Signal Score
- Deduplicate contacts automatically (reduces noise in contact count signal)
- Property validation rules (e.g., `abm_signal_score` must be 0-100)

**4. Programmable Automation (Webhooks + Custom Code)**

- Webhook triggers from visitor ID tools (RB2B/Warmly) can fire HubSpot workflows directly, eliminating the need for native integrations
- Custom code actions can call external APIs (e.g., query Apollo for enrichment data) within workflows
- Enables complex branching logic that exceeds standard workflow capabilities

### Migration Path

If Operations Hub is added:

1. Create new company-based workflow with custom code action containing the Signal Score logic
2. Port the Python computation logic to JavaScript (same algorithm, different language)
3. Set trigger to fire on: contact Lead Status change, Event Attendance creation, deal stage change
4. Run parallel with the cron script for 2 weeks to validate parity
5. Once validated, disable the cron script and remove the scheduled job
6. Update this design doc to reflect the new architecture

**Recommendation:** Operations Hub is not needed for the initial build. Evaluate after 6 months of Signal Engine operation. If the 6-hour latency proves to be a real business limitation (e.g., reps are missing time-sensitive signals), the ROI case for Operations Hub writes itself. At $800/mo Professional, it is roughly equal to the visitor ID tool cost.

---

## Measurement Framework (Leading Indicators)

Track from Week 1 to validate before lagging revenue metrics are available:

| Metric                       | Measurement                                           | First Quarter Target   |
| ---------------------------- | ----------------------------------------------------- | ---------------------- |
| Awareness Stage distribution | % of 1,092 tiered accounts at each stage              | >40% move past Unaware |
| Signal Score coverage        | % of accounts with non-zero score                     | >80%                   |
| Alert volume (Tier I)        | Alerts fired per week                                 | 5-15 (sweet spot)      |
| Alert action rate            | % of Tier I alerts with rep follow-up within 48 hours | >60%                   |
| Visitor-to-contact rate      | Identified visitors → HubSpot contacts                | Baseline TBD           |
| Job change detection hits    | Title changes detected per enrichment cycle           | Baseline TBD           |
| ICP engagement gap closure   | % of accounts scoring >0 on engagement pillar         | >50% (up from 17%)     |

---

## Cost Summary

| Item                             | Monthly          | Annual             | Notes                                                          |
| -------------------------------- | ---------------- | ------------------ | -------------------------------------------------------------- |
| Website visitor ID (RB2B/Warmly) | $500-1,000       | $6,000-12,000      | Pricing depends on traffic volume — confirm before procurement |
| HubSpot (existing)               | $0 incremental   | $0                 | Sales Hub Enterprise already licensed                          |
| Apollo (existing)                | $0 incremental   | $0                 | Weekly enrichment already running                              |
| Ops maintenance                  | 2-4 hrs/week     | ~$10,000-15,000    | At RevOps fractional rate                                      |
| **Total**                        | **$1,000-1,500** | **$16,000-27,000** | Plus one-time build (covered by engagement)                    |

**ROI at 1 incremental deal:** $140K / $27K = 5.2x
**ROI at 2 incremental deals:** $280K / $27K = 10.4x

---

## Related Documents

- `Enablement/01-Knotch-GTM-Overview.md` — Business context, revenue model, ICP
- `Enablement/02-CRM-Architecture-and-Standards.md` — Object model, properties, pipeline structure
- `Enablement/04-Pipeline-Hygiene-and-Scoring.md` — Hygiene tags and pipeline score methodology
- `Enablement/06-Territory-and-ICP-Tiering.md` — Territory assignment, tier distribution
- `Enablement/07-Data-Enrichment-Playbook.md` — Apollo enrichment, field mappings
- `Enablement/09-Workflow-Automation-Reference.md` — Existing workflows being recycled
- `Documentation/CRM/ICP-Scoring-Model-v3.md` — Four-pillar scoring model
- Growth Unhinged: "How to Build a Modern ABM Engine" — Framework reference
