# CRM Architecture and Standards

**Audience:** RevOps, Admins | **Topics:** HubSpot, CRM, object model, properties, lifecycle, naming conventions | **Last Updated:** May 28, 2026

---

## Object Model

Knotch's HubSpot environment (Portal 44523005) uses a hierarchical three-object model:

```
Company (Account) → Contact → Deal
                  ↓
             Contact
                  ↓
             Deal
```

### Object Hierarchy

**Company (Account)** – The anchor object representing a prospect or customer organization. All enrichment, firmographic data, and account-level intelligence flow to the company record.

**Contact** – Individual stakeholder at a company. Each contact associates to:

- **One company** (primary company relationship)
- **One or more deals** (buying group membership)

**Deal** – Opportunity record representing a sales opportunity with a specific company. Deals track pipeline progression, revenue, and decision criteria.

**Event Attendance** – Custom object (objectTypeId `2-62279031`) representing a contact's participation in a Knotch event. Each record stores event_name, event_date, event_status, event_type, and is associated to a contact. Created automatically by the Event Processor. See Documentation/Events/Event-Lifecycle.md for the full event workflow.

### Why This Structure?

- **Single source of truth** – One company record eliminates duplicates and keeps enriched data consistent
- **Scalability** – Supports multiple contacts and multiple concurrent deals per company
- **Clean reporting** – Account-level metrics (ARR, customer count, expansion) are unambiguous
- **Buying group visibility** -- Contacts linked to deals create a clear map of who's involved in each opportunity
- **HubSpot Buying Groups** -- Native visual org chart feature (Sales Hub Enterprise) for mapping buying committees on deals. Supports role assignment, reporting hierarchy, and activity heat maps. At Knotch, separate Buying Groups are created for separate deals at the same account when the buying committees differ. The same contact can appear in multiple Buying Groups with different roles. See Document 05 (Buyer Personas and Buying Committee) for full setup guide and best practices.

### Parent-Child Company Associations

HubSpot supports **company-to-company associations** to represent corporate hierarchies (parent companies, subsidiaries, divisions). Knotch uses these to map conglomerates where multiple business units are prospected independently.

**When to create a parent-child association:**

- A subsidiary or division has its **own marketing org** and buying committee (e.g., Sony Interactive Entertainment vs. Sony Pictures Entertainment)
- Contacts at the subsidiary report into that division's leadership, not the parent's
- The subsidiary operates on a **different domain** than the parent (e.g., activision.com vs. microsoft.com)
- Deal activity, pipeline, and revenue should be tracked at the **subsidiary level**, not rolled up to the parent

**When NOT to create separate companies:**

- The subsidiary shares the parent's domain and marketing org
- There is no independent buying committee at the subsidiary level
- The entity is a brand name, not an operating division (e.g., "Xbox" is a brand under Microsoft Gaming, not a separate company)

**How to set up in HubSpot:**

1. Ensure both the parent and child company records exist with complete firmographic data
2. On the **child company record**, navigate to the right sidebar → Associations → Companies
3. Click **"Add"** and search for the parent company
4. Select the **"Parent Company"** association label (this is a HubSpot default label)
5. Save the association — the parent record will now show the child under its associated companies

**Via API (for bulk operations):**

```
PUT /crm/v4/objects/companies/{childId}/associations/companies/{parentId}
Body: [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 14}]
```

- Association type 14 = child-to-parent ("Parent Company" label)
- Association type 13 = parent-to-child (created automatically as the inverse)

**Required fields on child company record:**

- Company Name (use the subsidiary's name, not the parent's)
- Website / Domain (the subsidiary's primary domain)
- Ownership Type = "subsidiary"
- All standard firmographic fields per data quality standards below

**Active parent-child associations at Knotch:**

| Parent                 | Child                          | Rationale                                                 |
| ---------------------- | ------------------------------ | --------------------------------------------------------- |
| Microsoft              | Activision Publishing          | Acquired Jan 2024; independent gaming marketing org       |
| Microsoft              | Blizzard Entertainment         | Acquired Jan 2024; independent gaming marketing org       |
| Sony Group Corporation | Sony Interactive Entertainment | Independent gaming division with own marketing leadership |
| Sony Group Corporation | Sony Pictures Entertainment    | Independent entertainment studio with own marketing org   |
| Tencent                | Riot Games                     | Subsidiary; independent gaming studio and marketing team  |
| Comcast                | NBCUniversal                   | Media division with independent content marketing org     |

**Reporting implications:**

- Pipeline and revenue report at the **child company level** (where the deal lives)
- Account-level reporting (customer count, ARR) uses the child record
- Parent company association enables roll-up views in custom reports when needed
- ICP scoring runs at the child level — each subsidiary gets its own score

## Pipeline Structure

Knotch uses **two distinct pipelines** in HubSpot:

### Pipeline 1: New/Expansion

For new customer acquisitions and significant expansion opportunities.

**Stages (in order):**

1. **IPM** – Initial Product Meeting scheduled and held; opportunity confirmed to exist
2. **Qualification (Stage 1)** – Situation and pain documented; opportunity size estimated
3. **Consensus (Stage 2)** – Pain validated across buying group; solution fit confirmed; champion identified
4. **Proposal + Business Case Review (Stage 3)** – Economic case drafted; proposal delivered; pricing discussed
5. **Procurement (Stage 4)** – Legal, procurement, and IT reviews in progress
6. **Closed Won** – Contract executed; deal closed successfully
7. **Closed Lost** – Opportunity lost; reason documented

### Pipeline 2: Renewal

For managing contract renewals and within-account upsell opportunities.

**Stages:**

1. **Qualify** – Renewal identified and qualified; renewal scope and timeline confirmed
2. **Consensus** – Stakeholder alignment on renewal terms and scope
3. **Proposal** – Renewal pricing and terms proposed
4. **Procurement** – Legal, procurement, and final approvals in progress
5. **Closed Won** – Contract renewed
6. **Closed Lost** – Customer did not renew; churn reason documented

---

## Forecast Categories

Deals are assigned to forecast categories to enable accurate revenue forecasting. Each category has a probability weighting:

| Category      | HubSpot Value | Probability | Use Case                                                       |
| ------------- | ------------- | ----------- | -------------------------------------------------------------- |
| **Omit**      | OMIT          | 0%          | Prospect identified but no confirmed pain; pre-IPM             |
| **Pipeline**  | PIPELINE      | 20%         | IPM completed; SPICED situation/pain documented; early stage   |
| **Best Case** | BEST_CASE     | 60%         | Consensus stage; buying group engaged; strong champion support |
| **Commit**    | COMMIT        | 90%         | Proposal delivered; pricing agreed; on track for close         |
| **Closed**    | CLOSED        | 100% / 0%   | Contract executed (won) or deal lost (terminal)                |

### Forecast Category Rules

- Forecast categories are linked to pipeline stage; changes to stage trigger category reassessment
- "Commit" category requires deal close date within current month/quarter
- Lost deals are removed from forecast immediately upon closure

---

## Lifecycle Stages

Each contact has a lifecycle stage that tracks their journey through the funnel:

| Lifecycle Stage          | Definition                                                             |
| ------------------------ | ---------------------------------------------------------------------- |
| **Cold Prospect**        | Identified target; no outreach or engagement yet                       |
| **Subscriber**           | In our database; receives marketing communications                     |
| **MQL**                  | Marketing Qualified Lead; meets ICP criteria; passed to SDR            |
| **SQL**                  | Sales Qualified Lead; has scheduled IPM; assigned to AE                |
| **Opportunity**          | Deal created; IPM held; in active sales process                        |
| **Customer**             | Deal closed won; active subscriber                                     |
| **Churned Customer**     | Former customer; contract not renewed                                  |
| **Previous Opportunity** | Had an active deal that closed lost; may re-engage in a future cycle   |
| **Previous IPM**         | Had an IPM that did not convert to a qualified deal; may revisit later |

---

## Lead Status

Each contact has a lead status that tracks their sales outreach disposition:

| Lead Status          | Definition                                                                                                                                                                                                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cold**             | No outreach attempted yet                                                                                                                                                                                                                                                       |
| **Attempted**        | Outreach sent; no response received                                                                                                                                                                                                                                             |
| **Connected**        | Contact responded; conversation started                                                                                                                                                                                                                                         |
| **Meeting Booked**   | IPM or follow-up meeting scheduled                                                                                                                                                                                                                                              |
| **Open Opportunity** | Active deal in pipeline                                                                                                                                                                                                                                                         |
| **Bad Fit**          | Does not match ICP; disqualified                                                                                                                                                                                                                                                |
| **Left Company**     | Contact confirmed no longer at the associated company. Set manually when discovered (bounced email, LinkedIn shows new role, informed by colleague). Suppress from all outreach and sequences. Consider re-enriching to find their new company — they may be a buyer elsewhere. |
| **Junk**             | Invalid record (spam, test data, non-business contact). Excluded from all outreach and reporting.                                                                                                                                                                               |

### Lead Status Hierarchy

Lead status follows a strict upward progression: **Cold → Attempted → Connected → Meeting Booked → Open Opportunity**. Contacts only move up, never down (exception: terminal statuses Bad Fit, Left Company, Junk can be set at any time).

### Lead Status Backfill (May 28, 2026)

Lead status (`hs_lead_status`) was 100% blank for ~9,693 contacts. A one-time rules-engine backfill assigned statuses based on existing CRM data:

| Rule (evaluated in order)                                | Status Assigned  | Count |
| -------------------------------------------------------- | ---------------- | ----- |
| Has active deal                                          | Open Opportunity | 1,178 |
| Has closed-won deal                                      | Connected        | 330   |
| Has closed-lost deal                                     | Bad Fit          | —     |
| Lifecycle = customer or evangelist                       | Connected        | —     |
| Lifecycle = opportunity                                  | Open Opportunity | —     |
| Lifecycle = salesqualifiedlead or marketingqualifiedlead | Attempted        | 86    |
| Default (all remaining)                                  | Cold             | 8,099 |

**Ongoing maintenance:** Six automation workflows maintain lead status going forward. See `Documentation/Workflows/Lead-Status-Automation-Plan.md` for specs.

---

## Key Properties Tracked

The Knotch CRM tracks core properties organized into functional groups. Below is the complete inventory:

### Firmographic Core (8 properties)

- Company Name
- Industry
- Number of Employees
- Annual Revenue
- Founded Year
- Headquarters Location (City, State, Country)
- Company Website
- Company Phone

### Funding & Ownership (2 properties)

- Funding Stage (seed, series A/B/C, growth equity, mature, private equity)
- Ownership Type (VC-backed, bootstrapped, PE-backed, public, subsidiary)

### Workforce & Tech Intelligence (2 properties)

- Tech Stack (`clay__tech_stack`; marketing/sales technology platforms enriched by Clay)
- Marketing Headcount % (`marketing_headcount`; % of workforce in marketing/digital functions)

### ICP Scoring Fields (7 properties)

- ICP Score Composite (0–100, four-pillar weighted score)
- ICP Enterprise Fit Score (firmographic + headcount signal)
- ICP Content Investment Score (content team, digital spend signals)
- ICP Engagement Score (HubSpot activity + deal history)
- ICP Data Completeness (enrichment coverage percentage)
- ICP Model Version (currently "v3")
- ICP Score Last Updated (date of last scoring run)

### Contact Enrichment Fields (4 properties)

- Enrichment Source (last tool that enriched the record: Apollo, Clay, Manual)
- Last Enrichment Date
- Employment History (`employment_history`; textarea; full work history from Apollo stored as JSON array. Fields per entry: company, title, start, end, current. Coverage: 11,403 / ~12,884 = 88.5%)
- Apollo ID (`apollo_id`; text; Apollo person ID for direct enrichment lookups. Coverage: 11,500 / ~12,884 = 89.3%)

### Deal-Level Properties

**SPICED Framework Fields:**

- Situation (text, multi-line)
- Pain (text, multi-line)
- Impact (text, multi-line)
- Critical Event (text)
- Decision Criteria (text, multi-line)

**Deal Metadata:**

- Deal Owner (AE assigned)
- Deal Amount
- Deal Close Date
- Number of Associated Contacts (`num_associated_contacts`; HubSpot built-in)
- Champion Identified (yes/no; `champion_identified`)
- Budget Confirmation (yes/no; `budget_confirmation`)
- Deal Stage (pipeline stage)
- Forecast Category (`hs_manual_forecast_category`; HubSpot built-in)
- Deal Tags (`hs_tag_ids`; used for hygiene tags)
- Closed Won Reason / Closed Lost Reason (separate properties, populated on close)
- Annual Contract Value (`hs_acv`; HubSpot built-in)
- Total Contract Value (`hs_tcv`; HubSpot built-in)

---

## Property Groups & Organization

Properties are organized in HubSpot by functional group:

1. **Firmographic Core** – Basic company identification and classification
2. **Funding & Ownership** – Capital structure and investor profile
3. **Workforce & Tech Intelligence** – Operational and technology metrics
4. **ICP Scoring Fields** – Four-pillar ICP scoring model (v3)
5. **Contact Enrichment Fields** – Data quality, freshness, and enrichment identifiers
6. **Deal Properties** – SPICED fields and deal tracking

---

## Data Ownership & Assignment Rules

### Geographic Assignment (80% of rules)

Accounts are assigned to AEs primarily by **geography**:

- Americas (North / Latin America)
- EMEA (Europe, Middle East, Africa)
- APAC (Asia-Pacific)

Regional territory assignments are managed by the Head of Sales and Revenue Operations.

### Active Deal Protection

If an AE has an **active deal** (Qualification stage or beyond) on an account, that account remains their responsibility until the deal closes. This prevents deal poaching and maintains relationship continuity.

### Tier Mix Balance

AE territories are balanced to include:

- 30% Tier I accounts (highest potential)
- 40% Tier II accounts (steady revenue)
- 30% Tier III accounts (opportunistic)

This mix ensures predictable quota distribution and opportunity access.

---

## Data Sources Flowing Into HubSpot

### Apollo

**Use:** Contact reachability, prospecting data, and employment intelligence

- Email addresses (verified)
- Job title and seniority
- Employment history (`employment_history`; full work history as JSON array — 88.5% coverage)
- Apollo person ID (`apollo_id`; for direct enrichment lookups — 89.3% coverage)
- Boolean match status (verified, partial, unverified)
- Last updated timestamp

**Note:** Apollo has zero phone data for Knotch's gap contacts. Clay is the only viable phone enrichment source.

**Integration:** Manual upload via Apollo API, enrichment runs on contact creation

**Rules:** Do not override Apollo data manually; always refresh via API if data is stale.

### HubSpot Breeze

**Use:** Automated basic firmographic enrichment

- Company name, industry, employee count, annual revenue
- Website and location
- Triggered automatically on company creation

**Rules:** Do not disable; allows baseline enrichment with zero manual effort.

### AI/Claude Enrichment (ICP Scoring v3)

**Use:** Four-pillar ICP scoring model

- ICP Score Composite (0–100) – weighted score across four pillars
- ICP Enterprise Fit Score – firmographic + headcount signal
- ICP Content Investment Score – content team, digital spend signals
- ICP Engagement Score – HubSpot activity + deal history
- ICP Data Completeness – enrichment coverage percentage
- ICP Model Version – currently "v3"
- ICP Score Last Updated – date of last scoring run

**Refresh Cadence:** Quarterly or on-demand for high-priority accounts

**Input Data:** Reads from Apollo, HubSpot firmographics, activity data, and SPICED notes

---

## Data Quality Standards

### Required Fields on Company Record

- Company Name
- Industry
- Headquarters Location
- Website
- Number of Employees (minimum)

### Required Fields on Contact Record

- First Name
- Last Name
- Email
- Job Title
- Company Association

### Required Fields on Deal Record

- Deal Name
- Deal Amount
- Deal Stage
- Close Date
- Account Tier (assigned on IPM)
- Situation (Qualification stage minimum)

### Freshness Standards

- Firmographic data refreshed annually (via Clay or HubSpot Breeze)
- SPICED fields updated on every stage transition
- Contact reachability (Apollo) verified before outreach

---

## Related Documentation

**See 01-Knotch-GTM-Overview.md** for business context and revenue model.

**See 03-Deal-Process-and-SPICED.md** for deal progression rules and SPICED field guidance.

**See Documentation/Events/Event-Lifecycle.md** for the end-to-end event workflow, Event Attendance object usage, and list naming conventions.
