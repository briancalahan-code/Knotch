# Knotch GTM Enablement Library

**17 documents covering everything a seller, admin, or RevOps team member needs to operate the Knotch GTM engine.** This is the canonical reference for pipeline process, CRM standards, enrichment, tooling, and sales methodology.

Source of truth: the local repo (`/Knotch/Enablement/`). This Google Drive folder is a read-only mirror — edits happen in the repo and sync to Drive.

---

## Start Here (by Role)

**Seller (AE / SDR):**
01 GTM Overview → 12 Seller Quick Reference → 03 Deal Process & SPICED → 05 Buyer Personas → 08 Prospecting & Outbound → 16 Seller Tool Setup

**RevOps / Admin:**
01 GTM Overview → 02 CRM Architecture → 09 Workflow Automation → 07 Data Enrichment → 04 Pipeline Hygiene → 17 Admin Tool Configuration

**Marketing:**
01 GTM Overview → 05 Buyer Personas → 06 Territory & ICP → 14 Event & Webinar Lists → 10 Reporting & Dashboards

**Intern (Prospecting / Research):**
18 Intern Targeting Playbook → 05 Buyer Personas → 08 Prospecting & Outbound → 06 Territory & ICP → 11 Onboarding FAQ

---

## Knowledge Map

Documents are grouped by topic cluster. The "Related To" column shows which other docs are most closely connected.

### Process & Methodology

| #   | Document                     | What It Covers                                                              | Related To |
| --- | ---------------------------- | --------------------------------------------------------------------------- | ---------- |
| 03  | Deal Process and SPICED      | SPICED framework, pipeline stages, stage exit criteria, forecast categories | 04, 05, 12 |
| 04  | Pipeline Hygiene and Scoring | 10 hygiene tags, pipeline scoring model, Deal Hygiene Dashboard             | 03, 10, 12 |
| 12  | Seller Quick Reference       | Daily checklists, key metrics, stage summary, hygiene flags at a glance     | 03, 04, 16 |

### People & Market

| #   | Document                            | What It Covers                                                                  | Related To     |
| --- | ----------------------------------- | ------------------------------------------------------------------------------- | -------------- |
| 05  | Buyer Personas and Buying Committee | 15 personas, 11 buying roles, seniority levels, HubSpot Buying Groups           | 03, 06, 08     |
| 06  | Territory and ICP Tiering           | ICP scoring (v3 four-pillar model), Tier I/II/III economics, territory rules    | 05, 08, 02     |
| 08  | Prospecting and Outbound            | Apollo prospecting, role clusters, outbound sequences, buying committee mapping | 05, 06, 07, 13 |

### Data & Events

| #   | Document                          | What It Covers                                                                    | Related To          |
| --- | --------------------------------- | --------------------------------------------------------------------------------- | ------------------- |
| 07  | Data Enrichment Playbook          | Apollo, Clay, Breeze enrichment architecture, email verification, phone waterfall | 08, 02, 14          |
| 14  | Event and Webinar List Management | Event Attendance system, Google Sheet processor, list naming, RSVP workflow       | 07, 09, Events SOPs |

### Systems & Tools

| #   | Document                       | What It Covers                                                                  | Related To |
| --- | ------------------------------ | ------------------------------------------------------------------------------- | ---------- |
| 02  | CRM Architecture and Standards | HubSpot object model, lifecycle stages, properties, naming conventions          | 03, 07, 09 |
| 09  | Workflow Automation Reference  | All HubSpot workflows: persona, seniority, deal hygiene, ownership, RSVP        | 02, 04, 14 |
| 10  | Reporting and Dashboards       | Dashboard IDs, report cadences, leadership metrics, self-service access         | 04, 03     |
| 16  | Seller Tool Setup              | Step-by-step setup: HubSpot, Otter, Granola, Apollo, Claude, Enrichment Sheet   | 12, 17     |
| 17  | Admin Tool Configuration       | Admin-side config: HubSpot portal, Granola workspace, Apollo org, Otter, Claude | 16, 09, 02 |

### AI & Automation

| #   | Document                 | What It Covers                                                                     | Related To |
| --- | ------------------------ | ---------------------------------------------------------------------------------- | ---------- |
| 15  | AI Skills and Knotch MCP | Three Claude skills (Deal Analysis, Call Prep, RevOps Docs), MCP server, workflows | 12, 16, 17 |

### Getting Started

| #   | Document                  | What It Covers                                                                      | Related To     |
| --- | ------------------------- | ----------------------------------------------------------------------------------- | -------------- |
| 01  | Knotch GTM Overview       | Company, product, engagement scope, team, workstreams                               | All docs       |
| 11  | Onboarding FAQ            | Common new-rep questions organized by topic                                         | 01, 03, 12, 16 |
| 18  | Intern Targeting Playbook | ICP guide for interns: company/people targeting, win/loss patterns, daily workflows | 05, 06, 08, 11 |

### Supplemental (Word Documents)

| #   | Document                                           | What It Covers                                            | Related To |
| --- | -------------------------------------------------- | --------------------------------------------------------- | ---------- |
| 13  | Apollo Seller Reference Guide (.docx)              | Apollo tool usage for reps: search, sequences, enrichment | 08, 07     |
| —   | Knotch Personas and Buying Roles One-Pager (.docx) | Visual persona/role reference card                        | 05         |

---

## Document Index

| #   | File                                            | One-Line Summary                                                              |
| --- | ----------------------------------------------- | ----------------------------------------------------------------------------- |
| 01  | 01-Knotch-GTM-Overview.md                       | Company, product, engagement scope, and GTM workstreams                       |
| 02  | 02-CRM-Architecture-and-Standards.md            | HubSpot object model, properties, lifecycle stages, naming rules              |
| 03  | 03-Deal-Process-and-SPICED.md                   | SPICED methodology, pipeline stages, exit criteria, forecast categories       |
| 04  | 04-Pipeline-Hygiene-and-Scoring.md              | 10 hygiene tags, scoring model, Deal Hygiene Dashboard                        |
| 05  | 05-Buyer-Personas-and-Buying-Committee.md       | 15 personas, 11 buying roles, seniority, HubSpot Buying Groups                |
| 06  | 06-Territory-and-ICP-Tiering.md                 | ICP scoring, Tier I/II/III economics, territory assignment rules              |
| 07  | 07-Data-Enrichment-Playbook.md                  | Apollo + Clay + Breeze enrichment, email verification, phone waterfall        |
| 08  | 08-Prospecting-and-Outbound.md                  | Outbound plays, role clusters, Apollo sequences, buying committee mapping     |
| 09  | 09-Workflow-Automation-Reference.md             | All HubSpot workflows: persona, seniority, deal hygiene, ownership, RSVP      |
| 10  | 10-Reporting-and-Dashboards.md                  | Dashboard IDs, report cadences, leadership and rep-level metrics              |
| 11  | 11-Onboarding-FAQ.md                            | Common questions from new sellers, organized by topic                         |
| 12  | 12-Seller-Quick-Reference.md                    | One-page daily cheat sheet: checklists, key numbers, stages, tools            |
| 13  | 13-Apollo-Seller-Reference-Guide.docx           | Apollo tool usage guide for sales reps                                        |
| 14  | 14-Event-and-Webinar-List-Management.md         | Event Attendance system, Google Sheet processor, list naming, RSVP workflow   |
| 15  | 15-AI-Skills-and-Knotch-MCP.md                  | Claude skills (Deal Analysis, Call Prep, RevOps Docs), MCP server reference   |
| 16  | 16-Seller-Tool-Setup.md                         | Step-by-step tool setup for sellers (HubSpot, Otter, Granola, Apollo, Claude) |
| 17  | 17-Admin-Tool-Configuration.md                  | Admin-side tool config (HubSpot, Granola, Apollo, Otter, Claude)              |
| 18  | 18-Intern-Targeting-Playbook.md                 | ICP guide for interns: company/people targeting, win/loss patterns, workflows |
| —   | Knotch-Personas-and-Buying-Roles-One-Pager.docx | Visual persona and buying role reference card                                 |

---

## Also in This Drive

The **Documentation/** folder contains detailed specs, implementation docs, and SOPs that the enablement docs reference:

- **Documentation/CRM/** — Ownership rules, pipeline consolidation, SPICED exit criteria matrix, CRM processes
- **Documentation/Events/** — Event Lifecycle, New Event Checklist, Post-Event Processing, RSVP Workflow Setup, Event Management Job Aid
- **Documentation/Workflows/** — Workflow build specs (persona, seniority, ownership enforcement)
- **Documentation/Dashboards/** — Dashboard build spec, QA reports
- **Documentation/Enrichment/** — Clay strategy, Apollo strategy, enrichment field mapping

---

## How to Use This Knowledge Base

**Browsing:** Start with the reading path for your role (above), then follow the "Related To" links in the Knowledge Map to explore connected topics.

**Searching:** Use document titles and topic keywords. Each document has audience and topic tags in its header to help identify the right file.

**AI skill:** The `knotch-gdrive` Claude skill can retrieve and answer questions from these documents. Ask it about any topic — it routes to the right doc using the topic keywords.

**Formats:** Most files are Markdown (`.md`) — readable as plain text. Two supplemental files are Word (`.docx`). Excel/CSV data files referenced in the docs live in the `Documentation/` subfolders.
