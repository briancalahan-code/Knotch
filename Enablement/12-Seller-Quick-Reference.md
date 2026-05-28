# Seller Quick Reference Card

**Audience:** Sellers | **Topics:** cheat sheet, daily checklist, key numbers, stages, hygiene, tools, quick reference | **Last Updated:** May 2026

**One-page reference for daily deal management and weekly priorities.**

---

## Weekly Checklist (Friday, 15 min)

- [ ] Update **amount, stage, forecast category, next step, close date** for every open deal
- [ ] Open **Deal Pipeline Hygiene dashboard** (Reporting > Dashboards), filter to your name, resolve all flags
- [ ] Confirm all **calls, emails, meetings** from the week are logged on correct deal records

---

## After Every Meeting (1-Hour Window)

- [ ] **Finalize Granola notes** in the meeting template (Otter transcript auto-attaches to HubSpot)
- [ ] Verify Otter meeting record is on the **correct deal** in HubSpot
- [ ] Add any **new contacts**, assign **buying role** in the Buying Group
- [ ] Update **SPICED fields** if you learned something new
- [ ] Update **Buying Group org chart** if reporting lines became clearer
- [ ] Update **next step and next step date**
- [ ] Use **Claude** to speed up: pull notes, suggest SPICED updates, identify missing contacts

---

## Before Every Pipeline Review

- [ ] All **deal basics current** (no past-due close dates, no stale next steps)
- [ ] **Zero hygiene flags** on your deals
- [ ] **Buyer roles assigned** for all associated contacts
- [ ] **Forecast categories reflect honest assessment**

---

## Key Numbers

| Metric               | Target                                           |
| -------------------- | ------------------------------------------------ |
| **Annual Quota**     | $1.1M ($500K NB + $600K R&E)                     |
| **IPM Target**       | 6/month ($400 kicker each = $28.8K/year)         |
| **Win Rate**         | 47.2% blended                                    |
| **Avg NB Land Size** | Tier I: $167K / Tier II: $129K / Tier III: $131K |
| **Target Accounts**  | 1,112 (59% uncontacted)                          |
| **Sales Cycle**      | ~60 days target                                  |

---

## Pipeline Stages (In Order)

**IPM** → **Qualification** → **Consensus** → **Proposal** → **Procurement** → **Closed Won/Lost**

---

## Minimum Contacts by Stage

| Stage         | Min Contacts |
| ------------- | ------------ |
| IPM           | 1–2          |
| Qualification | 2–3          |
| Consensus     | 3–5          |
| Proposal      | 4–6+         |
| Procurement   | 5+           |

**No single-threaded deals past Qualification.**

---

## Hygiene Tags (Goal: Zero Flags)

**Auto-flagged issues that block deal close:**

- **No Amount** — Missing deal size
- **Stalled** — Same stage for 45+ days
- **Zombie** — No activity for 45+ days
- **No Recent Activity** — No activity for 21+ days
- **No Contacts** — Zero contacts on deal
- **Single Threaded** — One contact at Qual+ stage
- **Stale Next Steps** — Next step date in past
- **Past-Due Close** — Close date passed, deal open
- **IPM Stale** — In IPM stage 14+ days without advancing
- **No Line Items** — Past IPM with no line items attached

**Action:** Review hygiene dashboard Friday; resolve all flags same day.

---

## Lead Status Values

| Status               | Meaning                                                                       |
| -------------------- | ----------------------------------------------------------------------------- |
| **Cold**             | No outreach yet                                                               |
| **Attempted**        | Outreach sent, no reply                                                       |
| **Connected**        | Conversation started                                                          |
| **Meeting Booked**   | IPM or meeting scheduled                                                      |
| **Open Opportunity** | Active deal                                                                   |
| **Bad Fit**          | Doesn't match ICP                                                             |
| **Left Company**     | No longer at the company — suppress from outreach, re-enrich to find new role |
| **Junk**             | Invalid record (spam, test data, non-person)                                  |

**Hierarchy:** Lead status only moves up: Cold → Attempted → Connected → Meeting Booked → Open Opportunity. Workflows enforce this — a Connected contact cannot regress to Attempted. Bad Fit, Left Company, and Junk are terminal statuses outside the progression.

---

## Buying Roles (Assign to Every Contact)

Decision Maker | Economic Buyer | Champion | Executive Sponsor | Influencer | Technical Buyer | End User | Blocker | Legal & Compliance | Procurement | AI Governance/Risk

---

## SPICED (Update as You Learn)

| Component             | Definition                                                                                   |
| --------------------- | -------------------------------------------------------------------------------------------- |
| **Situation**         | Current state, business context, team structure                                              |
| **Pain**              | Problems they're facing (measurement gaps, attribution blindness, content underperformance)  |
| **Impact**            | Business impact of not solving (revenue at risk, wasted spend, missed opportunities)         |
| **Critical Event**    | What's driving urgency? (budget cycle, Q planning, new initiative, leadership change)        |
| **Decision Criteria** | How will they evaluate? (price, implementation time, features, vendor stability, references) |

---

## Tools & Access

| Tool                          | Primary Use                                                                                                                                                                                                                                                                                     |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **HubSpot** (Portal 44523005) | Deal, contact, company data (single source of truth)                                                                                                                                                                                                                                            |
| **Otter.ai**                  | Meeting recording + transcription. Auto-creates meeting in HubSpot, attaches notes.                                                                                                                                                                                                             |
| **Granola**                   | Live note-taker. Run during every meeting. 1-hour window to finalize into template. Notes attach to contact/account/deal.                                                                                                                                                                       |
| **Claude**                    | AI assistant. Connected to Granola, HubSpot, and all tools. Ask questions, prep for meetings, take actions. See **15-AI-Skills-and-Knotch-MCP.md** for full skill reference (Deal Analysis, Call Prep, RevOps Documentation) and MCP tool details.                                              |
| **Apollo**                    | Prospecting (find contacts), enrichment (phone/email), outbound sequences                                                                                                                                                                                                                       |
| **Contact Enrichment Sheet**  | Self-service contact lookup, enrichment, email validation, push to HubSpot ([Sheet](https://docs.google.com/spreadsheets/d/1n_m-0GODGS0Lj9OCm_HENahzFvVVIND11zVgqcE-6wo/edit?usp=sharing) \| [Walkthrough](https://drive.google.com/file/d/18C23TcPByFHDiJSrj1rUllDoneNF7eIU/view?usp=sharing)) |
| **HubSpot Breeze**            | Native enrichment (firmographics)                                                                                                                                                                                                                                                               |

**Enrichment Stack:** Apollo + Enrichment Sheet | **Meeting Stack:** Otter.ai + Granola | **AI Assistant:** Claude

**Enrichment Fields on Contact Records:**

- **`employment_history`** — JSON array of past and current companies from Apollo. Shows full career history (company, title, start/end dates, current flag). Use this to identify warm intro paths through shared employers or to understand a contact's background before outreach.
- **`apollo_id`** — Stored on contact records for instant Apollo lookups. Enables direct enrichment without name/email matching.

---

## Account Prioritization

Start with **Tier I accounts** and those showing **recent engagement signals** (website visits, content interactions, or leadership changes). Research company news and initiatives to tailor outreach.

---

## Personas (15 Defined)

**Primary Targets:**

- Content/Demand Gen Specialist
- CMO / VP Marketing
- Digital Marketing Manager/Director
- Brand Manager/Director
- IT/Analytics/MarTech Leader

Personas auto-assigned via HubSpot based on job title (92.8% accuracy). Override if misclassified.

---

## Account Segmentation

| Tier         | Size             | Accounts  | Focus                        |
| ------------ | ---------------- | --------- | ---------------------------- |
| **Tier I**   | Enterprise       | ~50–80    | Highest touch, largest deals |
| **Tier II**  | Mid-Market       | ~300–400  | Expansion economics (3x LTV) |
| **Tier III** | Upper Mid-Market | Remainder | Volume play                  |

**Territory:** ~275–300 accounts per AE (80% geography-based + tier mix balance).

---

## Sales Process Basics

**Sales Methodology:** SPICED (Situation, Pain, Impact, Critical Event, Decision Criteria)

**ICP:** Enterprise/upper-mid-market brands with significant content and digital marketing investment. Dedicated content and marketing teams.

**Product:** Content intelligence platform measuring content ROI across owned and paid channels.

**Products:** Knotch One | ACE | K1 | Content Catalysts | JCI | KSC | AIQ | EQ/IQ

---

## Reporting Access

**Path:** HubSpot → Reporting → Dashboards → **Deal Pipeline Hygiene**

**Dashboard ID:** 19333613 | **Portal:** 44523005

**Reports Included:**

- Tag Counts + Pipeline Overview KPI
- Hygiene by Rep + No Contacts
- Past-Due Close + No Amount
- No Recent Activity + Stalled
- Zombie + Stale Next Steps
- Single-Threaded

Use quick filter to view only your deals.

---

## Events

Events follow a six-step lifecycle managed by RevOps. As a seller, your touchpoints are:

- **Step 1:** Align on invite list — flag accounts you want included or excluded
- **Step 4a:** Owner follow-up — you may get a task to personally follow up with your accounts after invites go out
- **Step 5:** RSVPs hit Slack in real-time — watch for your accounts accepting
- **Step 6a:** Post-event follow-up — you may get a task to follow up with attendees or no-shows

Event Attendance records and timeline notes are created automatically on every contact. Lists are auto-generated by status (Attended, No Show, etc.).

**Full lifecycle:** Documentation/Events/Event-Lifecycle.md

---

## Pro Tips

1. **Friday scrub eliminates 90% of issues.** Make it a habit.
2. **Otter records, Granola refines, you finalize.** Meeting notes auto-flow to HubSpot. Your job is the 1-hour refinement into the template.
3. **Use Claude before every meeting.** Ask it to summarize the account, pull last meeting notes, and flag missing SPICED fields.
4. **Enrichment matters.** Phone coverage drives outbound effectiveness.
5. **Research-based personalization wins.** Use company news, LinkedIn insights, and market research to tailor outreach.
6. **Start with your book.** 59% of accounts are uncontacted; exhaust existing territory first.
7. **Multiple contacts = deal survives.** No single-threaded deals past Qualification.
8. **SPICED guides discovery.** Update it after every call to build your case for close.
9. **Honest forecasts = credible conversations.** Don't sandbag or overstate in reviews.

---

## Contact Info

**Sales Manager:** [Your Manager] — Territory, accounts, coaching
**Sales Operations:** Sales enablement, reports, CRM issues
**RevOps / IT:** Tool access, Apollo support, Enrichment Sheet questions

---

## Related Documents

- **Deal Process and SPICED** (03) — Full SPICED methodology and stage exit criteria
- **Pipeline Hygiene and Scoring** (04) — Hygiene tag details and pipeline scoring model
- **Seller Tool Setup** (16) — Tool installation and configuration guide
