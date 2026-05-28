# AI Skills and Knotch MCP Reference

**Audience:** All roles | **Topics:** Claude, AI skills, MCP, Deal Analysis, Call Prep, RevOps Documentation | **Last Updated:** April 2026

---

## Executive Summary

Three AI skills cover the deal lifecycle end-to-end. They're powered by the Knotch MCP, a Model Context Protocol server that gives Claude direct, scoped access to HubSpot, Apollo, and Clay.

| Skill                    | When                               | What It Does                                      |
| ------------------------ | ---------------------------------- | ------------------------------------------------- |
| **Call Prep**            | Before the meeting                 | Research, attendees, objectives, business case    |
| **Deal Analysis**        | After the meeting / pipeline scrub | CRM hygiene, buying committee, stage progression  |
| **RevOps Documentation** | Anytime                            | Process reference — stages, SPICED, personas, ICP |

A typical week: run Call Prep before each external call, run Deal Analysis as part of Friday pipeline scrub, hit RevOps Docs anytime someone asks "what does that stage actually require?"

---

## Skill 1: Deal Analysis

### What It Does

Pulls everything HubSpot knows about a deal — contacts, meetings, emails, company context, stage requirements — in a single call, then reads the actual email and meeting bodies to surface insights you can't get from CRM fields alone. Finally, it offers to push confirmed changes back to HubSpot (associations, buyer roles, property updates).

### When to Use It

Pre-call prep, deal reviews, weekly forecast scrub, account planning, anytime you need to assess deal health beyond what's in the deal record.

### What You Get Back

- **Buying committee map** — who's on the deal, what role they should play (Champion, Economic Buyer, Technical Validator, Influencer, End User, Blocker, Executive Sponsor), and the evidence (a quote from an email or meeting note, not just a title).
- **Gap contacts** — people who showed up in meetings or email threads but aren't associated to the deal yet, prioritized CRITICAL to LOW.
- **SPICED scorecard** — element-by-element comparison of what the deal record says vs. what activity actually reveals, with the gap called out explicitly. See Document 03 (Deal Process and SPICED) for full SPICED definitions and stage exit criteria.
- **Stage gap analysis** — required vs. missing roles for the current stage, single-threading risk, contact-count check against the Knotch framework (IPM > Qualification > Consensus > Proposal > Procurement). See Document 12 (Seller Quick Reference) for minimum contact counts by stage.
- **Flags** — departed contacts, zero-engagement contacts, leadership changes to investigate.

### Why It Matters

Evidence-based, not title-based. A "VP" with zero notes doesn't get auto-assigned Economic Buyer; an analyst with 100 notes who asks about pricing does get flagged as Champion. It also filters out internal Knotch employees so you never label your own team as buyers. CRM write-back is grouped (associations, then buyer roles, then record cleanup) and always confirms before writing.

---

## Skill 2: Call Prep

### What It Does

Generates a tight, source-backed prep brief for any upcoming customer or prospect meeting — the kind of doc you can read in 5 minutes and walk in confident. Patterned on the Cox Automotive / ACE prep doc the team already uses. Outputs a `.docx` ready to share or upload to Drive.

### When to Use It

Before any external call where prep matters — prospect discovery, demos, follow-ups, working sessions, report scoping, upsell IPMs, partnership reviews, QBRs, check-ins, escalations.

### How It Works

Five steps: gather inputs (who, prospect vs. customer, call type, objectives, products), pull the meeting from Google Calendar if asked, run parallel research across the right sources for the meeting type, build the doc, deliver as `.docx`.

The skill calibrates source priority by meeting type:

| Meeting Type                | Source Priority (highest first)              |
| --------------------------- | -------------------------------------------- |
| **Prospect calls**          | Web > Drive > Otter > HubSpot > Gmail > Jira |
| **Existing customer calls** | Otter > HubSpot > Gmail > Jira > Drive > Web |

Prospect calls build a picture from the outside in. Customer calls walk you in already knowing what was said and what was promised.

### What's in the Brief

- **Meeting overview** with attendee table
- **Call objectives**
- **Business context** — strategic priorities + their website/content KPIs (not their product's metrics)
- **Account Health** (existing customers only)
- **Prior Call Context** with verbatim quotes from Otter/Granola
- **Mini Business Case** grounded in the specific product being discussed
- **3-5 Suggested Questions** tailored to the call type
- **Deduplicated Sources list** — every factual claim hyperlinked to its origin (Otter recording, Drive doc, web page, HubSpot record, Gmail thread)

### Sourcing Rules

The doc is sourcing-strict. Unverifiable claims are labeled "(inferred)" or cut. Call type drives emphasis: a working session focuses on blockers and unmet commitments, a partnership review surfaces renewal health and contract scope, an upsell IPM treats the new product like a mini-prospect motion. No padded sections — if Otter has nothing for a net-new prospect, the doc says so and moves on.

### Common Pitfalls It Avoids

- Don't assume product focus — always ask
- Don't confuse current products with upsell targets
- Don't reuse prospect questions on existing customers
- Don't skip the renewal date
- Don't confuse the customer's product KPIs with their website KPIs

---

## Skill 3: Knotch RevOps Documentation

### What It Does

Acts as a live reference desk for Knotch GTM process — pipeline stages, SPICED exit criteria, personas, ICP tiering, CRM architecture, ownership rules, enrichment playbook, workflow automation, deal hygiene definitions. Pulls answers directly from the canonical docs in the Knotch Google Drive shared folder so you're always reading the current version.

### When to Use It

- "What's the exit criteria for Consensus?"
- "Which personas live in Tier I?"
- "What does 'Stalled Deal' mean on the hygiene dashboard?"
- Onboarding questions, process clarifications, settling debates about what a stage gate actually requires.

### How It Answers

Routes the question to the right document via a topic map, pulls the specific section (not the whole doc), and cites with a live Drive link every time. Includes a built-in fallback: if Drive MCP isn't connected, it walks you through reconnecting and meanwhile answers from embedded definitions for the most common asks (pipeline stages, SPICED elements, the seven buying roles, ICP tier benchmarks, the ten hygiene tags).

### Why It Matters

One source of truth for "how Knotch sells" — no more conflicting answers across reps, no more guessing what a stage means.

---

## Knotch MCP

### What It Is

A Model Context Protocol server that gives Claude direct, scoped access to the Knotch HubSpot portal (44523005) plus the enrichment stack (Apollo + Clay). It's the engine behind Deal Analysis and a key data source for Call Prep — but you can also call its tools directly when you want a one-off lookup, enrichment, or CRM update without going through a full skill workflow.

### Why It Exists

1. **Fast** — `deal_analysis` pulls deal metadata, contacts, gap contacts, full email and meeting bodies, company context, and stage requirements in a single parallel fetch instead of a dozen serial HubSpot calls.
2. **Write-aware** — every write tool is scoped to a specific record type (contact, deal, company, association) so Claude can't accidentally clobber unrelated data.
3. **Workflow-aware** — lookup tools return `next_step` and `suggested_actions` fields so Claude (or you) always knows what to do next.

### Architecture

- **Read tools** fetch from HubSpot, Apollo, and Clay
- **Write tools** push only to HubSpot
- **Enrichment tools** coordinate Apollo and Clay automatically and write results back to HubSpot
- Clay enrichment is async with a 50-second wait; if it times out, you get a correlation ID to poll later
- Apollo returns **employment history** (JSON array with company, title, start, end, current fields) and **Apollo ID** for direct lookups — stored on contact records as `employment_history` and `apollo_id`

### Enrichment Coverage (as of May 2026)

| Data Point             | Contacts | Coverage |
| ---------------------- | -------- | -------- |
| **Employment History** | 11,403   | ~97%     |
| **Apollo ID**          | 11,500   | ~97%     |

Apollo ID on a contact record bypasses name/email matching entirely, enabling instant lookups via `lookup_contact`.

---

### The 13 Tools

#### Contact Lookup (Read-Only)

| Tool                      | What It Does                                                                                               | Key Inputs                                                                                        | Returns                                                                                                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `find_contact_by_details` | Find a contact by name + any combination of company, email, or LinkedIn URL. More inputs = better match.   | first_name, last_name, optional company / email / linkedin_url                                    | Best match with data quality warnings (company_changed, personal_email, email_risky, thin_record), next_step, suggested_actions, and alternate candidates |
| `find_contacts_by_role`   | Find people at a company by job title and optional seniority filter.                                       | titles[], company, optional seniority (c_suite / vp / director / manager / senior / entry), limit | Top candidates ranked by fit, with HubSpot status                                                                                                         |
| `lookup_contact`          | Fetch a full contact record by Apollo ID. Use after `find_contact_by_details` returns multiple candidates. | apollo_id                                                                                         | Full contact record + HubSpot status check                                                                                                                |
| `find_phone`              | Phone-only lookup from cached Apollo data.                                                                 | At least one of apollo_id, email, linkedin_url + name                                             | Phone number if cached; suggests `clay_enrich` if not                                                                                                     |

#### Enrichment (Read + Write)

| Tool                | What It Does                                                                                                                                                                                                                                                                                                                                                                 | Key Inputs                                                                                    | Returns                                                  |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `enrich_contact`    | Fill empty HubSpot fields (jobtitle, phone, LinkedIn, location, company, employment history) from Apollo + Clay. Writes results back to HubSpot. Apollo now returns employment history as a JSON array (company, title, start, end, current fields) and Apollo ID for direct lookups. See Document 07 (Data Enrichment Playbook) for the full enrichment stack architecture. | hubspot_contact_id                                                                            | Diff of what was filled                                  |
| `clay_enrich`       | Direct Clay enrichment for phone or email. Waits up to 50s.                                                                                                                                                                                                                                                                                                                  | first_name, last_name, company_domain, optional linkedin_url, requested_data (phone or email) | Enriched data inline, OR a correlationId if it times out |
| `check_clay_result` | Poll for an async Clay result that timed out.                                                                                                                                                                                                                                                                                                                                | correlation_id                                                                                | Enriched data if ready, status pending otherwise         |

#### Deal Intelligence (Read-Only)

| Tool            | What It Does                                                                                      | Key Inputs                | Returns                                                                                                                                                                                |
| --------------- | ------------------------------------------------------------------------------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `deal_analysis` | Parallel data fetcher behind the Deal Analysis skill. Accepts deal ID or deal name (text search). | deal_id (numeric or name) | Deal metadata, all on-deal contacts with engagement, gap contacts, full meeting bodies, full email bodies, company context, other open deals, stage requirements, internal team emails |

This tool is a raw fetcher — not the analysis. The Deal Analysis skill turns this output into the buying-committee map and SPICED scorecard.

#### HubSpot Write-Back

| Tool                        | What It Does                                                                                                                             | Key Inputs                                                                                                      | Returns                       |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `add_to_hubspot`            | Create a contact (or update if email/LinkedIn matches). Creates the company too if it doesn't exist, then associates contact to company. | first_name, last_name, optional email, linkedin_url, company, company_domain, title, phone, location, apollo_id | New or updated contact record |
| `associate_contact_to_deal` | Link an existing contact to a deal. Used after `deal_analysis` surfaces gap contacts.                                                    | contact_id, deal_id                                                                                             | Confirmation                  |
| `update_contact_properties` | Set any HubSpot contact properties via JSON string.                                                                                      | contact_id, properties (JSON)                                                                                   | Updated record                |
| `update_deal_properties`    | Set any HubSpot deal properties via JSON string.                                                                                         | deal_id, properties (JSON)                                                                                      | Updated record                |
| `update_company_properties` | Set any HubSpot company properties via JSON string.                                                                                      | company_id, properties (JSON)                                                                                   | Updated record                |

**Common property keys** (HubSpot internal names, not UI labels):

| Object  | Properties                                                                                                             |
| ------- | ---------------------------------------------------------------------------------------------------------------------- |
| Contact | `hs_buying_role`, `jobtitle`, `lifecyclestage`, `hs_lead_status`, `phone`, `email`, `firstname`, `lastname`, `company` |
| Deal    | `dealname`, `dealstage`, `amount`, `closedate`, `description`, `hubspot_owner_id`                                      |
| Company | `name`, `domain`, `industry`, `numberofemployees`, `annualrevenue`, `description`                                      |

---

### Common MCP Workflows

#### "Find this person and get them into HubSpot"

1. `find_contact_by_details` — search by name, company, email
2. If multiple candidates, show them, let user pick, then `lookup_contact` with chosen Apollo ID
3. If `hubspot_status` is `not_found`, offer `add_to_hubspot`
4. Run `enrich_contact` to fill any remaining gaps

#### "I need a phone number for this person"

1. Try `find_phone` first (cached Apollo data, fast)
2. If nothing, fall back to `clay_enrich` with `requested_data: phone`
3. If Clay times out, save the correlationId and poll with `check_clay_result` later

#### "Find me VPs of Marketing at [Company]"

1. `find_contacts_by_role` with titles: `["VP Marketing"]`, company, seniority: `"vp"`
2. Review candidates, ask which to add
3. `add_to_hubspot` for each selected

#### "Audit this deal"

1. `deal_analysis` with the deal ID
2. Deal Analysis skill interprets the result
3. Push approved changes back: `associate_contact_to_deal` (gap contacts) > `update_contact_properties` (buyer roles) > `update_deal_properties` (description, stage) — one group at a time, always with user confirmation

---

### Workflow Rules

These rules are baked into the MCP to enforce process discipline:

1. **Always follow next_step.** `find_contact_by_details` returns a `next_step` field that adapts to the situation (company_changed = confirm the move, alternate_matches = let user pick, hubspot_status not_found = offer to add). Don't skip these.
2. **Always confirm before writing.** Every write tool requires explicit user approval.
3. **Group write-back changes.** When pushing changes from a Deal Analysis run, do associations first, then buyer roles, then property updates. Bundle changes by category, not by record.
4. **Internal team filtering.** `deal_analysis` returns `internal_emails` (HubSpot portal owners). Never recommend buyer roles for those contacts — they're Knotch employees, not the prospect's buying committee.

---

### Limits and Gotchas

| Limit                | Detail                                                                                                                                       |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Read scope**       | HubSpot portal 44523005, Apollo (Knotch seat), Clay (Knotch workspace). Cannot reach other tenants or personal accounts.                     |
| **Write scope**      | Writes only go to HubSpot. No tool to update Apollo or Clay records.                                                                         |
| **Clay async**       | `clay_enrich` blocks for up to 50s. If callback is slow, you get a correlationId — don't treat as failure, poll with `check_clay_result`.    |
| **Dedup on add**     | `add_to_hubspot` dedupes on email and LinkedIn URL. If the person has neither, you may get a duplicate. Always pass at least one identifier. |
| **Property keys**    | Use HubSpot internal names (`hs_buying_role`, `numberofemployees`, `closedate`), not UI labels.                                              |
| **Deal name search** | `deal_analysis` accepts deal name as text search but matches loosely. If you have the deal ID, use it.                                       |

---

### How the MCP Fits with the Three Skills

| Skill                    | Uses Knotch MCP? | What the MCP Does for It                                                                                                        |
| ------------------------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Call Prep**            | Yes              | HubSpot lookups to enrich attendee table; Account Health data for existing customers                                            |
| **Deal Analysis**        | Yes (heavily)    | `deal_analysis` does the data fetch; write-back tools push approved changes; the skill does interpretation and user-facing flow |
| **RevOps Documentation** | No               | Reads from Google Drive instead — that's where canonical process docs live                                                      |

You can also call any MCP tool directly without invoking a skill. "Find me Sasha Franger's phone" or "associate contact 12345 to deal 67890" both work as plain chat asks.

---

## Installing Skills

### Option 1: Knotch Plugin (Recommended)

Plugin-bundled skills (Deal Analysis, RevOps Documentation, Call Prep) get installed once and become available across Claude Code, Cowork, and team Claude.ai accounts.

1. In Claude Code or Cowork, run `/plugin` to open the plugin manager
2. Browse the marketplace and find the Knotch plugin (or install from the Knotch repo URL if not yet listed)
3. Install — skills, MCPs, and slash commands all activate automatically
4. Verify by running `/help` or asking Claude "what skills are available?" — Deal Analysis, Call Prep, and Knotch RevOps Documentation should all show up

### Option 2: Custom Skills via Claude.ai

Good for testing a skill before bundling it, or sharing a one-off with a teammate.

1. Go to **claude.ai > Settings > Capabilities > Skills**
2. Click **Create Skill**
3. Paste the skill name, description, and full system prompt into the form
4. Save — the skill becomes available in your Claude.ai chats immediately
5. To share: send the skill's prompt text to teammates and have them follow the same steps

### Which to Choose

The plugin route scales better — if Call Prep gets refined, every rep gets the update automatically. Ad-hoc Claude.ai installs drift out of sync quickly. For anything the team should use consistently, get it into the plugin.

---

## Quick Reference: Daily Use

| Moment                              | Action                                                  | Skill/Tool                                              |
| ----------------------------------- | ------------------------------------------------------- | ------------------------------------------------------- |
| Before every external call          | Generate prep brief                                     | **Call Prep**                                           |
| After every meeting (1-hour window) | Finalize Granola notes, update SPICED, add new contacts | Manual + **Deal Analysis** for contact/role suggestions |
| Friday pipeline scrub               | Run against each active deal                            | **Deal Analysis**                                       |
| "What does this stage require?"     | Look it up                                              | **RevOps Documentation**                                |
| Need a phone number                 | Quick lookup                                            | `find_phone` > `clay_enrich`                            |
| Found a new contact to add          | Search, verify, create                                  | `find_contact_by_details` > `add_to_hubspot`            |
| Prospect research                   | Find key people at target account                       | `find_contacts_by_role`                                 |

---

## Cross-References

| Topic                                                | Document                                          |
| ---------------------------------------------------- | ------------------------------------------------- |
| SPICED framework definitions and stage exit criteria | Document 03 — Deal Process and SPICED             |
| Pipeline hygiene tags and scoring                    | Document 04 — Pipeline Hygiene and Scoring        |
| Buying roles and buying committee setup              | Document 05 — Buyer Personas and Buying Committee |
| Enrichment stack architecture (Apollo, Clay, Breeze) | Document 07 — Data Enrichment Playbook            |
| Weekly checklist and seller workflow                 | Document 12 — Seller Quick Reference              |
