# Event Management Workflow — Job Aid

Updated: BC 5.15

---

## Pre-Event

1. **David Brown shares overview doc** with title, description, panelists

2. **Create thumbnail in Figma**
   - Duplicate previous thumbnail → update title, panelist photos, etc.
   - [Figma link](https://www.figma.com/design/9m0HkdKdEedTmmnGXcvI0Q/Untitled?node-id=0-1&p=f&t=yeTbKONzNBysJKHf-0)
   - Download thumbnail JPG → add to overview doc

3. **Set up event in Sequel**
   - Create new event → add details, thumbnail
   - Copy Sequel embed code → add to overview doc
   - Slack Aron to add new workshop to the website

4. **Add panelists and hosts to Sequel**
   - Copy/share each panelist's unique studio link with David

5. **Add event to the Event Processor Google Sheet**
   - Open the [Knotch Event Processor](https://docs.google.com/spreadsheets/) → Event Setup tab
   - Fill in: Event Name, Event Date, Event Type (In-Person or Online)
   - Naming format: `{City/Format} {Event Series} {Mon YYYY}` (e.g., NYC ACE Launch Jun 2026)

6. **Create RSVP form in HubSpot** (if collecting RSVPs)
   - Name: `RSVP | {Event Name}` (e.g., `RSVP | ACE Launch Jun 2026`)
   - Add a hidden field `event_rsvp_event_name` pre-filled with the event name
   - Add your new form as an enrollment trigger in the `WF | Event | RSVP Processor` workflow (ID 1819563370)
   - The workflow adds contacts to `RSVP | Unprocessed` list and sends a Slack notification for every submission
   - If you need event-specific email/task actions, copy the template branch in the workflow (see [RSVP Processor Workflow Setup](RSVP-Processor-Workflow-Setup.md))

---

## Email Invite

1. **Duplicate previous event invite email** in HubSpot
2. Update thumbnail, copy, links
3. Send test email → review segments → send

---

## Post-Event

1. **Switch the recording to On-Demand** in Sequel

2. **Download transcript**
   - Sequel → Media Hub → Sequel AI → download transcript → add to Google Doc → share with David

---

## Event Processing

> Previously 30+ manual steps (Apollo CSV, Clay enrichment, LinkedIn lookup, sort, re-upload). Now automated via the Event Processor Google Sheet.

### Load Attendees (pick one)

| Method             | When to use                                                 | How                                                                        |
| ------------------ | ----------------------------------------------------------- | -------------------------------------------------------------------------- |
| **Pull RSVPs**     | RSVP form was set up and submissions came in (see note)     | Sidebar → Pull RSVPs (pulls from the RSVP Unprocessed list)                |
| **Pull from List** | You have a HubSpot list ID (e.g., from Sequel registration) | Sidebar → Pull from List → enter list ID + default status                  |
| **Paste directly** | You have a CSV or spreadsheet from the event platform       | Paste emails into column A, set status in column B, event name in column C |

> **Pull RSVPs prerequisite:** This only works if an RSVP form was created in HubSpot with a hidden field `event_rsvp_event_name`, and the form was added as an enrollment trigger in the `WF | Event | RSVP Processor` workflow. The workflow adds submissions to the `RSVP | Unprocessed` list (ID 1775), which is what Pull RSVPs reads from.
>
> **Pre-made examples:** `RSVP | ACE Launch Jun 2026` and `RSVP | P&C Summit Sep 2026` are already set up — clone one of these as a starting point for new events. See [RSVP Processor Workflow Setup](RSVP-Processor-Workflow-Setup.md) for the full guide.

### Set Statuses

Make sure every attendee row has the correct status before processing:

| Status     | Meaning                    |
| ---------- | -------------------------- |
| Invited    | Invited, no response yet   |
| Registered | RSVP'd yes                 |
| Attended   | Showed up                  |
| No Show    | Registered but didn't show |
| Declined   | Said no                    |
| Waitlisted | On the waitlist            |

Use **Bulk Status Change** in the sidebar to flip all rows from one status to another (e.g., change all "Registered" to "Attended" after the event).

### Process

1. Click **Process Event** in the sidebar
2. Review the confirmation summary (shows counts of records, lists, tasks to create)
3. Click OK

**The processor handles everything automatically:**

- Enriches contacts (looks up in HubSpot first → falls back to Apollo → creates new contact if not found)
- Creates Event Attendance records in HubSpot (custom object linked to each contact)
- Creates timeline notes on each contact
- Creates/populates HubSpot lists using the naming convention:
  - In-person: `EVT_{Event_Name}_{Status}` (e.g., `EVT_NYC_ACE_Launch_Jun_2026_Attended`)
  - Online: `WEVT_{Event_Name}_{Status}` (e.g., `WEVT_Content_Workshop_May_2025_No_Show`)
  - Plus an `_All` list for every event
- Updates contact RSVP properties (event_rsvp_status, event_rsvp_event_name, event_rsvp_date)
- Creates follow-up tasks per the Settings tab configuration

4. **Check the Log tab** for any errors

### If Something Goes Wrong

- **Preview first:** Use Preview (Dry Run) to see what would happen without writing to HubSpot
- **Rollback:** Sidebar → Rollback Last Run deletes the Event Attendance records, notes, and tasks from the last run
- **Contact History:** Sidebar → Contact History to look up all events for a specific email

---

## Post-Event Emails

Lists are already created by the processor — no manual list setup needed.

1. **Attendee email:** HubSpot → Emails → create attendee version (add takeaway blog, recording link) → send to `(W)EVT_{Event}_Attended` list
2. **No-show email:** Create no-show version (add takeaway blog, recording link) → send to `(W)EVT_{Event}_No_Show` list

---

## List Naming Reference

| Type                    | Prefix  | Example                                      |
| ----------------------- | ------- | -------------------------------------------- |
| In-Person (all)         | `EVT_`  | `EVT_NYC_ACE_Launch_Jun_2026_All`            |
| In-Person (status)      | `EVT_`  | `EVT_NYC_ACE_Launch_Jun_2026_Attended`       |
| Online/Webinar (all)    | `WEVT_` | `WEVT_Content_Workshop_May_2025_All`         |
| Online/Webinar (status) | `WEVT_` | `WEVT_Content_Workshop_May_2025_No_Show`     |
| Hybrid                  | `EVT_`  | Uses `EVT_` prefix (has in-person component) |

**Legacy lists** (pre-May 2026): Some older lists use `EVT_` or `WEVT_` with different date formats. These remain as-is — the processor creates new lists in the format above.

---

## Quick Reference: What's Manual vs. Automatic

| Step                                   | Manual                    | Automatic                 |
| -------------------------------------- | ------------------------- | ------------------------- |
| Create event in Sequel                 | You                       | —                         |
| Create RSVP form + add to workflow     | You (if collecting RSVPs) | —                         |
| Add event to Event Processor sheet     | You (name, date, type)    | —                         |
| Send invite emails                     | You                       | —                         |
| Load attendees into sheet              | You (one click or paste)  | —                         |
| Set attendee statuses                  | You                       | —                         |
| Enrich contacts (name, company, title) | —                         | HubSpot + Apollo lookup   |
| Create/find HubSpot contacts           | —                         | Auto-creates if not found |
| Create Event Attendance records        | —                         | Batch created             |
| Create timeline notes                  | —                         | Batch created             |
| Create/populate HubSpot lists          | —                         | Auto-named and populated  |
| Update contact RSVP properties         | —                         | Batch updated             |
| Create follow-up tasks                 | —                         | Per Settings tab rules    |
| Send post-event emails                 | You                       | —                         |

---

## Checklists

### Pre-Event Checklist

- [ ] David Brown shares overview doc (title, description, panelists)
- [ ] Create thumbnail in Figma (duplicate previous → update)
- [ ] Download thumbnail JPG → add to overview doc
- [ ] Set up event in Sequel (details, thumbnail, embed code)
- [ ] Slack Aron to add new workshop to the website
- [ ] Add panelists/hosts to Sequel → share studio links with David
- [ ] Add event to Event Processor Google Sheet (Event Setup tab: name, date, type)
- [ ] **If collecting RSVPs:**
  - [ ] Create RSVP form in HubSpot: `RSVP | {Event Name}`
  - [ ] Add hidden field `event_rsvp_event_name` with canonical event name
  - [ ] Add form as enrollment trigger in `WF | Event | RSVP Processor` workflow
  - [ ] Test: submit form → confirm contact appears in `RSVP | Unprocessed` list

### Email Invite Checklist

- [ ] Duplicate previous event invite email in HubSpot
- [ ] Update thumbnail, copy, links
- [ ] Send test email to yourself
- [ ] Review send segments
- [ ] Send

### Post-Event Checklist

- [ ] Switch recording to On-Demand in Sequel
- [ ] Download transcript (Sequel → Media Hub → Sequel AI)
- [ ] Add transcript to Google Doc → share with David

### Event Processing Checklist

- [ ] Open Event Processor Google Sheet → Event Tools → Open Event Panel
- [ ] Load attendees (Pull RSVPs, Pull from List, or paste directly)
- [ ] Verify every row has a status (Invited, Registered, Attended, No Show, Declined, Waitlisted)
- [ ] Use Bulk Status Change if needed (e.g., flip all Registered → Attended)
- [ ] Click **Process Event** → review confirmation summary → OK
- [ ] Check the **Log** tab for errors
- [ ] **Spot-check 3-5 contacts in HubSpot:**
  - [ ] Contact exists with correct name, email, company
  - [ ] Event Attendance record linked to contact
  - [ ] Contact in `(W)EVT_{Event_Name}_All` list
  - [ ] Contact in `(W)EVT_{Event_Name}_{Status}` list
  - [ ] Follow-up task created (if enabled in Settings for that status)

### Post-Event Emails Checklist

- [ ] Create attendee email (add takeaway blog, recording link)
- [ ] Send to `(W)EVT_{Event}_Attended` list
- [ ] Create no-show email (add takeaway blog, recording link)
- [ ] Send to `(W)EVT_{Event}_No_Show` list
