# Event and Webinar List Management

**Audience:** Marketing, RevOps, Admins | **Topics:** events, webinars, lists, Event Attendance, RSVP, Google Sheet processor | **Last Updated:** May 2026

---

## Core Principle

**HubSpot lists are the source of truth for event attendance, not contact properties.** Contact-level event properties (`fy25_event_status`, `fy26_event_attendance`, etc.) capture only ~12% of actual participants and should never be relied on alone.

---

## Event Attendance System (May 2026)

The Event Attendance system replaces the manual list-creation process for new events. It consists of:

- **Event Attendance custom object** (objectTypeId `2-62279031`) -- structured records with event_name, event_date, event_status, event_type, event_key, and event_source. Associated to contacts. This is the primary data store for event participation going forward.
- **Google Sheet "Knotch Event Processor"** -- the operator interface for adding attendees, triggering processing, and reviewing results. Tabs: Event Setup, Attendees, Settings, Log, Reference.
- **Apps Script backend** -- handles HubSpot search, Apollo enrichment, contact creation, Event Attendance record creation, list management, and RSVP property updates. Source: `Projects/Event-Processor/apps-script/`.
- **Workflow `WF | Event | RSVP Processor`** (ID 1819563370) -- fires on form submissions, adds contacts to the `RSVP | Unprocessed` list (ID 1775), and sends a Slack notification for every RSVP. A dormant template branch is available to copy when you need event-specific actions (confirmation email, follow-up task). See **RSVP Processor Workflow Setup** (Documentation/Events/RSVP-Processor-Workflow-Setup.md).

### How It Works

1. RSVPs come in via HubSpot forms. The workflow adds them to `RSVP | Unprocessed`.
2. After the event, an operator opens the Google Sheet, clicks **Event Tools > Open Event Panel** to open the sidebar with action buttons, loads attendee data (Pull RSVPs, Pull from List, Import CSV, or paste directly), and clicks **Process Event**.
3. The processor enriches unknown contacts (HubSpot search, then Apollo fallback), creates contacts as needed, creates Event Attendance records, builds static lists, updates RSVP properties, and creates follow-up tasks (configurable per status in the Settings tab).

### Sheet UI

- **Sidebar** (Event Tools > Open Event Panel): Action buttons for Process Event, Pull RSVPs, Pull from List, Import CSV, Refresh Owner List
- **Purple headers** = required fields (email, status, event name/date/type). **Dark headers** = auto-filled by the processor.
- **Example rows** (gray, italic, row 2 on each tab) are never processed -- they show the expected format.
- **Hover tooltips** on every column header explain what the field is and whether it's required or automatic.
- **Settings tab**: Table with checkboxes and dropdowns for follow-up task configuration per status. "Contact Owner" assigns the task to whoever owns the contact in HubSpot. Run **Refresh Owner List** to populate team dropdowns from HubSpot.
- **Reference tab**: Built-in cheat sheet with naming conventions, status definitions, and quick-start instructions.

### SOPs

- **Event Lifecycle** (Documentation/Events/Event-Lifecycle.md) — End-to-end six-step workflow
- **Event Management Job Aid** (Documentation/Events/Event-Management-Job-Aid.md) — Quick reference checklists
- **New Event Checklist** (Documentation/Events/New-Event-Checklist.md) — Setting up a new event
- **Post-Event Processing** (Documentation/Events/Post-Event-Processing.md) — Processing attendees after an event
- **RSVP Processor Workflow Setup** (Documentation/Events/RSVP-Processor-Workflow-Setup.md) — Building the RSVP workflow

---

## Naming Conventions

### Lists (New System -- May 2026+)

The Google Sheet processor automatically creates lists using this convention:

**Format:** `EVT_{Event_Name}_{Status}` (in-person) / `WEVT_{Event_Name}_{Status}` (online/webinar), plus `_All` list per event

Examples:

- `EVT_NYC_ACE_Launch_Jun_2026_Attended`
- `EVT_NYC_ACE_Launch_Jun_2026_Registered`
- `EVT_NYC_ACE_Launch_Jun_2026_All`
- `WEVT_Secret_Weapon_Webinar_Mar_2026_All`

The canonical event name follows the format: `{City/Format} {Event Series} {Mon YYYY}`.

### Forms

**Format:** `RSVP | {Canonical Event Name}`

Examples:

- `RSVP | NYC ACE Launch Jun 2026`
- `RSVP | P&C Summit Sep 2026`

Each form includes a hidden field `event_rsvp_event_name` pre-filled with the canonical event name.

### Legacy Lists (Pre-May 2026)

Older lists use the `EVT_` and `WEVT_` prefix conventions. These are still valid and still in HubSpot -- do not rename or delete them. The backfill created Event Attendance records for all legacy list members.

- `EVT_{Event_Name}_{Year}` -- in-person events (e.g., `EVT_Cannes_Lions_2026`)
- `WEVT_{Webinar_Name}_{Date}` -- webinars (e.g., `WEVT_Content_Intelligence_Masterclass_2026-03`)

---

## List Type

Always create **static (manual) lists**, not active lists. Event attendance is a point-in-time fact, not a dynamic filter.

---

## Manual Process (Legacy -- Pre-May 2026)

For new events, use the Google Sheet processor instead (see SOPs above). The manual process below is retained for reference and edge cases where the processor is not suitable.

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

As of May 2026:

- **96** legacy lists (43 `EVT_`/`WEVT_` prefix + sub-lists), ~6,218 unique contacts
- **4,464** Event Attendance custom object records (backfilled from legacy lists, covering 31 events)
- New events create `(W)EVT_{Name}_{Status}` lists automatically via the processor

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

---

## Related Documents

- **Data Enrichment Playbook** (07) — Enrichment tools used during event processing (Apollo, Clay)
- **Workflow Automation Reference** (09) — RSVP Processor Workflow details and trigger logic
