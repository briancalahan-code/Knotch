# Knotch GTM Operations Repo

**Client:** Knotch (brian.calahan@knotch.com)
**Managed by:** Brian Calahan, GTM Evolved (VP RevOps, ongoing engagement)
**Repo:** https://github.com/briancalahan-code/Knotch.git
**HubSpot Portal:** 44523005

## What This Is

GTM operations infrastructure for Knotch -- CRM hygiene, data enrichment, territory management, sales enablement, and AI agent coordination. This is an ops/data repo (markdown, Excel, CSV, Word docs, agent prompts), not a code application.

## Environment Variables

- `HUBSPOT_API_KEY` -- HubSpot API access (portal 44523005)
- `APOLLO_API_KEY` -- Apollo enrichment API access
- `CLAY_API_KEY` -- Clay enrichment API access (added 2026-04-04)

## Key Data Points

- **Contacts:** ~11,801
- **Companies:** 2,005
- **Apollo credits:** ~452K remaining of 456K
- **Enrichment baseline:** Pre-enrichment snapshot taken 2026-03-15
- **Unassigned Marketing user:** Owner ID 90107252, unassigned@knotch.com (view-only seat)
- **Clay credits:** Used for April 4 burn (LinkedIn URLs + phone waterfall)
- **Clay Play 1 complete:** 847 LinkedIn URLs enriched and pushed to HubSpot
- **LinkedIn URL coverage:** 10,743 / 11,801 (91.0%) -- 843 added via Clay on 2026-04-04
- **Phone coverage:** 8,686 / 11,801 (73.6%) -- 535 added via Clay on 2026-04-04
- **Email verification:** 10,047 Verified, 1,694 Invalid (Clay/Icypeas loop running daily)

## Active Project: CRM Ownership & Lifecycle Cleanup

**Status:** Awaiting approval from Jason Lee (sent 2026-03-27)
**Deliverable:** Projects/Knotch-CRM-Ownership-Review-Jason-Pete.xlsx
**Full spec:** Documentation/CRM/CRM-Ownership-Lifecycle-Cleanup.md
**Workflows to build:** Documentation/Workflows/CRM-Ownership-Lifecycle-Workflows.md

Pending Jason's thumbs up to execute:

- Reassign ownership by role (CS owns customers, AEs own prospects)
- Fix lifecycle mismatches and consolidate to `account_stage`
- Build 6 enforcement workflows (owner cascade, closed-won lifecycle, etc.)
- Resolve Ben Smith's account ownership (open question for Jason)

## Active Project: Clay Credit Burn (April 4 Deadline)

**Status:** Plays 1-2 complete, Play 3 pending
**Full spec:** Documentation/Enrichment/Clay-Credit-Burn-Strategy.md

- Play 1 (LinkedIn URLs): DONE -- 847 contacts enriched, pushed to HubSpot
- Play 2 (Phone Waterfall): DONE -- 535 phones enriched via Clay, pushed to HubSpot (2026-04-04)
- Play 3 (Multi-Threading): ~6.2K credits, find new contacts at target accounts

## Active Project: LinkedIn Enrichment Round 2 (Automated Drip)

**Status:** Running -- scheduled task `linkedin-enrichment-drip` fires every 5 min
**Tracker:** Projects/Enrichment/linkedin-enrichment-tracker.json
**CSVs:** Projects/Enrichment/Contacts-Missing-LinkedIn-Round2.csv (304 enrichable), Contacts-Missing-LinkedIn-NotWorthEnriching.csv (696 junk)

Automated enrichment of 304 remaining contacts missing LinkedIn URLs:

- Scheduled task runs every 5 minutes, processes 5 contacts per run
- First pass: Apollo bulk people match (name + email + domain + company)
- Second pass: Web search fallback for Apollo misses (site:linkedin.com/in)
- Results pushed directly to HubSpot `hs_linkedin_url` property
- Also captures phone numbers when found
- Tracker JSON tracks status per contact: pending, enriched, enriched_web, no_match, error
- ~60 runs to complete, ~5 hours total

## Integrations

- **HubSpot** -- CRM reads/writes via MCP connector (portal 44523005)
- **Apollo** -- Contact/company enrichment, prospecting data via MCP connector
- **Clay** -- Enrichment workflows, email verification, phone waterfall. API key stored as `CLAY_API_KEY` env var. Clay API can be used for programmatic table creation, enrichment runs, and data pushes.

## Active Project: Email Verification Loop (LIVE)

**Status:** Live and running daily as of 2026-03-27
**Full spec:** Documentation/Enrichment/Clay-Credit-Burn-Strategy.md (Automated Email Verification Loop section)

Automated daily email verification via Clay + Icypeas:

- HubSpot list feeds unverified contacts to Clay daily
- Icypeas verifies, formula translates, Clay writes results back to HubSpot
- Properties: `email_verification_status` (dropdown), `email_last_verified_at` (date), `email_quarantine_status`
- Current: 10,048 Verified, 1,693 Invalid, 0 Catch-all
- HubSpot workflow "Copy Email Verification Result to Status" (ID 1796834461) is OFF (redundant -- Clay writes dropdown directly)
- Apollo deliverability suite is monitoring only (0 sends), not a separate verification system

## Active Project: Executive Reporting System

**Status:** Live
**Files:** Projects/Reporting/

- `Exec-Report-Data-Spec.md` -- Shared data contract (queries, computations, rounding rules)
- `compute_report.py` -- HubSpot API -> deterministic JSON (python3, standalone)
- `Monthly-Exec-Report-Prompt.md` -- Claude prompt for monthly report (sections 1-3)
- `Quarterly-Exec-Report-Prompt.md` -- Claude prompt for quarterly report (sections 1-6)

**Cadence:** Monthly (sections 1-3: Bookings, Activity, Pipeline), Quarterly (adds Market Feedback, Seller Performance, Initiatives)

**QA:** Run `compute_report.py` independently to verify numbers. `--dry-run` shows API calls without executing. Q1 benchmark: $1,102,500 bookings (from Q1 PDF, but live data may drift as deals are modified post-quarter).

**Requires:** `HUBSPOT_API_KEY` env var, python3 with `requests` and `openpyxl` packages, shell access in Claude (CLI or desktop).

## Directory Structure

```
Context/              Master context, CRM audit, GTM overview
  Knotch-GTM-Master-Context.docx
  knotch-crm-audit.html
  Knotch-Target-Account-Audit.xlsx

Documentation/        Organized CRM/GTM documentation
  CRM/
  Events/
  Workflows/
  Dashboards/
  Enrichment/

Projects/             Active project work
  Territory/
  AE_Batch1_Company_Imports/
  Enrichment/
  Event-Processor/
  HubSpot-Imports/
  Apollo-Prospecting/
  Pipeline-Reports/

Enablement/           Sales enablement playbooks (01-12 numbered series)
  01-Knotch-GTM-Overview.md through 12-Seller-Quick-Reference.md

Research/             Enrichment strategies, Apollo planning
Client Files/         Client-provided source files
Archive/              Completed/historical work
```

## AI Agent Prompts

Four agent prompt files live at the repo root:

- `Agent-1-Granola-Organizer-Prompt.md` -- Meeting notes organizer
- `Agent-2-Daily-Brief-Prompt.md` -- Daily GTM briefing
- `Agent-3-HubSpot-Sync-Prompt.md` -- CRM sync agent
- `Agent-ICP-Scoring-Prompt.md` -- ICP/tier scoring agent
- `Agent-Setup-Instructions.md` -- Setup guide for all agents
- `Combined-Daily-Agent-Prompt.md` -- Unified daily agent prompt
- `deal-arena-agent-prompt.md` -- Deal review/coaching
- `deal-hygiene-agent-prompts.md` -- Deal hygiene checks

## Event Tracking

### Event Attendance System (May 2026)

Structured event tracking via a custom object, Google Sheet processor, and HubSpot workflow.

- **Event Attendance custom object:** objectTypeId `2-62279031`. Properties: event_name, event_date, event_status, event_type, event_key, event_source. Associated to contacts.
- **Contact RSVP properties:** `event_rsvp_status`, `event_rsvp_event_name`, `event_rsvp_date` -- "last touch" only (updated if the new event is more recent than the existing value).
- **Google Sheet processor:** "Knotch Event Processor" -- tabs: Event Setup, Attendees, Settings, Log, Reference. Operator interface for loading attendees and triggering processing.
- **Apps Script source:** `Projects/Event-Processor/apps-script/` (10 files: ApolloAPI.gs, Config.gs, Enrichment.gs, HubSpotAPI.gs, ListManager.gs, Logger.gs, ProcessEvent.gs, PullFunctions.gs, TaskManager.gs, UI.gs)
- **Workflow:** `WF | Event | RSVP Processor` (ID 1819563370) -- form trigger adds contacts to `RSVP | Unprocessed` list (ID 1775), sends Slack notification for every RSVP. Dormant template branch available for event-specific email/task actions (copy the template, change the filter to the real event name). Currently enrolled forms: ACE Launch (`6a2aa7f1-7069-45b3-9a91-9c5b64c3cff3`), Cannes Chef's Table (`a9c30aa2-4b50-483f-92cd-51c27b629b57`).
- **Webflow event pages:** Single HTML embed blocks in `Projects/Event-Page-Template/webflow/`. Each embed is a full-page takeover with custom CSS, built-in HubSpot form submission via JS, confirmation card, and AccessiBe widget removal. Clone an existing embed to create new event pages.
- **Enrichment cascade:** HubSpot search by email, then Apollo match (name + email + domain + company), then create contact.
- **Canonical event name format:** `{City/Format} {Event Series} {Mon YYYY}` (e.g., "NYC ACE Launch Jun 2026")
- **List naming:** `EVT_{Event_Name}_{Status}` (in-person) / `WEVT_{Event_Name}_{Status}` (online/webinar), plus `_All` list per event (created automatically by the processor)
- **Form naming:** `RSVP | {Event Name}` with hidden field `event_rsvp_event_name`
- **Event statuses:** Invited, Registered, Confirmed, Attended, No Show, Declined, Waitlisted, Pending Review
- **Backfill complete:** 4,464 Event Attendance records created from 96 legacy lists covering 31 events

### Legacy Data (Pre-May 2026)

- All lists now use unified `EVT_` / `WEVT_` naming (97 backfill lists renamed 2026-05-15)
- Original 43 legacy lists (15 EVT* in-person, 28 WEVT* webinar) predate the processor
- Legacy contact properties (`fy25_event_status`, `fy26_event_attendance`, etc.) capture only ~12% of actual participants -- do NOT rely on these alone
- Script `pull-hubspot-segments.py` pulls list membership via `/crm/v3/lists/{id}/memberships` API

### SOPs and Templates

- **New event setup (includes Webflow page creation):** Documentation/Events/New-Event-Checklist.md
- **Post-event processing:** Documentation/Events/Post-Event-Processing.md
- **RSVP workflow setup:** Documentation/Events/RSVP-Processor-Workflow-Setup.md
- **Event management job aid:** Documentation/Events/Event-Management-Job-Aid.md
- **List management (enablement):** Enablement/14-Event-and-Webinar-List-Management.md

## Key Workflows

1. **CRM Hygiene:** Audit contacts/companies, fix duplicates, standardize fields
2. **Data Enrichment:** Apollo bulk enrichment against HubSpot records, credit tracking
3. **Territory Management:** ICP tiering, AE assignment, account segmentation
4. **Sales Enablement:** Playbooks, talk tracks, buyer personas, SPICED deal process
5. **Pipeline Reporting:** Deal hygiene, win/loss analysis, dashboard data
6. **Ownership & Lifecycle:** Company ownership rules, lifecycle field consolidation, owner cascade workflows
7. **Event Tracking:** Event Attendance custom object, Google Sheet processor, RSVP workflow, list automation

## Working With This Repo

- Excel/CSV files are data artifacts -- read but do not regenerate unless asked
- Word docs (.docx) contain long-form strategy documents
- HTML files are rendered reports/analyses (CRM audit, win/loss, tech stack)
- The Enablement/ series (01-12) is a complete seller onboarding library
- When making changes, respect the existing directory structure above
