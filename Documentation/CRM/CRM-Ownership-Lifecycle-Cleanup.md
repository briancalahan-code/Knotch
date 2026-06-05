# CRM Ownership & Lifecycle Cleanup

**Status:** Pending approval from Jason Lee (SVP Strategic Finance)
**Date:** 2026-03-27
**Deliverable:** Projects/Knotch-CRM-Ownership-Review-Jason-Pete.xlsx
**Slack:** Sent to Jason Lee DM for review

## Summary

Full audit and cleanup plan for company ownership, lifecycle accuracy, and field hygiene in HubSpot portal 44523005. Goal is one source of truth on who owns what and who is actually a customer.

## Decisions Made

### Role Assignments (Confirmed by Brian)

| Person          | Role                                   | Owns Accounts?                                |
| --------------- | -------------------------------------- | --------------------------------------------- |
| Andrew Bolton   | CS                                     | Yes -- active customers                       |
| Eli Grant       | CS                                     | Yes -- active customers                       |
| David Brown     | CS                                     | Yes -- active customers                       |
| Tim Long        | Former AE (departed)                   | No -- reassigned to Unassigned Marketing      |
| Don Vanderslice | AE                                     | Yes -- prospects                              |
| Pete Davies     | AE (Head of Growth, but owns accounts) | Yes -- prospects                              |
| Lee Fine        | Former AE (departed 2026-06-03)        | No -- reassigned to Pete/Don/Unassigned       |
| Jason Lee       | SVP Strategic Finance                  | No -- removing from ownership                 |
| Anda Gansca     | Leadership                             | No -- removing from ownership                 |
| Tyler Roselli   | Former/inactive                        | No -- removing from ownership                 |
| Ben Smith       | TBD                                    | Open question -- on Publicis, should he stay? |

### Ownership Rules

- **Active customers** -> owned by CS (Andrew, Eli, David)
- **Prospects** -> owned by AE (Don, Pete)
- **Unassigned / new inbound** -> "Unassigned Marketing" queue user
- **Contact ownership** -> cascades from company owner (enforced by workflow)

### Unassigned Marketing Queue User

- **Owner ID:** 90107252
- **Email:** unassigned@knotch.com
- **Seat type:** View-only
- **Purpose:** Holds unassigned/new inbound companies so reps can see they are unworked

### Lifecycle Field Consolidation

Two competing fields identified:

- `lifecyclestage` -- HubSpot native, 9 options including custom value `153491880` ("Cold Prospect", 1,673 companies)
- `account_stage` -- Custom "Company Lifecycle Stage", 6 options

**Recommendation:** Consolidate to `account_stage` as source of truth. Deprecate `lifecyclestage` for active use.

Related contact fields:

- `company_lifecycle_stage_sync` -- mirrors `account_stage` from company (9,508 contacts)
- `company_abx_stage` -- Demandbase enrichment (read-only, keep as-is)

### AE Owner Field

- `ae_owner` field on companies (1,023 populated)
- Currently 100% matches `hubspot_owner_id`
- Decision: Keep as-is, no changes needed

## Customer Triangulation Findings

Cross-referenced lifecyclestage + account_stage + closed-won deals + contract_start_date + term_end_date across 416 closed-won deals.

- **42** active contracts identified
- **57** companies flagged for review in the Excel
- **30** confirmed active customers
- **15** mislabeled as customers (no active deal, last contract ended years ago)
- **7** need Jason's verification
- **3** confirmed churned
- **2** active customers mislabeled as churned

Key insight: No single reliable "is this a current customer" indicator exists in HubSpot. Asked Jason for a finance/billing report to help triangulate.

## What Happens After Approval

### Cleanup Actions

1. Reassign Tyler Roselli's 439 companies per ownership rules
2. Assign 433 unowned companies to Unassigned Marketing
3. Fix lifecycle mismatches (customer tags on non-customers, etc.)
4. Move active customer accounts from AEs to CS owners
5. Reassign Jason and Anda's accounts per rules
6. Cascade company owners down to all associated contacts
7. Resolve Ben Smith's accounts based on Jason's decision

### Workflows to Build

See: Documentation/Workflows/CRM-Ownership-Lifecycle-Workflows.md

## Files

- `Projects/Knotch-CRM-Ownership-Review-Jason-Pete.xlsx` -- Final deliverable (2 tabs: Customer List Review + Roles & Ownership)
- `Projects/CRM-Ownership-Audit-2026-03-26.xlsx` -- Earlier 4-tab audit (superseded by above, keep for reference)
