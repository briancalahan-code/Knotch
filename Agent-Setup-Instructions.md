# Knotch Agent Setup Instructions

How to get each person's daily agent running. Takes about 15 minutes per person.

---

## Prerequisites (Brian does once)

1. **Granola Enterprise/Business plan** enabled for the workspace
2. **Shared "Client Notes" folder** created in Granola's Team space
3. **Brian added as a member** of the Client Notes folder (so Agent 3 can read it)
4. **Granola MCP** enabled in workspace settings (Enterprise admin toggle)
5. **HubSpot MCP** connected to each person's Claude account
6. **Slack MCP** connected to each person's Claude account

---

## Per-Person Setup (each AE does this)

### Step 1: Create Google Docs (5 min)

1. Open Google Drive
2. Create a folder: **My Drive > Granola** (if it doesn't exist)
3. Inside that folder, create two Google Docs:
   - **To-dos** -- leave it blank, the agent will populate it on first run
   - **Top Priorities** -- add your top 3-5 priorities right now (deals you care about, deadlines, focus areas). One line each.
4. Copy the sharing URL for each doc (click Share > Copy Link). Make sure it's set to "Anyone with the link can edit" OR share directly with the Claude/automation account.

**Save these two URLs -- you'll need them for Step 3.**

### Step 2: Connect Granola MCP (5 min)

1. Open Claude on your machine
2. Go to Settings > MCP Servers (or equivalent)
3. Add the Granola MCP connector
4. Authenticate with your Granola account (OAuth)
5. Verify it works: ask Claude "list my recent Granola meetings" -- you should see your meetings

### Step 3: Create the Scheduled Task (5 min)

1. Open Claude on your machine
2. Type: `/schedule`
3. Or ask Claude: "Create a scheduled task called daily-brief"
4. Set the schedule: **Weekdays at 8:00 AM** (cron: `0 8 * * 1-5`)
5. For the prompt, paste the contents of `Combined-Daily-Agent-Prompt.md`
6. **Before pasting, fill in your row** in the Team Configuration table at the top:

```
| Pete Davies | 87170480 | https://docs.google.com/document/d/YOUR_TODOS_ID | https://docs.google.com/document/d/YOUR_PRIORITIES_ID |
```

Replace `[PASTE URL]` with your actual Google Doc URLs from Step 1.

7. Save and enable the task

### Step 4: Test It (2 min)

1. Run the scheduled task manually once
2. Check that:
   - You get a Slack DM with your daily brief
   - Your To-dos Google Doc has a new date header with any action items from yesterday
   - The nudge message appears in Slack if you had external meetings yesterday
3. If anything is off, check:
   - Is Granola MCP connected? (try `list_meetings` manually)
   - Is HubSpot MCP connected? (try searching for your deals)
   - Are the Google Doc URLs correct and accessible?

---

## Team Configuration Reference

Fill in each person's Google Doc URLs as they set up:

| Name              | HubSpot Owner ID | To-dos Doc URL | Top Priorities Doc URL |
| ----------------- | ---------------- | -------------- | ---------------------- |
| Pete Davies       | 87170480         |                |                        |
| Jason [LAST NAME] | [OWNER ID]       |                |                        |
| Don Vanderslice   | 693091902        |                |                        |

---

## Agent 3: HubSpot Sync (Brian only)

This is a separate scheduled task that only Brian runs. It reads the shared Client Notes folder and syncs meeting notes to HubSpot.

### Setup

1. Open Claude on Brian's machine
2. Create a scheduled task: `knotch-hubspot-sync`
3. Schedule: **Every 30 min, weekdays 8 AM - 7 PM** (cron: `*/30 8-19 * * 1-5`)
4. Paste the contents of `Agent-3-HubSpot-Sync-Prompt.md` as the prompt
5. Verify Brian's Granola MCP can see the Client Notes shared folder:
   - Ask Claude: "list my Granola meeting folders"
   - Confirm "Client Notes" appears in the list
6. Test by having someone share a meeting note to Client Notes, then run the task manually

---

## Troubleshooting

**"No Granola meetings found"**

- Is Granola MCP connected? Check Settings > MCP
- Are you on Business or Enterprise plan? Free/Basic has limited MCP access
- Did you have meetings yesterday? Check Granola directly

**"No HubSpot deals found"**

- Is HubSpot MCP connected?
- Check your HubSpot Owner ID is correct (ask Brian if unsure)
- Do you actually have open deals in the New/Expansion pipeline?

**Brief doesn't arrive in Slack**

- Is Slack MCP connected?
- Check the Slack user ID lookup -- sometimes names don't match exactly

**Google Doc not updating**

- Is the doc URL correct?
- Is sharing set to "Anyone with the link can edit"?
- Check if the Google Drive MCP has write permissions

**Agent 3 can't see Client Notes folder**

- Is Brian a member of the shared folder in Granola?
- Has the folder been created in Granola's Team space?
- Try: "list my Granola meeting folders" -- does Client Notes appear?
