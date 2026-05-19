# WF | Event | RSVP Processor -- Setup Guide

**Portal:** 44523005 (Sales Enterprise)
**Workflow Type:** Contact-based
**Workflow ID:** 1819563370
**Created:** May 2026 | **Updated:** May 19, 2026
**Related:** Enablement/14-Event-and-Webinar-List-Management.md

---

## What This Workflow Does

When someone submits an RSVP form for any Knotch event, this workflow:

1. Adds the contact to the `RSVP | Unprocessed` static list (list ID 1775) so the Google Sheet processor can pick them up in batch
2. Sends a Slack notification (fires for ALL events, every submission)
3. Routes through an IF/THEN branch with a dormant template — no email or task fires by default

The template branch exists as a copyable pattern. When you need event-specific actions (confirmation email, follow-up task), duplicate the template branch, change the filter to the real event name, and add your actions.

The workflow does NOT update `event_rsvp_status` or create Event Attendance records. That is handled downstream by the Google Sheet processor.

---

## Prerequisites

Complete all of these before building the workflow.

### 1. Static List Exists

Confirm the static list `RSVP | Unprocessed` (list ID 1775) exists in HubSpot.

1. Go to **Contacts > Lists** in the top navigation bar.
2. Search for `RSVP | Unprocessed`.
3. Verify it appears and is a **static** list (not active). The list ID should be 1775 -- you can confirm by clicking into the list and checking the URL, which will end in `/lists/1775`.

If the list does not exist, create it:

1. Click **Create list** (top right).
2. Select **Contact-based**.
3. Select **Static list**.
4. Name it exactly: `RSVP | Unprocessed`
5. Click **Save list**. Note the list ID from the URL.

### 2. RSVP Forms Follow Naming Convention

All RSVP forms must be named with the prefix `RSVP |` followed by the event name. Examples:

- `RSVP | ACE Launch Jun 2026`
- `RSVP | P&C Summit Sep 2026`

Each form must include a hidden field called `event_rsvp_event_name` that is pre-filled with the canonical event name (e.g., "ACE Launch"). This hidden field is what the workflow branches on.

### 3. Contact Property Exists

Confirm the contact property `event_rsvp_event_name` exists:

1. Go to **Settings** (gear icon, top right).
2. In the left sidebar, click **Data Management > Properties**.
3. Search for `event_rsvp_event_name`.
4. If it does not exist, create it:
   - Click **Create property**.
   - **Object type:** Contact
   - **Group:** Event information (or create a new group)
   - **Label:** Event RSVP Event Name
   - **Internal name:** `event_rsvp_event_name` (HubSpot auto-generates this from the label -- verify it matches)
   - **Field type:** Single-line text
   - Click **Create**.

### 4. HubSpot Slack Integration Installed

The Slack notification step requires HubSpot's official Slack app.

1. Go to **Settings > Integrations > Connected apps**.
2. Look for **Slack** in the list.
3. If not connected, click **Visit App Marketplace**, search for "Slack", and install it. You will need to authorize HubSpot to post to your Slack workspace.
4. After connecting, verify you can see your Slack channels from within HubSpot by going to any workflow and adding a "Send Slack notification" action -- the channel picker should populate.

### 5. (Optional) Confirmation Email Template

Only needed if you plan to add event-specific email actions by copying the template branch.

1. Go to **Marketing > Email**.
2. Click **Create email > Automated**.
3. Design the confirmation email (subject line, body content, branding).
4. Save it but do NOT send it. The workflow will trigger it.
5. Note the email name -- you will select it when configuring the event-specific branch.

---

## Build the Workflow

### Step 1: Create a New Workflow

1. In the top navigation bar, click **Automations > Workflows**.
2. Click the **Create workflow** button (top right, orange button).
3. You will see a screen asking you to choose how to start. Select **From scratch**.
4. Under "Choose object", select **Contact-based**.
5. Click **Next**.
6. At the top of the screen, you will see the default name "Untitled workflow" -- click on it and rename it to exactly: `WF | Event | RSVP Processor`
7. Click anywhere outside the name field to save it.

### Step 2: Set the Enrollment Trigger

1. In the workflow editor, you will see a box at the top that says **Set up triggers**. Click it.
2. A panel will open on the left side. You will see a search bar and filter options. Under "Filter type", select **Form submission**.

   > You will see a dropdown that says "Form submission" with options below it. This is the correct trigger type.

3. In the form picker that appears, you need to select forms that match the `RSVP |` naming pattern. HubSpot does not support wildcard/prefix matching in form triggers natively, so you have two options:

   **Option A -- Select all existing RSVP forms (recommended):**
   - In the form dropdown, scroll or search for forms starting with `RSVP |`.
   - Select each one (e.g., `RSVP | ACE Launch Jun 2026`).
   - To add multiple forms, click **Add filter** and add another "Form submission" filter for each form.
   - Set the logic between filters to **OR** (any of these forms).

   **Option B -- Use "any form":**
   - Select **Any form** from the dropdown if you want this workflow to fire on every form submission. Then use a branch later to filter to RSVP forms only.
   - This is less precise and not recommended unless you add a branch to check the form name.

   > **Important:** Every time you create a new RSVP form, you must come back to this workflow and add it to the trigger list (Option A) or the new form will not trigger the workflow. Add a reminder to your event launch checklist.

4. Click **Save** in the trigger panel.

### Step 3: Enable Re-enrollment

This is critical. The same contact might RSVP to multiple events, so they need to re-enter the workflow each time.

1. While still in the trigger panel (or click back into it), look for the **Re-enrollment** tab or toggle. In Sales Enterprise, this appears as a tab next to "Triggers" at the top of the trigger panel.
2. Click the **Re-enrollment** tab.
3. Toggle re-enrollment **ON**.
4. Under "Re-enroll contacts when they meet any of these triggers again", make sure all your form submission triggers are checked.
5. Click **Save**.

   > Without re-enrollment, a contact who RSVPs to one event and then RSVPs to another would NOT enter the workflow the second time. This would break the entire process.

### Step 4: Add Action -- Add to Static List

1. Below the trigger box, click the **+** button to add the first action.
2. A panel opens on the left showing action categories. Search for or scroll to **Add to static list** (under the "List" or "Contact" category).

   > You will see "Add to static list" as an option. Do not confuse this with "Add to list" which is for active lists.

3. Click **Add to static list**.
4. In the configuration panel:
   - **List:** Search for and select `RSVP | Unprocessed` (list ID 1775).
5. Click **Save**.

### Step 5: Add Action -- Send Slack Notification

This fires for every RSVP submission across all events.

1. Below the "Add to static list" action, click the **+** button.
2. Search for **Send Slack notification** (under the "Communication" or "External communication" category).

   > If you do not see this option, the Slack integration is not installed. Go back to Prerequisites Step 4.

3. Click **Send Slack notification**.
4. In the configuration panel:
   - **Slack channel:** Select the appropriate channel (currently channel ID `C0B2NJHDCBH`).
   - **Message:** Enter the following text (use personalization tokens for the dynamic fields):
     ```
     New RSVP: {{contact.firstname}} {{contact.lastname}} ({{contact.company}}) — Event: {{contact.event_rsvp_event_name}} | Status: {{contact.event_rsvp_status}}
     ```
5. Click **Save**.

### Step 6: Add Action -- IF/THEN Branch (Template)

This branch exists as a dormant template. It never fires in normal operation because its filter value is set to `TEMPLATE_DO_NOT_DELETE`, which no real event name will ever match.

1. Below the Slack action, click the **+** button.
2. Search for or scroll to **If/then branch** (under the "Logic" category).
3. Click **If/then branch**.
4. Configure **Branch 1** (the template branch):
   - **Branch name:** `TEMPLATE - Copy for event-specific actions`
   - Set the filter:
     - **Filter type:** Contact property
     - **Property:** `event_rsvp_event_name`
     - **Operator:** **contains**
     - **Value:** `TEMPLATE_DO_NOT_DELETE`
   - Click **Save** on the branch.
5. The **"None met"** branch catches all real events. Rename it to `All other events (no extra actions)` if your HubSpot version allows branch renaming.

   > The template branch routes to a placeholder email action (see Step 7). When you need event-specific actions for a real event, copy this branch and change the filter — see Maintenance section below.

### Step 7: Template Branch -- Placeholder Email

This email action is only reachable through the template branch, which never matches. It exists so that when you copy the template branch for a real event, the email action is already wired up.

1. Under the template branch, click the **+** button.
2. Search for **Send email**.
3. Select a placeholder automated email (or the most recent event confirmation email).
4. Click **Save**.

   > You can also add a "Create task" action before the email on this branch. The template structure should be: Create task → Send email. Both are dormant until you copy the branch for a live event.

### Step 8: Review the Workflow

Before turning it on, review the complete flow:

```
[Trigger: Form submission -- RSVP | forms (OR logic)]
         |
         v
[Add to static list: RSVP | Unprocessed]
         |
         v
[Slack notification (fires for ALL events)]
         |
         v
[IF/THEN: event_rsvp_event_name contains...]
        /                              \
  TEMPLATE (never fires)        All other events
       |                              |
 [Send email]                    (no actions)
   (dormant)
```

Verify each action by clicking on it and confirming the settings match what is documented above.

### Step 11: Set Workflow Settings

1. Click the **Settings** tab at the top of the workflow editor (next to "Actions").
2. Review the following:
   - **Unenrollment and suppression:** Leave defaults unless you have contacts who should never receive event communications.
   - **Execution timing:** Set to **Any time** (RSVPs should process immediately, not wait for business hours).
3. Click **Save**.

### Step 12: Turn On the Workflow

1. Click the **Review and publish** button (top right, orange).
2. HubSpot will show a summary of the workflow, including trigger conditions, actions, and re-enrollment settings.
3. Review the summary carefully.
4. You will be asked whether to enroll contacts who currently meet the trigger criteria. Select **No, only enroll contacts who meet the trigger criteria after turning on the workflow** -- you do not want to retroactively process old form submissions.
5. Click **Turn on**.

---

## Testing

### Test 1: Basic RSVP

1. Create a test form named `RSVP | Test Event` with the hidden field `event_rsvp_event_name` set to "Test Event".
2. Add the form to the workflow enrollment triggers.
3. Submit the form using a test contact.
4. Wait 1-2 minutes for the workflow to process.
5. Verify:
   - [ ] The test contact appears in the `RSVP | Unprocessed` static list (list ID 1775).
   - [ ] The test contact's workflow history shows they entered and exited the workflow.
   - [ ] A Slack notification was posted (event name and status should appear in the message).
   - [ ] No email was sent (the template branch should not match "Test Event").
   - [ ] No task was created.
6. Remove the test contact from the static list manually after testing.

### Test 2: Re-enrollment

1. Using the same test contact from Test 1, submit a different RSVP form.
2. Verify the contact enters the workflow a second time (check the contact's workflow history -- it should show two separate enrollments).
3. Verify they are added to the static list again (they may already be on it -- that is fine, HubSpot silently handles duplicates in static lists).

### Test 3: Verify Google Sheet Integration

After completing Tests 1-2, confirm the Google Sheet processor is successfully pulling contacts from the `RSVP | Unprocessed` list and processing them. This is outside the scope of this workflow but confirms the end-to-end flow works.

---

## Maintenance Checklist

### When Creating a New Event

1. Create the RSVP form following the naming convention: `RSVP | {Event Name}`
2. Add the hidden field `event_rsvp_event_name` with the canonical event name
3. **Go to this workflow** and add the new form to the enrollment trigger list (Step 2 above)
4. If the event needs a custom landing page, see [New Event Checklist](New-Event-Checklist.md) Step 4
5. If the event needs event-specific actions (confirmation email, follow-up task), copy the template branch (see below)

### Adding Event-Specific Actions (Copying the Template Branch)

The default workflow sends a Slack notification for every RSVP but does not send emails or create tasks. If you need those for a specific event:

1. Open the workflow and click on the IF/THEN branch (Action 2).
2. Click **Add branch** (or the "+" next to the existing branches).
3. Name the branch after the event (e.g., `NYC ACE Launch Jun 2026`).
4. Set the criteria:
   - **Property:** `event_rsvp_event_name`
   - **Operator:** **contains**
   - **Value:** The canonical event name (e.g., `ACE Launch`)
5. Add actions to the new branch:
   - **Create task** — Title: `{{contact.firstname}} {{contact.lastname}} RSVPed to {Event Name}`, assign to the appropriate rep, due in 2 business days
   - **Send email** — Select the automated confirmation email for this event
6. Save and re-publish the workflow.

> The template branch (`TEMPLATE - Copy for event-specific actions`) is a visual reference. Do NOT modify or delete it — it serves as a pattern for future branches. Its filter value (`TEMPLATE_DO_NOT_DELETE`) ensures it never matches a real contact.

### When Removing Event-Specific Actions

After an event is over and you no longer need the event-specific branch:

1. Open the workflow and click on the IF/THEN branch.
2. Delete the event-specific branch (NOT the template or catch-all branches).
3. Save and re-publish.

### Quarterly Review

- Verify all active RSVP forms are included in the workflow trigger
- Confirm the Slack integration is still connected
- Review the `RSVP | Unprocessed` list -- if it is growing without being processed, investigate the Google Sheet processor
- Archive old event forms that are no longer active
- Remove IF/THEN branches for past events that no longer need specific actions

---

## Troubleshooting

| Problem                                                   | Cause                                                         | Fix                                                                  |
| --------------------------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------- |
| Contact submitted form but did not enter workflow         | Form not listed in workflow trigger                           | Edit workflow triggers, add the missing form                         |
| Contact entered workflow but was not added to static list | List ID mismatch or list was deleted                          | Verify list ID 1775 exists and is a static list                      |
| Slack notification not sending                            | Slack app disconnected or channel permissions changed         | Go to Settings > Integrations > Slack and reconnect                  |
| Contact only entered workflow once despite multiple RSVPs | Re-enrollment is not enabled                                  | Edit workflow, go to Re-enrollment tab, toggle ON                    |
| Event-specific branch not firing                          | Filter value doesn't match `event_rsvp_event_name` on contact | Check capitalization, extra spaces in the hidden field default value |
| Template branch firing unexpectedly                       | Someone changed the filter value from TEMPLATE_DO_NOT_DELETE  | Reset the template branch filter value to `TEMPLATE_DO_NOT_DELETE`   |
| Email action shows "email not found"                      | Automated email was deleted or is in draft state              | Recreate the email or publish it as an automated email               |
