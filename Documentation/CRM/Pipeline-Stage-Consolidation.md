# New Business Pipeline: Stage Consolidation

**Date:** 2026-03-30
**Status:** Executed -- 2026-05-01
**Applies to:** New / Expansion pipeline only (Renewal pipeline unchanged)

---

## The Change

Collapse **IPM Set** and **IPM Held** into a single **IPM** stage. Everything from Qualification forward stays the same.

**Before:** IPM Set → IPM Held → Qualification → Consensus → Proposal → Procurement → Closed Won/Lost

**After:** IPM → Qualification → Consensus → Proposal → Procurement → Closed Won/Lost

---

## Why

Two IPM stages creates ambiguity and slows down pipeline velocity. The real question coming out of a first meeting is binary: am I going to spend time on this in the next 6 weeks, or not? One stage, one decision, one gate.

---

## How IPM Works Now

**A deal enters IPM when:**

- There is interest from the right person (proper persona, not "Other")
- A meeting is on the books

**HubSpot required actions at deal creation:**

- Create contact if not already in HubSpot
- Create deal (New/Expansion pipeline, stage = IPM)
- Select deal type
- Select deal owner
- Associate to contact
- Buyer group created (minimum 1 person)

**What happens in IPM:**

- The first meeting takes place
- Rep captures Situation and Pain (SPICED)

**The exit question:** _Am I going to spend time on this in the next 6 weeks?_

- **Yes** → Move to Qualification. Pain identified, coach or champion identified, follow-up meeting set.
- **No** → Close Lost.

**Timeline:** 24 hours ideal. Up to 1 week max. No deal should sit in IPM longer than 7 days after the first meeting.

---

## Two Key Dates

| Date Field             | Source                                                                     | Description                                           |
| ---------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------- |
| **First Meeting Date** | Auto-populated from HubSpot meetings tool                                  | Date the first meeting on this deal actually occurred |
| **Qualification Date** | Auto-populated when deal exits IPM (moves to Qualification or Closed Lost) | Timestamp of the stage change                         |

Both fields are overridable if the auto-populated value is wrong.

**Metric this unlocks:** Time-to-qualify = Qualification Date minus First Meeting Date. Target: under 7 days.

---

## IPM Credit Rules

| Scenario                                                              | Counts as IPM?     | Kicker Eligible? | HubSpot Requirement                       |
| --------------------------------------------------------------------- | ------------------ | ---------------- | ----------------------------------------- |
| First meeting with anyone at an account (proper persona, not "Other") | Yes -- Account IPM | Yes              | Buyer role filled on contact              |
| Net-new Executive Sponsor added to any deal on that account           | Yes -- Deal IPM    | Yes              | Buyer role = Executive Sponsor on contact |
| Second meeting with same contact                                      | No                 | No               | --                                        |
| Meeting with non-executive at an account that already has an IPM      | No                 | No               | --                                        |

**Account IPM:** Manual tag — the rep stamps `ipm_held` on the deal. Guidance: this should be a new buyer group at the account, or 12+ months since the last engagement with the same buyer group. The rep can override the 12-month rule if the contacts are genuinely new to HubSpot (e.g., completely different people at the same company).

**Deal IPM (Secondary Executive IPM):** Automated via workflow. Awarded when a net-new Executive Sponsor has their first completed meeting on a deal where the initial IPM was already held. The buyer role must be set to Executive Sponsor **before the meeting is marked complete** — if tagged after, the workflow has already fired and exited. No retroactive credit. This is intentional discipline enforcement.

**Hard rule for both:** Buyer role MUST be updated on the contact in HubSpot. No buyer role = no IPM credit. This is the enforcement gate. For Deal IPM specifically, the timing matters — tag the role before completing the meeting.

---

## Stages After IPM (Unchanged Structure, Updated Gates)

### Qualification (Stage 1) -- Pipeline, 10%

**Entrance gate:** Previous stage exit gates met

**Exit gate:**

- Demo has been given to key and/or additional stakeholders
- Champion is aligned on the Impact of Knotch
- Champion names the additional stakeholders and commits to recommending Knotch to them

**HubSpot required actions:**

- Additional stakeholders added as contacts and associated to deal
- Buyer group: 3+ people
- Amount and Close Date set
- Official deal name: Company Name - Product(s) Contract Year(s), Deal Type
- SPICED: 50% complete (Situation, Pain, Impact captured)

**SPICED focus:** Impact

---

### Consensus (Stage 2) -- Pipeline, 25%

**Entrance gate:** Previous stage exit gates met

**Exit gate:**

- Champion validates that consensus is reached to proceed with a formal proposal
- Initial MAP created (action plan on next steps with clients) with Champion
- Proposal review meeting is scheduled
- Business case sent to key stakeholders

**HubSpot required actions:**

- Draft MAP in HubSpot
- SPICED: 100% complete
- Buyer group: Economic Decision Maker identified
- Proposal uploaded
- All stakeholders identified, mapped, and blockers identified

**SPICED focus:** Critical Event, Decision Criteria

---

### Proposal & Biz Case Review (Stage 3) -- Best Case, 50%

**Entrance gate:** Previous stage exit gates met

**Exit gate:**

- MAP is agreed to by Champion
- Budget confirmed by Champion
- Verbal received on scope and deliverables from Champion
- SOW and MSA sent

**HubSpot required actions:**

- SOW uploaded
- MAP uploaded
- Buyer group: 1+ Legal & Procurement contacts identified
- Onboarding & testing plan developed

**SPICED focus:** Buyer Group Consensus, Verbal, SOW Sent

---

### Procurement (Stage 4) -- Commit, 90%

**Entrance gate:** Previous stage exit gates met

**Exit gate:**

- In contact with procurement, working through legal, info/sec, finance, and any other internal approval processes
- Legal approval
- Info/sec clearance
- Finance approval
- Signer identified
- Vendor onboarding complete (invoice instructions)

**HubSpot required actions:**

- All documents uploaded
- MSA finalized
- Addendums (asked, not required)
- S&E date set
- 2 meeting dates scheduled

---

### Closed Won -- 100%

**Entrance gate:** Previous stage exit gates met

**Required actions:**

- Add contract start and end date per SOW
- Upload signed docs
- Handover document completed in HubSpot

**Post-close:** Schedule internal hand over, IPM identification for cross-sell, external business and technical kick-offs

---

### Closed Lost

**Required actions:**

- Close reason captured
- Month deal was moved to Closed Lost recorded

---

## Buyer Group Requirements by Stage (Summary)

| Stage         | Minimum Buyer Group Size | Key Roles Required                  |
| ------------- | ------------------------ | ----------------------------------- |
| IPM           | 1 person                 | Any proper persona                  |
| Qualification | 3+ people                | Coach or Champion identified        |
| Consensus     | 3+ people                | Economic Decision Maker identified  |
| Proposal      | 3+ people                | Legal & Procurement (1+) identified |
| Procurement   | Full committee           | All stakeholders mapped             |

---

## Implementation Checklist

- [x] Delete or deactivate IPM Held stage in HubSpot (QA that existing deals don't break)
- [x] Rename IPM Set to "IPM" (or create new stage and migrate)
- [x] Create "First Meeting Date" deal property (date type, auto-populated from meetings)
- [x] Delete `ipm_scheduled` (IPM Set On) property — deleted 2026-05-27, backup at `Archive/ipm_scheduled_backup_2026-05-27.csv`
- [ ] Create "Qualification Date" deal property (date type, auto-populated on stage exit)
- [ ] Update deal hygiene workflows to reflect single IPM stage
- [ ] Update deal hygiene tags/dashboard for new stage structure
- [ ] Update IPM credit tracking to reflect Account IPM vs. Deal IPM logic
- [ ] Build workflow: flag deals in IPM for 7+ days after first meeting date
- [ ] QA: ensure no existing deals are orphaned by stage removal
- [ ] Update Enablement docs (seller quick reference, CRM expectations)

---

## Open Questions for Team Discussion

1. **IPM Held cleanup:** How many deals are currently in IPM Held? Do we migrate them all to IPM, or force reps to qualify/kill them as part of the cutover?
2. **Executive definition for Deal IPM:** Is "Executive Sponsor" the only buyer role that earns an additional IPM, or does Economic Buyer count too?
3. **7-day enforcement:** Hard block (auto-flag/auto-close) or soft nudge (hygiene dashboard tag)?
4. **First Meeting Date automation:** Does HubSpot's meetings tool reliably capture this, or do we need a fallback (manual entry, workflow-based)?
