# Stage Gate Workflow Plan

**Status:** Revised — standard workflows (no Ops Hub Pro)
**Date:** 2026-05-19
**Pipeline:** New/Expansion (ID: 72018330)
**Properties managed:** `ready_to_advance` (Yes/No), `stage_gap_summary` (textarea)

---

## Overview

A set of standard deal workflows evaluate whether a deal has met the complex requirements for its current stage — things HubSpot's native conditional stage properties can't check (SPICED field counts, contact minimums, line items, amount > 0).

Simple "is this field filled out" checks (documents uploaded, dates set, etc.) stay as **native conditional stage properties**.

Buying role validation (Budget Holder at Proposal, Procurement/Legal at Procurement) is handled by **manual confirmation properties** — standard workflows can't read contact properties from a deal context.

The workflows write two properties:

- **`ready_to_advance`** — Yes when all automated checks pass, No when not. Used as a required conditional stage property.
- **`stage_gap_summary`** ("What's Needed to Advance") — static checklist of what's required at the current stage. Cleared when all automated checks pass.

---

## Scope: Deal Type

| Deal Type                                    | Treatment                                           |
| -------------------------------------------- | --------------------------------------------------- |
| **New License**                              | Full stage gate evaluation (rules below)            |
| **Cross-sell**, **Upsell**                   | Auto-approved: `ready_to_advance` = Yes, clear gaps |
| **Partnership**, **Winback**, **Consulting** | Auto-approved: `ready_to_advance` = Yes, clear gaps |
| **Renewal**                                  | Separate pipeline — not evaluated                   |

---

## What Standard Workflows Can and Cannot Do

| Capability                              | Standard workflow? | Solution                           |
| --------------------------------------- | ------------------ | ---------------------------------- |
| Check SPICED fields empty/not empty     | ✅ Yes             | If/then on deal properties         |
| Check `num_associated_contacts` >= N    | ✅ Yes             | If/then on deal property           |
| Check `hs_num_of_associated_line_items` | ✅ Yes             | If/then on deal property           |
| Check `amount` > 0                      | ✅ Yes             | If/then on deal property           |
| Set `ready_to_advance` Yes/No           | ✅ Yes             | CRM action: set property           |
| Set `stage_gap_summary` text            | ✅ Yes             | CRM action: set property (static)  |
| Check buying roles on contacts          | ❌ No              | Manual confirmation property       |
| Count contacts with specific roles      | ❌ No              | Manual confirmation property       |
| Build dynamic gap text per deal         | ❌ No              | Static checklist per stage instead |
| Sum line items to compare to amount     | ❌ No              | Manual check or deferred           |

---

## Workflow Architecture

**6 workflows total** (one per stage that needs evaluation, plus a cleanup):

| Workflow                            | Trigger stage(s)             | Purpose                                   |
| ----------------------------------- | ---------------------------- | ----------------------------------------- |
| `WF \| Deal \| Gate: Qualification` | Qualification (152455272)    | Check SPICED 2/5, contacts, lines, amount |
| `WF \| Deal \| Gate: Consensus`     | Consensus (138620983)        | Check SPICED 4/5, contacts                |
| `WF \| Deal \| Gate: Proposal`      | Proposal (138620984)         | Check SPICED 5/5, contacts                |
| `WF \| Deal \| Gate: Procurement`   | Procurement (138620985)      | Check contacts                            |
| `WF \| Deal \| Gate: Clear`         | IPM, Closed Won, Closed Lost | Auto-approve or clear properties          |
| `WF \| Deal \| Line Item Balance`   | Any stage (amount/LI change) | Check line items = amount                 |

### Common Pattern (each stage workflow)

```
Enrollment: dealstage = [stage] + re-enroll on property changes
    │
    ▼
Branch: Deal Type = "New License"?
    │
    ├── NO → Set ready_to_advance = Yes, clear stage_gap_summary → END
    │
    └── YES → Check requirements...
         │
         ├── ALL PASS → Set ready_to_advance = Yes, clear stage_gap_summary → END
         │
         └── ANY FAIL → Set ready_to_advance = No, set stage_gap_summary = [stage checklist] → END
```

### Re-enrollment Triggers (per workflow)

Each stage workflow re-enrolls when its relevant properties change:

| Workflow          | Re-enroll on                                                                                                |
| ----------------- | ----------------------------------------------------------------------------------------------------------- |
| Qualification     | `situation`, `pain`, `num_associated_contacts`, `hs_num_of_associated_line_items`, `amount`, `dealtype`     |
| Consensus         | `situation`, `pain`, `impact`, `critical_event`, `num_associated_contacts`, `dealtype`                      |
| Proposal          | `situation`, `pain`, `impact`, `critical_event`, `decision_criteria`, `num_associated_contacts`, `dealtype` |
| Procurement       | `num_associated_contacts`, `dealtype`                                                                       |
| Clear             | `dealtype`                                                                                                  |
| Line Item Balance | `hs_num_of_associated_line_items`, `amount`                                                                 |

---

## Rules by Stage (New License Only)

### IPM

No gate. `ready_to_advance` = Yes. Cleared by the Clear workflow.

Native conditional properties (Deal Type) remain as hard requirements.

### Qualification (Stage 1)

**Automated checks (workflow):**

| #   | Requirement         | Branch condition                       |
| --- | ------------------- | -------------------------------------- |
| 1   | Situation completed | `situation` is known                   |
| 2   | Pain completed      | `pain` is known                        |
| 3   | 1+ contacts         | `num_associated_contacts` >= 1         |
| 4   | Line items exist    | `hs_num_of_associated_line_items` >= 1 |
| 5   | Amount set          | `amount` is known AND > 0              |

**Branch logic:** If ALL 5 pass → Yes. If ANY fail → No + gap text.

**Gap summary (static, shown when any check fails):**

```
To advance from Qualification:
• Complete Situation and Pain in SPICED
• Add at least 1 contact (with buying role set)
• Add product line items
• Set deal amount > $0
```

### Consensus (Stage 2)

**Automated checks (workflow):**

| #   | Requirement         | Branch condition               |
| --- | ------------------- | ------------------------------ |
| 1   | Situation completed | `situation` is known           |
| 2   | Pain completed      | `pain` is known                |
| 3   | Impact completed    | `impact` is known              |
| 4   | Critical Event set  | `critical_event` is known      |
| 5   | 2+ contacts         | `num_associated_contacts` >= 2 |

**Gap summary:**

```
To advance from Consensus:
• Complete Situation, Pain, Impact, and Critical Event in SPICED (4/5)
• Add at least 2 contacts (with buying roles set)
```

### Proposal + Business Case Review (Stage 3)

**Automated checks (workflow):**

| #   | Requirement           | Branch condition               |
| --- | --------------------- | ------------------------------ |
| 1   | Situation completed   | `situation` is known           |
| 2   | Pain completed        | `pain` is known                |
| 3   | Impact completed      | `impact` is known              |
| 4   | Critical Event set    | `critical_event` is known      |
| 5   | Decision Criteria set | `decision_criteria` is known   |
| 6   | 3+ contacts           | `num_associated_contacts` >= 3 |

**Manual checks (native conditional properties):**

| Property                            | What it enforces                                              |
| ----------------------------------- | ------------------------------------------------------------- |
| `proposal_uploaded` ⚠️ CREATE THIS  | Proposal document uploaded                                    |
| `proposal_role_confirmed` ⚠️ CREATE | "I confirm a Budget Holder or Decision Maker is on this deal" |

**Gap summary:**

```
To advance from Proposal:
• Complete all 5 SPICED fields (Situation, Pain, Impact, Critical Event, Decision Criteria)
• Add at least 3 contacts (with buying roles set)
• Upload proposal (separate conditional property)
• Confirm Budget Holder or Decision Maker identified (separate conditional property)
```

### Procurement (Stage 4)

**Automated checks (workflow):**

| #   | Requirement | Branch condition               |
| --- | ----------- | ------------------------------ |
| 1   | 4+ contacts | `num_associated_contacts` >= 4 |

**Manual checks (native conditional properties):**

| Property                               | What it enforces                                                        |
| -------------------------------------- | ----------------------------------------------------------------------- |
| `upload_sow___msa`                     | SOW/MSA uploaded                                                        |
| `procurement_role_confirmed` ⚠️ CREATE | "I confirm a Procurement or Legal & Compliance contact is on this deal" |

**Gap summary:**

```
To advance from Procurement:
• Add at least 4 contacts (with buying roles set)
• Upload SOW/MSA (separate conditional property)
• Confirm Procurement or Legal & Compliance contact identified (separate conditional property)
```

### Closed Won

`ready_to_advance` = Yes by default (Clear workflow). All requirements are native conditional properties.

### Closed Lost

Clear workflow sets `ready_to_advance` = empty and `stage_gap_summary` = empty.

---

## Separate Workflow: Line Item Balance

**Name:** `WF | Deal | Line Item Balance`
**Purpose:** Check whether line items exist and line item total matches deal amount.

HubSpot auto-calculation is **off** (deals have `hs_deal_amount_calculation_preference` = None). Reps set amounts manually, so mismatches are possible.

### What this workflow CAN check (standard):

| Check            | Branch condition                       |
| ---------------- | -------------------------------------- |
| Line items exist | `hs_num_of_associated_line_items` >= 1 |
| Amount > 0       | `amount` is known AND > 0              |

### What this workflow CANNOT check (standard):

| Check                  | Why                                 |
| ---------------------- | ----------------------------------- |
| Line item sum = amount | Requires API call to sum line items |

### Recommended approach

Create a `line_items_balanced` (Yes/No) property. The workflow checks line items >= 1 AND amount > 0:

- **Both true** → `line_items_balanced` = Yes
- **Either false** → `line_items_balanced` = No

For the **sum = amount** verification, two options:

1. **Turn on auto-calculation later** — set `hs_deal_amount_calculation_preference` = TCV. Then sum always equals amount.
2. **Add a manual conditional** at Closed Won: `line_items_match_amount_confirmed` ("I confirm line items match the deal amount")

### Enrollment

- `hs_num_of_associated_line_items` changes (re-enroll)
- `amount` changes (re-enroll)

### Add as conditional property at Closed Won

`line_items_balanced` = Required at Closed Won stage.

---

## Native Conditional Stage Properties (Final Configuration)

### By Stage

| Stage           | Conditional Property                                        | Required | Type      |
| --------------- | ----------------------------------------------------------- | -------- | --------- |
| **IPM**         | Deal Type                                                   | Yes      | Keep      |
| **Qual**        | `ready_to_advance`                                          | Yes      | Keep      |
| **Consensus**   | `ready_to_advance`                                          | Yes      | Keep      |
| **Proposal**    | `ready_to_advance`                                          | Yes      | Keep      |
| **Proposal**    | `proposal_uploaded`                                         | Yes      | ⚠️ Create |
| **Proposal**    | `proposal_role_confirmed`                                   | Yes      | ⚠️ Create |
| **Procurement** | `ready_to_advance`                                          | Yes      | Keep      |
| **Procurement** | `upload_sow___msa`                                          | Yes      | Keep      |
| **Procurement** | `procurement_role_confirmed`                                | Yes      | ⚠️ Create |
| **Closed Won**  | `contracts_uploaded_to_hubspot`                             | Yes      | Keep      |
| **Closed Won**  | `schedule_internal_handover`                                | Yes      | Keep      |
| **Closed Won**  | `external_business___technical_kick_off_meetings_scheduled` | Yes      | Keep      |
| **Closed Won**  | `contract_start_date`                                       | Yes      | Keep      |
| **Closed Won**  | `term_end_date`                                             | Yes      | Keep      |
| **Closed Won**  | Close Date                                                  | Yes      | Keep      |
| **Closed Won**  | Amount                                                      | Yes      | Keep      |
| **Closed Won**  | `line_items_balanced`                                       | Yes      | ⚠️ Create |
| **Closed Lost** | Close Date                                                  | Yes      | Keep      |
| **Closed Lost** | Closed Lost Reason                                          | Yes      | Keep      |

### Properties to REMOVE (replaced by workflow or no longer needed)

| Stage         | Remove                                                                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Qualification | IPM Follow-Up Meeting Scheduled, Pain point identified, Champion or Coach Identified, Close Date, Amount, Add Product Line Items + Amounts |
| Consensus     | Demo Given (Key Stakeholders), Champion aligned on impact of Knotch, Champion names additional stakeholders, Business Case Sent            |
| Proposal      | Consensus Reached, Initial MAP Created, Proposal Meeting Scheduled                                                                         |
| Procurement   | Final MAP agreed to by Champion, Budget Confirmation, Verbal Commitment (Scope + contract terms)                                           |
| Closed Won    | Add Product Line Items + Amounts, Closed Won Reason                                                                                        |

---

## Properties to Create in HubSpot

| Property                     | Type        | Field Type      | Label                                     | Group           | Status    |
| ---------------------------- | ----------- | --------------- | ----------------------------------------- | --------------- | --------- |
| `ready_to_advance`           | enumeration | booleancheckbox | Ready to Advance                          | dealstages      | ✅ Done   |
| `stage_gap_summary`          | string      | textarea        | What's Needed to Advance                  | dealinformation | ✅ Done   |
| `proposal_uploaded`          | string      | file            | Proposal Uploaded                         | dealstages      | To create |
| `proposal_role_confirmed`    | enumeration | booleancheckbox | Budget Holder or Decision Maker Confirmed | dealstages      | To create |
| `procurement_role_confirmed` | enumeration | booleancheckbox | Procurement or Legal Contact Confirmed    | dealstages      | To create |
| `line_items_balanced`        | enumeration | booleancheckbox | Line Items Balanced                       | dealstages      | To create |

---

## Build Order

1. **Create properties** — `proposal_uploaded`, `proposal_role_confirmed`, `procurement_role_confirmed`, `line_items_balanced`
2. **Build workflows** — start with `WF | Deal | Gate: Qualification` as a test, verify it sets `ready_to_advance` correctly
3. **Build remaining stage workflows** — Consensus, Proposal, Procurement, Clear
4. **Build Line Item Balance workflow**
5. **Test all workflows** on a test deal — walk it through every stage
6. **Reconfigure conditional stage properties** — add the new ones, remove the old ones per the tables above
7. **Go live** — turn on re-enrollment, monitor for a week
