# Workflow Automation Reference

**Effective Date:** March 2026
**Audience:** Sales, Marketing, Revenue Ops, HubSpot Admins
**Purpose:** Complete reference for all automated workflows, trigger logic, and expected behavior

---

## Executive Summary

HubSpot workflows automate contact classification, enrichment tracking, and deal hygiene to reduce manual data entry and ensure consistent naming conventions. This playbook documents all active workflows, their branches, accuracy rates, and troubleshooting steps.

**Scope:** 4 core workflow families

1. Persona Auto-Assignment
2. Seniority Auto-Assignment
3. Enrichment Tracking
4. SPICED Gate Validation + Deal Pipeline Hygiene

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
3. Optional: Set `enrichment_status` = "Complete"

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

## SPICED Gate Validation Workflows

**Type:** Deal-based
**Trigger:** Deal stage transition
**Action:** Validate prerequisite fields and conditionally advance or block progression
**Result:** Enforces sales discipline and deal hygiene

---

### Gate 1: IPM → Qualification

**Prerequisite Fields (all must be true):**

- [ ] `hs_spiced_situation` is not empty (qualitative description of customer situation)
- [ ] `hs_spiced_pain` is not empty (key pain point identified)
- [ ] Deal has ≥1 contact associated with buying role (`hs_persona` ∈ [persona_1, persona_2, persona_3, persona_6, persona_9])

**If All Prerequisites Met:**

- Advance deal to Qualification stage
- Set `gate_1_passed` = true
- Set `gate_1_passed_date` = today

**If Prerequisites NOT Met:**

- Revert deal to IPM stage
- Log activity: "Gate 1 validation failed: missing SPICED or contact role"
- Notify AE in Slack (optional): "@[AE Name] Deal [deal name] missing SPICED documentation or buying committee member"

**Example Scenario:**

- AE moves deal "Acme Inc" from IPM to Qualification
- Workflow checks: Situation? ✓ Pain? ✓ Buying role contact? ✗ (only coordinators associated)
- Workflow reverts to IPM, sends notification
- AE adds contact "CMO, Acme" to deal, re-moves to Qualification
- Gate 1 now passes ✓

---

### Gate 2: Qualification → Consensus

**Prerequisite Fields (all must be true):**

- [ ] Complete SPICED documentation: Situation ✓, Pain ✓, Impact ✓, Consequences ✓, Economic buyer identified ✓
- [ ] Deal has ≥2 contacts with buying roles (`hs_persona` ∈ [persona_1, persona_2, persona_3, persona_6, persona_9])
- [ ] Champion identified (contact tagged as persona_1 OR persona_9, flagged `is_champion` = true)
- [ ] `budget_confirmed` = true (AE documents approval or estimated budget)

**If All Prerequisites Met:**

- Advance deal to Consensus stage
- Set `gate_2_passed` = true
- Set `gate_2_passed_date` = today
- Create Slack alert: "Deal [name] advanced to Consensus (2+ contacts, champion confirmed)"

**If Prerequisites NOT Met:**

- Revert to Qualification
- Log activity: "Gate 2 validation failed: SPICED incomplete, <2 contacts, or no champion"
- List missing fields in activity log

**Example Scenario:**

- AE moves "Acme Inc" from Qualification to Consensus
- Workflow checks:
  - Full SPICED? ✓
  - 2+ buying roles? CMO + VP Content = ✓
  - Champion? VP Content = ✓
  - Budget? Not yet = ✗
- Gate 2 fails; revert to Qualification with note: "Budget not confirmed"
- AE documents "$50k approved budget Q2" in deal, re-advances
- Gate 2 now passes ✓

---

### Gate 3: Consensus → Proposal

**Prerequisite Fields (all must be true):**

- [ ] Economic buyer actively engaged (contact tagged persona_9 OR persona_2 with last activity <7 days)
- [ ] Decision criteria documented (`decision_criteria` field populated)
- [ ] Deal has ≥3 unique contacts with buying roles
- [ ] No open objections (`decision_blockers` field is empty or marked "Resolved")

**If All Prerequisites Met:**

- Advance deal to Proposal stage
- Set `gate_3_passed` = true
- Set `gate_3_passed_date` = today
- Create Slack alert: "Deal [name] ready for Proposal (EB engaged, 3 contacts, decision criteria clear)"

**If Prerequisites NOT Met:**

- Revert to Consensus
- Log activity: "Gate 3 validation failed: EB not engaged, decision criteria missing, or <3 contacts"

**Example Scenario:**

- AE moves "Acme Inc" from Consensus to Proposal
- Workflow checks:
  - EB engaged? CMO activity 4 days ago = ✓
  - Decision criteria? "Reduce lead cost + integrate with HubSpot" = ✓
  - 3+ contacts? CMO + VP Content + Marketing Ops = ✓
  - Open blockers? "Pricing approval pending" = ✗
- Gate 3 fails; revert to Consensus
- AE resolves pricing objection, marks blocker as "Resolved"
- Re-advances to Proposal; Gate 3 now passes ✓

---

### Gate Field Reference

| Field                      | Type         | Required For | Example                                                                                                  |
| -------------------------- | ------------ | ------------ | -------------------------------------------------------------------------------------------------------- |
| `hs_spiced_situation`      | Text         | Gate 1+      | "Acme manages 12 brands with disparate content calendars; no centralized intelligence."                  |
| `hs_spiced_pain`           | Text         | Gate 1+      | "Marketing team spends 30% of time on manual competitive research instead of strategy."                  |
| `hs_spiced_impact`         | Text         | Gate 2+      | "If unresolved: $500k annually in lost efficiency; delayed campaign launches; competitive response lag." |
| `hs_spiced_consequences`   | Text         | Gate 2+      | "Resolved: 20% time savings, 2-week faster campaign launches, real-time competitive visibility."         |
| `hs_spiced_economic_buyer` | Contact Link | Gate 2+      | CMO (link to contact record)                                                                             |
| `champion_contact`         | Contact Link | Gate 2+      | VP Content (link to contact record)                                                                      |
| `budget_confirmed`         | Boolean      | Gate 2+      | true                                                                                                     |
| `decision_criteria`        | Text         | Gate 3+      | "Reduce lead acquisition cost to <$150; integrate with HubSpot; customer success support."               |
| `decision_blockers`        | Text         | Gate 3+      | "Pricing approval pending CEO sign-off" (or "Resolved" / empty)                                          |

---

## Deal Pipeline Hygiene Tag Automation

**Type:** Deal-based
**Trigger:** Deal conditions change (stage, contact count, last activity, etc.)
**Action:** Auto-apply/remove tags based on conditions
**Manual Management:** None required (fully automated)

---

### Hygiene Tags & Auto-Apply Rules

| Tag Name                    | Apply Condition                                           | Clear Condition                      |
| --------------------------- | --------------------------------------------------------- | ------------------------------------ |
| `stale_lead`                | No contact activity >21 days + deal age >30 days          | Last contact activity ≤7 days        |
| `no_buying_committee`       | 0 contacts with buying role personas                      | 1+ contact with buying role assigned |
| `budget_not_confirmed`      | `budget_confirmed` = false and deal in Qualification+     | `budget_confirmed` = true            |
| `missing_spiced_situation`  | Deal in Qualification+ AND `hs_spiced_situation` is empty | `hs_spiced_situation` populated      |
| `missing_spiced_pain`       | Deal in Qualification+ AND `hs_spiced_pain` is empty      | `hs_spiced_pain` populated           |
| `missing_decision_criteria` | Deal in Consensus+ AND `decision_criteria` is empty       | `decision_criteria` populated        |
| `eb_not_engaged`            | Deal in Consensus+ AND EB last activity >14 days          | EB activity ≤7 days                  |
| `single_contact`            | Deal has 1 contact only                                   | Deal has 2+ contacts                 |

---

### Tag Auto-Lifecycle Example

**Scenario: New deal "Acme Inc" created in IPM stage**

| Event                                       | Tags Applied                                              | Tags Removed          | Reason                             |
| ------------------------------------------- | --------------------------------------------------------- | --------------------- | ---------------------------------- |
| Deal created, 0 contacts                    | `no_buying_committee`, `single_contact`                   | —                     | No contacts assigned yet           |
| CMO contact added                           | ✓ `no_buying_committee` removed                           | `no_buying_committee` | 1 buying role contact now assigned |
| Deal moved to Qualification, SPICED missing | `missing_spiced_situation`, `missing_spiced_pain` added   | —                     | Gate validation requires these     |
| AE documents Situation + Pain               | `missing_spiced_situation`, `missing_spiced_pain` removed | —                     | Fields populated by AE             |
| 14 days pass, no EB activity                | `eb_not_engaged` applied                                  | —                     | EB (CMO) last activity >14d        |
| AE calls CMO (activity logged)              | ✓ `eb_not_engaged` removed                                | `eb_not_engaged`      | Recent EB activity logged          |
| Deal moves to Closed/Won                    | All tags removed                                          | (all)                 | Lifecycle complete                 |

---

### Tag Reporting

**Hygiene Dashboard Query (HubSpot Reports):**

- Filter: All open deals with tag = `stale_lead`
- Insight: Which deals are at risk? (>21 days inactive)
- Action: AE outreach or archive

**Sample Report Output:**

```
Tag: stale_lead
Count: 12 deals
Total pipeline value: $450k
Last activity: 25-45 days ago
AE action needed: Check-in call or archival
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

**Issue 3: SPICED gates blocking valid progression**

- **Root Cause:** Required field empty (e.g., `budget_confirmed` not set even though AE discussed budget)
- **Solution:** AE explicitly sets field value; workflow re-evaluates and advances
- **Prevention:** Train AEs on field names and gate requirements; use pre-deal-creation checklist

**Issue 4: Enrichment tracking not triggering**

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
- [ ] SPICED Gate 1: IPM > Qualification (Situation, Pain, 1 role required)
- [ ] SPICED Gate 2: Qualification > Consensus (Full SPICED, 2 roles, champion, budget required)
- [ ] SPICED Gate 3: Consensus > Proposal (EB engaged, decision criteria, 3 roles, no blockers required)
- [ ] Hygiene tags (9 total): Auto-apply/remove rules configured
- [ ] QA audit: Sample 100 records across all workflows; document accuracy
- [ ] Slack notifications: Gate failures and milestone advances (optional)
- [ ] Documentation: Posted in HubSpot resources and Knotch docs site

---

**Questions?** Reach out to Ops. Last updated: March 2026.
