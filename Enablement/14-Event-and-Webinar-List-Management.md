# Event and Webinar List Management

**Effective Date:** April 2026
**Audience:** Marketing, Revenue Ops, HubSpot Admins
**Purpose:** Standard operating procedure for creating and maintaining event attendee lists in HubSpot

---

## Core Principle

**HubSpot lists are the source of truth for event attendance, not contact properties.** Contact-level event properties (`fy25_event_status`, `fy26_event_attendance`, etc.) capture only ~12% of actual participants and should never be relied on alone.

---

## Naming Conventions

### In-Person Events

**Prefix:** `EVT_`
**Format:** `EVT_{Event_Name}_{Year}`

Examples:

- `EVT_Cannes_Lions_2026`
- `EVT_Adobe_Summit_2026`
- `EVT_CES_2026`
- `EVT_Knotch_ACE_Launch_2026`

### Webinars

**Prefix:** `WEVT_`
**Format:** `WEVT_{Webinar_Name}_{Date}`

For webinars, include the date (YYYY-MM or YYYY-MM-DD) since the same webinar series may recur:

- `WEVT_Content_Intelligence_Masterclass_2026-03`
- `WEVT_Quarterly_Product_Update_2026-Q2`

### Sub-Lists (When Needed)

Append a suffix to distinguish attendance status:

- `EVT_Cannes_Lions_2026` — primary attendee list (confirmed attendees)
- `EVT_Cannes_Lions_2026_Registered` — registered but attendance unknown
- `EVT_Cannes_Lions_2026_NoShow` — registered but did not attend

Only create sub-lists when tracking registrant-only and no-show data adds value. For most events, a single attendee list is sufficient — registrant-only and no-show lists historically add only ~18 VP+ contacts beyond attendee lists.

---

## List Type

Always create **static (manual) lists**, not active lists. Event attendance is a point-in-time fact, not a dynamic filter.

---

## Step-by-Step: Creating an Event List

### 1. Prepare the Attendee Data

Before touching HubSpot:

- **Deduplicate the source file.** Check for intra-list duplicates (same person listed twice with slight name/email variations).
- **Cross-reference against HubSpot by email.** Search every attendee email to identify contacts that already exist.
- **Cross-reference by name + company.** For contacts not matched by email, search HubSpot by last name and verify against company. Watch for domain aliases (e.g., `chase.com` vs `jpmchase.com`, `ae.com` vs `aeo-inc.com`).
- **Cross-reference companies.** For every company in the list, verify whether it already exists in HubSpot by domain and name before creating new company records.
- **Build a dedup plan.** Categorize every row as: `skip` (already exists), `create_contact` (new contact, existing company), or `create_company_and_contact` (both new).
- **Get approval** on the dedup plan before writing anything to HubSpot.

### 2. Import New Contacts and Companies

- Create new companies first (batch if possible), then contacts.
- Associate every contact with their company at creation time.
- Verify all associations after import.

### 3. Create the List in HubSpot

1. Go to **Contacts → Lists → Create list**
2. Select **Contact-based**, **Static list**
3. Name it following the convention: `EVT_{Event_Name}_{Year}` or `WEVT_{Name}_{Date}`
4. Save the list

### 4. Add Members

Add **all attendees** to the list — both pre-existing contacts (the "skips") and newly imported contacts. The list should represent everyone who attended, not just who was new.

### 5. Verify

- Confirm the member count matches your expected total
- Spot-check a sample of members to ensure correct contacts are included

---

## Common Pitfalls

| Pitfall                                      | How to Avoid                                                                                                          |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Relying on contact properties for event data | Always use list membership as source of truth                                                                         |
| Creating duplicates during import            | Full email + name/company cross-reference before importing                                                            |
| Missing domain aliases                       | Search by both domain and company name — many companies use different email domains than their HubSpot primary domain |
| Skipping company dedup                       | Companies duplicate just as easily as contacts — always verify                                                        |
| Using active lists for events                | Events are point-in-time — always use static lists                                                                    |
| Only adding new contacts to the list         | Add all attendees, including those who already existed in HubSpot                                                     |
| Creating sub-lists by default                | Only create registrant/no-show sub-lists when the data is actionable                                                  |

---

## Current Inventory

As of April 2026:

- **15** in-person event lists (`EVT_` prefix), ~5,512 contacts
- **28** webinar lists (`WEVT_` prefix), ~1,291 attendees + registrants/no-shows
- **~6,218** unique contacts across all event lists

---

## Using Event Lists

Event lists are most valuable for:

- **Targeted follow-up campaigns** — enroll attendees in post-event sequences
- **Account intelligence** — identify which target accounts had representation at an event
- **Event ROI reporting** — cross-reference attendee lists against pipeline and closed-won deals
- **Multi-touch attribution** — event attendance as a touchpoint in the buyer journey
- **Future event planning** — analyze past attendance to build invite lists

To pull list membership programmatically, use the HubSpot API:

```
GET /crm/v3/lists/{listId}/memberships
```
