# New Event Checklist

**Audience:** Brian Calahan, Pete Davies
**Last updated:** May 2026
**Related:** [Post-Event Processing SOP](Post-Event-Processing.md) | [RSVP Processor Workflow](RSVP-Processor-Workflow-Setup.md) | [Enablement/14](../../Enablement/14-Event-and-Webinar-List-Management.md)

---

## Before You Start

Decide on the **canonical event name**. This name is used everywhere -- lists, forms, the Google Sheet, Event Attendance records. Once set, do not change it.

**Naming convention:** `{City/Format} {Event Series} {Mon YYYY}`

Examples:

- `NYC ACE Launch Jun 2026`
- `Virtual Content Intelligence Webinar Apr 2026`
- `Cannes Lions Jun 2026`
- `P&C Summit Sep 2026`

---

## First-Time Setup (do once per sheet)

Before using the sheet for the first time:

1. Open the Google Sheet "Knotch_EventProcessor".
2. Click **Event Tools** > **Open Event Panel** in the menu bar -- a sidebar opens on the right with action buttons.
3. In the sidebar, click **Refresh Owner List** -- this fetches your HubSpot team members and populates the "Assign To" dropdowns in the Settings tab.
4. Go to the **Settings** tab and review follow-up task defaults:
   - **Follow-Up Tasks Enabled** (checkbox at top) = master on/off for all tasks
   - Each status row has: **Create Task** (checkbox), **Assign To** (dropdown -- pick a person or "Contact Owner"), **Due Days** (1-30), **Title Template** (variables: `{name}`, `{event}`, `{email}`)
   - Defaults: Attended + No Show tasks enabled, assigned to Contact Owner, due in 3-5 days

> **Tip:** Hover over any column header -- every field has a tooltip. Purple headers = you fill in. Dark headers = automatic.

---

## Checklist

### 1. Add the Event to Google Sheet

Open the **Knotch Event Processor** Google Sheet.

1. Go to the **Event Setup** tab.
2. Skip the gray example row (row 2) -- start in **row 3 or below**.
3. Fill in the three purple-header columns:
   - **Event Name:** The canonical name (exactly as you want it everywhere)
   - **Event Date:** The event date
   - **Event Type:** Select from dropdown -- In-Person, Online, or Hybrid
4. Set **Status** to "Active" (dropdown).
5. Leave all other columns blank -- List IDs, Form ID, and Last Processed are filled automatically by the processor.
6. Go to the **Settings** tab if you want to adjust follow-up task settings for this event (the settings apply to whatever event you process next).

### 2. Create the RSVP Form (If Taking RSVPs)

Skip this step if you are only processing post-event attendee data.

1. In HubSpot, go to **Marketing > Forms > Create form**.
2. Name it: `RSVP | {Canonical Event Name}` (e.g., `RSVP | NYC ACE Launch Jun 2026`).
3. Add the fields you need (First Name, Last Name, Email, Company, etc.).
4. Add a **hidden field** called `event_rsvp_event_name`.
5. Set the hidden field's default value to the canonical event name.
6. Save and publish the form.

### 3. Add the Form to the RSVP Processor Workflow

This is required every time you create a new RSVP form. The workflow does not auto-detect new forms.

1. Go to **Automations > Workflows**.
2. Open `WF | Event | RSVP Processor` (ID 1819563370).
3. Click on the enrollment trigger.
4. Add your new form to the trigger list (it uses OR logic -- any matching form triggers enrollment).
5. Save and re-publish the workflow.

The workflow automatically adds contacts to the `RSVP | Unprocessed` list and sends a Slack notification for every submission. No email or task fires by default. If you need event-specific actions (confirmation email, follow-up task), copy the template branch in the workflow — see [RSVP Processor Workflow Setup](RSVP-Processor-Workflow-Setup.md) for full details.

### 4. Create a Landing Page

Not every event needs a landing page. Skip if RSVPs are collected another way (email link, calendar invite, etc.).

**Option A: Webflow Event Page (recommended for high-touch events)**

Use the single-embed approach — one HTML block pasted into a Webflow page that takes over the entire page with custom design, built-in form, and confirmation card.

1. **Copy an existing template.** Clone the most recent embed file from `Projects/Event-Page-Template/webflow/`:
   - `ace-launch-EMBED.html` — dark luxury theme (Guggenheim event)
   - `cannes-chefs-table-EMBED.html` — warm gold theme (Cannes dinner)
2. **Customize the content.** Update these sections in the HTML:
   - Hero section: event tagline, date, brand name
   - Details grid: venue, date/time, dress code
   - RSVP section: heading, capacity note
   - Footer: event description, copyright
3. **Update the JavaScript variables** at the bottom of the file:
   ```javascript
   var PORTAL_ID = "44523005"; // Knotch HubSpot portal (don't change)
   var FORM_ID = "your-new-form-id"; // From Step 2
   var RSVP_STATUS = "Waitlisted"; // Default status on submission
   var EVENT_NAME = "Your Event Name"; // Must match hidden field value exactly
   var PAGE_NAME = "Your Page Name"; // For HubSpot analytics
   ```
4. **Update the container ID.** Change `#ace-page` or `#cannes-page` to a unique ID (e.g., `#summit-page`) in both the CSS and HTML. This prevents style collisions if multiple event pages exist on the same Webflow site.
5. **Update background images.** Upload event-specific images to HubSpot Files and update the CSS `background` URLs for both desktop and mobile.
6. **Keep the AccessiBe fix.** Every embed must include both the CSS rules and the JavaScript that removes the AccessiBe widget. These are at the top of the `<style>` block and at the bottom of the `<script>` block. Do not remove them.
7. **Create the Webflow page:**
   - In Webflow, create a new page under `/events/your-event-slug`.
   - Add a single **HTML Embed** element to the page body.
   - Paste the entire contents of your embed file into the embed block.
   - Publish.
8. **Test end-to-end:**
   - Visit the published page.
   - Submit the form with a test email.
   - Confirm the confirmation card appears ("Thank you, {name}. Your invite request has been received...").
   - Confirm the contact lands in `RSVP | Unprocessed` list (ID 1775).
   - Confirm the Slack notification fires.
   - Confirm the AccessiBe blue button does NOT appear.

**Option B: HubSpot Landing Page**

For simpler events or when you don't need custom design:

1. Clone the most recent event landing page template in HubSpot.
2. Update the content (event details, date, location, speakers).
3. Embed the RSVP form you created in Step 2.
4. Preview and test the form submission end-to-end.
5. Publish the landing page.

### 5. Share the Link

Distribute the landing page URL or direct form link to the team. If Pete is doing outbound for the event, make sure he has the link for email sequences.

---

## Quick Reference

| Item                              | Convention                                |
| --------------------------------- | ----------------------------------------- |
| Canonical name                    | `{City/Format} {Event Series} {Mon YYYY}` |
| Form name                         | `RSVP \| {Canonical Name}`                |
| Hidden field                      | `event_rsvp_event_name` = canonical name  |
| List names (created by processor) | `(W)EVT_{Event_Name}_{Status}` and `_All` |
| Workflow                          | `WF \| Event \| RSVP Processor`           |
| Unprocessed list                  | `RSVP \| Unprocessed` (ID 1775)           |

---

## Understanding the Sheet

- **Example rows** (gray, italic, row 2 on each tab) are never processed -- they show you the format
- **Purple headers** = required fields you fill in
- **Dark headers** = auto-filled by the processor (don't edit these)
- The **sidebar** (Event Tools > Open Event Panel) has all the action buttons -- you don't need to memorize menu items
- The **Reference** tab is a built-in cheat sheet with naming conventions, status definitions, and quick-start instructions
- Run **Refresh Owner List** in the sidebar if your HubSpot team changes

---

## After the Event

Move on to [Post-Event Processing](Post-Event-Processing.md) to process attendee data through the Google Sheet.
