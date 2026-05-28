# Workflow Automation Reference

**Audience:** Sales, Marketing, RevOps, Admins | **Topics:** workflow, automation, persona, seniority, deal hygiene, ownership, RSVP | **Last Updated:** May 2026

---

## Executive Summary

HubSpot workflows automate contact classification, enrichment tracking, and deal hygiene to reduce manual data entry and ensure consistent naming conventions. This playbook documents all active workflows, their branches, accuracy rates, and troubleshooting steps.

**Scope:** 4 core workflow families

1. Persona Auto-Assignment
2. Seniority Auto-Assignment
3. Enrichment Tracking
4. Deal Pipeline Hygiene

---

## Persona Auto-Assignment Workflow

**Type:** Contact-based
**Trigger:** `jobtitle` field populated or changed
**Action:** Set `hs_persona` property based on title keywords
**Re-enrollment:** Yes (if title changes, persona re-evaluated)
**Accuracy Rate:** 92.8% match rate vs. full classification logic

---

### Persona Definition & Branches

The workflow uses **13 branches** in priority order. First matching branch wins. If no match, contact receives persona_11 (other).

| Branch # | Condition                                                                                          | Persona    | Personas           |
| -------- | -------------------------------------------------------------------------------------------------- | ---------- | ------------------ |
| **0**    | Title contains "Assistant To"                                                                      | persona_11 | Other (non-buyer)  |
| **1**    | Title contains: legal, counsel, procurement, sourcing, compliance                                  | persona_13 | Legal/Procurement  |
| **2**    | Title contains: finance, FP&A, controller, CFO                                                     | persona_15 | Finance/CFO        |
| **3**    | Title contains: "demand gen" OR "demand generation" OR "demand marketing"                          | persona_1  | Demand Gen         |
| **4**    | Title contains: martech, marketing ops, analytics, data scientist, CRM, software engineer          | persona_6  | MarTech/Technical  |
| **5**    | Title contains: brand strategy, brand marketing, brand manager                                     | persona_10 | Brand              |
| **6**    | Title contains digital compound (digital marketing, SEO, SEM, paid media, ecommerce, social media) | persona_3  | Digital Marketing  |
| **7**    | Title contains "digital" (not "chief digital officer" context)                                     | persona_3  | Digital Marketing  |
| **8**    | Title contains: content, editorial, copywriter, growth marketing, campaign, ABM, creative          | persona_1  | Demand Gen/Content |
| **9**    | Title contains: CEO, COO, CTO, CIO, president, founder (NOT CMO)                                   | persona_2  | Executive          |
| **10**   | Title contains: CMO, chief marketing, marketing, communications, PR, advertising, events           | persona_9  | Marketing          |
| **11**   | Catch-all: No prior match                                                                          | persona_11 | Other              |

---

### Persona Reference Map

| Persona ID | Persona Name        | Profile                                                                   |
| ---------- | ------------------- | ------------------------------------------------------------------------- |
| persona_1  | Demand Gen/Content  | Owns lead generation, content strategy, campaign execution                |
| persona_2  | Executive (Non-CMO) | C-Suite or founder (CEO, COO, CTO, CIO, president)                        |
| persona_3  | Digital Marketing   | Owns digital channels, SEO/SEM, digital experience, performance marketing |
| persona_6  | MarTech/Technical   | MarTech stack owner, marketing ops, analytics, engineering                |
| persona_9  | Marketing           | CMO, Head of Marketing, VP Marketing, Chief Communications                |
| persona_10 | Brand               | Brand strategy, brand marketing, brand management                         |
| persona_13 | Legal/Procurement   | Legal, counsel, procurement, sourcing, compliance                         |
| persona_15 | Finance/CFO         | Finance, FP&A, controller, CFO                                            |
| persona_11 | Other               | Non-marketing buyer, support staff, assistant roles                       |

---

### Workflow Branching Logic (Detailed)

**Example Path 1: "VP Demand Generation"**

1. Title contains "demand gen"? → YES, match Branch 3 → persona_1 ✓
2. Workflow stops; no further evaluation

**Example Path 2: "Director, Digital Marketing"**

1. "Assistant To"? → NO
2. Legal/Procurement terms? → NO
3. Finance terms? → NO
4. "demand gen"? → NO
5. MarTech terms? → NO
6. Brand terms? → NO
7. Digital compound terms (digital + marketing)? → YES, match Branch 6 → persona_3 ✓

**Example Path 3: "CMO"**

1. "Assistant To"? → NO
2. Legal/Procurement? → NO
3. Finance? → NO
4. Demand gen? → NO
5. MarTech? → NO
6. Brand? → NO
7. Digital compound? → NO
8. Standalone "digital"? → NO
9. Content/Growth/Campaign/ABM? → NO
10. CEO/CTO/founder (not CMO)? → NO (CMO is excluded from this branch)
11. CMO/chief marketing/marketing/communications? → YES, match Branch 10 → persona_9 ✓

**Example Path 4: "General Counsel"**

1. "Assistant To"? → NO
2. Legal? → YES, match Branch 1 → persona_13 ✓

---

### Accuracy & Testing

**Validation Method:**

- Persona assignments compared against full classification logic (manual review)
- Sample: 1,000 random contact titles
- Accuracy: 92.8% (928 matches, 72 exceptions)

**Common Exceptions (7.2%):**

- Titles with multiple overlapping keywords (e.g., "Director of Content & Digital Marketing" → assigned Digital [persona_3] instead of Content [persona_1]; both valid, workflow picks first match)
- Abbreviated titles (e.g., "Sr. Comms" → might hit marketing branch instead of comms-specific; acceptable false positive)
- Non-English titles or acronyms → defaults to persona_11 (other)

**False Positive Examples:**

- "Chief Digital Officer" tagged as persona_2 (executive) instead of persona_3 (digital) due to branch order
- "Product Manager" not in any branch → persona_11 (other)
- "VP, Content & Demand Gen" → persona_1 (first match), could reasonably be both

**Recommended Manual Review:**

- Before outbound campaigns, spot-check personas of top 100 target accounts
- Flag obvious mismatches for manual correction
- Annual re-validation (test 500 random titles)

---

## Seniority Auto-Assignment Workflow

**Type:** Contact-based
**Trigger:** `jobtitle` field populated or changed
**Action:** Set `hs_seniority` property based on title keywords
**Re-enrollment:** Yes (if title changes, seniority re-evaluated)
**Accuracy Rate:** 99.4% match rate

---

### Seniority Definition & Branches

The workflow uses **11 branches + default** in priority order. First matching branch wins.

| Branch #    | Condition                                                                | Seniority Level | Logic                                  |
| ----------- | ------------------------------------------------------------------------ | --------------- | -------------------------------------- |
| **0**       | Title contains "Assistant To"                                            | entry           | Explicitly junior                      |
| **1**       | Title contains: Chief, CEO, CFO, CTO, CIO (NOT "Editor in Chief")        | executive       | C-level, chief executives              |
| **2**       | Title contains: SVP, SEVP (Senior/Executive Vice President)              | vp              | Senior VP (higher than standard VP)    |
| **3**       | Title contains: EVP, VP, Vice President                                  | vp              | Vice President (all forms)             |
| **4**       | Title contains: President (NOT Vice President)                           | executive       | President-level (executive equivalent) |
| **5**       | Title contains: Owner (NOT Product Owner, Partnerships Owner)            | owner           | Business owner, co-founder             |
| **6**       | Title contains: Director, Head of, Managing Director, Chief of Staff     | director        | Director-level and above               |
| **7**       | Title contains: Partner (NOT Partner Marketing, Partnerships)            | partner         | Business partner, engagement partner   |
| **8**       | Title contains: Senior, Sr., Principal, Lead, Consultant, Advisor        | senior          | Senior individual contributor          |
| **9**       | Title contains: Manager (and no prior match)                             | manager         | First-level manager                    |
| **10**      | Title contains: Coordinator, Specialist, Analyst, Assistant, Intern      | entry           | Entry-level support roles              |
| **11**      | Title contains: Engineer, Developer, Designer, Writer, Editor, Architect | employee        | Individual contributors (IC)           |
| **Default** | No match found                                                           | (blank)         | Leave blank; insufficient data         |

---

### Seniority Reference Map

| Level         | Examples                                             | Authority                  | Role                         |
| ------------- | ---------------------------------------------------- | -------------------------- | ---------------------------- |
| **executive** | CEO, CFO, CTO, President, Founder                    | Full P&L / Board level     | Strategic decision-maker     |
| **vp**        | VP, SVP, EVP, Vice President                         | Department / Business Unit | Senior leader                |
| **director**  | Director, Head of, Managing Director, Chief of Staff | Team / Function            | Manager of managers          |
| **owner**     | Business Owner, Co-founder, Owner                    | Equity stake               | Founder-level                |
| **partner**   | Partner (business), Engagement Partner               | Client / Account level     | Senior advisor               |
| **senior**    | Senior [role], Principal, Lead, Consultant, Advisor  | Technical / expertise      | Expert IC, no formal reports |
| **manager**   | Manager, Team Lead                                   | Team level                 | First-level manager          |
| **employee**  | Engineer, Developer, Designer, Writer, Editor        | Individual contributor     | IC (no reports)              |
| **entry**     | Coordinator, Specialist, Analyst, Assistant, Intern  | Entry/support              | Junior staff                 |

---

### Workflow Branching Logic (Detailed)

**Example Path 1: "Senior Director, Demand Generation"**

1. "Assistant To"? → NO
2. Chief/CEO/CFO/CTO/CIO? → NO
3. SVP/SEVP? → NO
4. EVP/VP/Vice President? → NO
5. President (not VP)? → NO
6. Owner (not Product Owner)? → NO
7. Director? → YES, match Branch 6 → director ✓

**Example Path 2: "SVP, Marketing"**

1. "Assistant To"? → NO
2. Chief/C-level? → NO
3. SVP? → YES, match Branch 2 → vp ✓

**Example Path 3: "Senior Content Strategist"**

1. "Assistant To"? → NO
2. Chief/C-level? → NO
3. SVP? → NO
4. VP? → NO
5. President? → NO
6. Owner? → NO
7. Director/Head of? → NO
8. Partner (business)? → NO
9. Senior? → YES, match Branch 8 → senior ✓

**Example Path 4: "Marketing Manager"**

1. "Assistant To"? → NO
2. Chief/C-level? → NO
3. SVP? → NO
4. VP? → NO
5. President? → NO
6. Owner? → NO
7. Director? → NO
8. Partner? → NO
9. Senior? → NO
10. Manager? → YES, match Branch 9 → manager ✓

**Example Path 5: "Product Manager"**

1. All prior branches → NO
2. Engineer/Developer/Designer/Writer/Editor? → NO
3. No match → Default → (blank) ← Seniority undetermined

---

### Accuracy & Testing

**Validation Method:**

- Seniority assignments compared against manual title parsing
- Sample: 1,000 random contact titles
- Accuracy: 99.4% (994 matches, 6 exceptions)

**Common Exceptions (0.6%):**

- "Chief Product Officer" tagged as executive (branch 1) instead of director (branch 6) — actually correct; CPO is C-level
- "Chief of Staff" tagged as director (branch 6) — correct; Chief of Staff is director-equivalent
- "Engineer" in title but also "VP Engineering" → VP branch wins (correct)
- Titles without clear rank (e.g., "Coordinator, Analytics") → entry level (conservative, correct)

**False Positive Reduction:**

- Branch 5 excludes "Product Owner" and "Partnerships Owner" to avoid tagging non-executives as owners
- Branch 1 excludes "Editor in Chief" to avoid tagging editors as C-suite
- Comprehensive testing shows <1% error rate acceptable for sales ops

---

## Enrichment Tracking Workflows

**Type:** Company-based and Contact-based (parallel)
**Trigger:** `apollo_account_id` field populated (company) OR Apollo enrichment data received
**Action:** Set `enrichment_source` and `last_enrichment_date`
**Re-enrollment:** No (one-time write)

---

### Workflow Logic

**Trigger Condition:**

- Contact: `apollo_account_id` is known (populated by Apollo integration)
- Company: `apollo_account_id` is known (populated by Apollo integration)

**Actions (executed once per record):**

1. Set `enrichment_source` = "Apollo"
2. Set `last_enrichment_date` = current date/time

**Rationale:**

- Provides audit trail of which records were enriched
- Enables quarterly re-enrichment cycles (query on `last_enrichment_date`)
- Differentiates Apollo-enriched from manually-entered data

---

### Enrichment Workflow Example

**Scenario:** New contact imported from Apollo, `apollo_account_id` = "12345abc"

| Field                  | Action            | Value                                   |
| ---------------------- | ----------------- | --------------------------------------- |
| `enrichment_source`    | Set to            | "Apollo"                                |
| `last_enrichment_date` | Set to            | 2026-03-20                              |
| `apollo_account_id`    | Already populated | 12345abc                                |
| `phone`                | Not touched       | (Apollo integration handles separately) |

**Quarterly Re-enrichment Query:**

- Find all contacts where `last_enrichment_date` < 90 days ago
- Re-enroll in Apollo enrichment workflow
- Update `last_enrichment_date` to today

---

## Deal Pipeline Hygiene Tag Automation

**Type:** Deal-based
**Trigger:** Deal conditions change (stage, contact count, last activity, etc.)
**Action:** Auto-apply/remove tags based on conditions
**Manual Management:** None required (fully automated)

---

### Hygiene Tags & Auto-Apply Rules

| Tag Name               | Apply Condition                         | Clear Condition                   |
| ---------------------- | --------------------------------------- | --------------------------------- |
| **No Amount**          | Deal amount is empty                    | Amount populated                  |
| **Stalled**            | Same stage for 45+ days                 | Stage changes                     |
| **Zombie**             | No activity for 45+ days                | Activity logged                   |
| **No Recent Activity** | No activity for 21+ days                | Activity logged                   |
| **No Contacts**        | Zero contacts on deal                   | 1+ contact associated             |
| **Single Threaded**    | One contact at Qualification+ stage     | 2+ contacts associated            |
| **Stale Next Steps**   | Next step date in past                  | Next step date updated to future  |
| **Past-Due Close**     | Close date passed, deal still open      | Close date updated or deal closed |
| **IPM Stale**          | In IPM stage 14+ days without advancing | Deal advances past IPM            |
| **No Line Items**      | Past IPM with no line items attached    | Line items added                  |

---

### Tag Auto-Lifecycle Example

**Scenario: New deal "Acme Inc" created in IPM stage**

| Event                               | Tags Applied                   | Tags Removed           | Reason                              |
| ----------------------------------- | ------------------------------ | ---------------------- | ----------------------------------- |
| Deal created, 0 contacts, no amount | **No Contacts**, **No Amount** | —                      | No contacts or amount yet           |
| CMO contact added                   | —                              | **No Contacts**        | 1 contact now associated            |
| Amount set to $150K                 | —                              | **No Amount**          | Deal amount populated               |
| Deal in IPM for 14+ days            | **IPM Stale** applied          | —                      | IPM stage exceeded 14-day threshold |
| Deal advances to Qualification      | —                              | **IPM Stale**          | No longer in IPM                    |
| 21 days pass, no activity           | **No Recent Activity** applied | —                      | No logged activity for 21+ days     |
| AE calls CMO (activity logged)      | —                              | **No Recent Activity** | Recent activity logged              |
| Deal moves to Closed/Won            | All tags removed               | (all)                  | Lifecycle complete                  |

---

### Tag Reporting

**Hygiene Dashboard Query (HubSpot Reports):**

- Filter: All open deals by hygiene tag (No Recent Activity, Stalled, Zombie, etc.)
- Insight: Which deals need attention?
- Action: AE outreach, update, or archive

**Sample Report Output:**

```
Tag: No Recent Activity
Count: 12 deals
Total pipeline value: $450k
Last activity: 21-44 days ago
AE action needed: Check-in call or update next steps
```

---

## Workflow Monitoring & Troubleshooting

### Common Issues & Resolution

**Issue 1: Persona assignments incorrect for multi-role titles**

- **Root Cause:** Workflow branch order; "Digital Content Manager" matches "Digital" before "Content"
- **Solution:** Manual override for top 100 accounts; accept 7% exception rate as normal
- **Prevention:** Use standardized title format in HubSpot on import

**Issue 2: Seniority blank for non-traditional titles**

- **Root Cause:** Title doesn't match any branch (e.g., "Product Manager" not in workflow)
- **Solution:** Add job title to appropriate branch (requires HubSpot admin) or manually set
- **Prevention:** Standardize job titles on import; run QA on samples

**Issue 3: Enrichment tracking not triggering**

- **Root Cause:** `apollo_account_id` not populated (Apollo integration not working)
- **Solution:** Check Apollo > HubSpot sync status; verify field mapping in Apollo admin
- **Prevention:** Weekly sync monitor; audit integration health monthly

**Issue 5: Tags not clearing despite condition resolved**

- **Root Cause:** Workflow engine caching; tag update delayed by 1-2 hours
- **Solution:** Wait 2 hours or manually clear tag from deal record; workflow will re-apply if condition still true
- **Prevention:** Check tag history in deal record to understand last update timestamp

---

### Workflow Health Checks (Monthly)

| Check                            | Expected Result                                   | Frequency |
| -------------------------------- | ------------------------------------------------- | --------- |
| Persona auto-assignment rate     | >95% of new contacts have persona                 | Weekly    |
| Seniority auto-assignment rate   | >99% of titles yield seniority                    | Weekly    |
| Enrichment tracking success rate | >90% of Apollo enrichments tracked                | Weekly    |
| Gate validation blocks           | <5% of stage transitions blocked (expected range) | Weekly    |
| Hygiene tag accuracy             | Spot-check 10 deals; verify tags match conditions | Monthly   |
| Workflow execution errors        | 0 workflow failures (check HubSpot logs)          | Monthly   |

---

## Training & Documentation

### For Sales Team

- **One-pagers:** Persona definitions (what each persona means)
- **Checklists:** Gate prerequisites (what must be true before advancing stage)
- **Video:** SPICED documentation (how to fill fields correctly)

### For Ops Team

- **HubSpot Admin Training:** Workflow branch logic, field mapping, troubleshooting
- **Monthly Sync:** Discuss issues, plan improvements, review QA audit results

### For Marketing Team

- **Persona Reference:** Use hs_persona for campaign segmentation
- **List Building:** Filter by persona + seniority for targeted campaigns

---

## Appendix: Workflow Configuration Checklist

- [ ] Persona workflow: 11 branches configured, tested on 100 titles
- [ ] Seniority workflow: 11 branches configured, tested on 100 titles
- [ ] Enrichment tracking (company): Trigger on `apollo_account_id`, set metadata fields
- [ ] Enrichment tracking (contact): Trigger on `apollo_account_id`, set metadata fields
- [ ] Hygiene tags (10 total): Auto-apply/remove rules configured
- [ ] QA audit: Sample 100 records across all workflows; document accuracy
- [ ] Slack notifications: Milestone advances (optional)
- [ ] Documentation: Posted in HubSpot resources and Knotch docs site

---

---

## Lead Status Automation (Planned)

**Type:** Contact-based (6 workflows)
**Status:** Pending build (backfill complete — all contacts have lead status populated)
**Full spec:** Documentation/Workflows/Lead-Status-Automation-Plan.md

These workflows enforce lead status hierarchy (statuses only move up: Cold → Attempted → Connected → Meeting Booked → Open Opportunity). Each workflow fires on a CRM event and sets the appropriate status if the contact's current status is lower in the hierarchy.

| Workflow | Trigger              | Sets Status To   | Notes                                       |
| -------- | -------------------- | ---------------- | ------------------------------------------- |
| WF-LS1   | Deal created         | Open Opportunity | Highest progression status                  |
| WF-LS2   | Deal closed won      | Connected        | Maintains relationship status post-close    |
| WF-LS3   | Deal closed lost     | Bad Fit          | Conditional — only if no other active deals |
| WF-LS4   | Meeting created      | Meeting Booked   |                                             |
| WF-LS5   | Sequence enrollment  | Attempted        | Outreach initiated via sequence             |
| WF-LS6   | Email reply received | Connected        | Two-way conversation established            |

---

## Event RSVP Processor Workflow

**Type:** Contact-based
**Workflow:** `WF | Event | RSVP Processor` (ID 1819563370)
**Trigger:** RSVP form submission (any form matching `RSVP | {Event Name}`)
**Actions:** Add to `RSVP | Unprocessed` static list (ID 1775), send Slack notification, route through IF/THEN for event-specific actions (confirmation emails, follow-up tasks)
**Re-enrollment:** Yes (same contact can RSVP to multiple events)

This workflow is the real-time intake for all event RSVPs. The Google Sheet Event Processor handles downstream processing (enrichment, Event Attendance records, list creation). For the full six-step event lifecycle, see Documentation/Events/Event-Lifecycle.md. For the workflow build guide, see Documentation/Events/RSVP-Processor-Workflow-Setup.md.

---

## Related Documents

- **CRM Architecture and Standards** (02) — Object model and properties that workflows act on
- **Pipeline Hygiene and Scoring** (04) — Hygiene tags that workflow enforcement supports
- **Event and Webinar List Management** (14) — RSVP Processor Workflow context and event lists

---

**Questions?** Reach out to Ops.
