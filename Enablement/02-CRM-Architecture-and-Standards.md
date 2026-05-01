# CRM Architecture and Standards

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

### Why This Structure?

- **Single source of truth** – One company record eliminates duplicates and keeps enriched data consistent
- **Scalability** – Supports multiple contacts and multiple concurrent deals per company
- **Clean reporting** – Account-level metrics (ARR, customer count, expansion) are unambiguous
- **Buying group visibility** -- Contacts linked to deals create a clear map of who's involved in each opportunity
- **HubSpot Buying Groups** -- Native visual org chart feature (Sales Hub Enterprise) for mapping buying committees on deals. Supports role assignment, reporting hierarchy, and activity heat maps. At Knotch, separate Buying Groups are created for separate deals at the same account when the buying committees differ. The same contact can appear in multiple Buying Groups with different roles. See Document 05 (Buyer Personas and Buying Committee) for full setup guide and best practices.

## Pipeline Structure

Knotch uses **two distinct pipelines** in HubSpot:

### Pipeline 1: New Business & Expansion

For new customer acquisitions and significant expansion opportunities.

**Stages (in order):**

1. **IPM** – Initial Product Meeting scheduled and held; opportunity confirmed to exist
2. **Qualification (Stage 1)** – Situation and pain documented; opportunity size estimated
3. **Consensus (Stage 2)** – Pain validated across buying group; solution fit confirmed; champion identified
4. **Proposal + Business Case (Stage 3)** – Economic case drafted; proposal delivered; pricing discussed
5. **Procurement (Stage 4)** – Legal, procurement, and IT reviews in progress
6. **Closed Won** – Contract executed; deal closed successfully
7. **Closed Lost** – Opportunity lost; reason documented

### Pipeline 2: Renewal & Upsell

For managing contract renewals and within-account upsell opportunities.

**Stages:**

1. **Renewal Identified** – Renewal contract identified; renewal manager assigned
2. **Renewal Initiated** – Contract renewal discussion begun with customer
3. **Renewal Proposal** – Pricing and terms proposed
4. **Renewal Negotiation** – Commercial terms being finalized
5. **Closed Won (Renewal)** – Contract renewed
6. **Closed Lost (Renewal)** – Customer did not renew; churn reason documented

---

## Forecast Categories

Deals are assigned to forecast categories to enable accurate revenue forecasting. Each category has a probability weighting:

| Category        | Probability | Use Case                                                       |
| --------------- | ----------- | -------------------------------------------------------------- |
| **Lead**        | 0%          | Prospect identified but no confirmed pain; pre-IPM             |
| **Pipeline**    | 20%         | IPM completed; SPICED situation/pain documented; early stage   |
| **Best Case**   | 60%         | Consensus stage; buying group engaged; strong champion support |
| **Commit**      | 90%         | Proposal delivered; pricing agreed; on track for close         |
| **Closed Won**  | 100%        | Contract executed                                              |
| **Closed Lost** | 0%          | Deal lost; closed terminal                                     |

### Forecast Category Rules

- Deals must exit stage gates before advancing forecast category
- Forecast categories are linked to pipeline stage; changes to stage trigger category reassessment
- "Commit" category requires deal close date within current month/quarter
- Lost deals are removed from forecast immediately upon closure

---

## Lifecycle Stages

Each contact has a lifecycle stage that tracks their journey through the funnel:

| Lifecycle Stage | Definition                                                   |
| --------------- | ------------------------------------------------------------ |
| **Subscriber**  | In our database; receives marketing communications           |
| **Lead**        | Engaged with marketing content; identified as prospect       |
| **MQL**         | Marketing Qualified Lead; meets ICP criteria; passed to SDR  |
| **SQL**         | Sales Qualified Lead; has scheduled IPM; assigned to AE      |
| **Opportunity** | Deal created; IPM held; in active sales process              |
| **Customer**    | Deal closed won; active subscriber                           |
| **Evangelist**  | Customer with strong executive champion; expansion candidate |

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

---

## Key Properties Tracked (61 Total)

The Knotch CRM tracks **61 core properties** organized into functional groups. Below is the complete inventory:

### Firmographic Core (8 properties)

- Company Name
- Industry
- Number of Employees
- Annual Revenue
- Founded Year
- Headquarters Location (City, State, Country)
- Company Website
- Company Phone

### Funding & Ownership (4 properties)

- Funding Stage (seed, series A/B/C, growth equity, mature, private equity)
- Lead Investor
- Valuation
- Ownership Type (VC-backed, bootstrapped, PE-backed, public, subsidiary)

### Workforce & Tech Intelligence (6 properties)

- Headcount (total FTE)
- Headcount Growth Rate (YoY %)
- Tech Stack (technology platforms used)
- Marketing Spend (estimated annual)
- Digital Spend (estimated annual)
- Content Team Size (estimated)

### AI-Computed Fields (8 properties)

- ICP Score (0–100, computed via Claude analysis)
- ICP Score Explanation (text reason for score)
- Primary Persona (role/function of primary contact)
- Account Summary (2–3 sentence AI summary of business)
- Content Spend Estimate (AI estimate of annual content investment)
- Digital Transformation Stage (early, mid, advanced)
- Competitive Threat (likely competing vendor)
- Expansion Opportunity (AI assessment of upsell potential)

### Enrichment Metadata (4 properties)

- Apollo Match Status (verified, partial, unverified)
- Clay Enrichment Status (enriched, pending, failed)
- Last Enrichment Date
- Data Freshness Flag (green/yellow/red)

### Deal-Level Properties (20 properties)

**SPICED Framework Fields:**

- Situation (text, multi-line)
- Pain (text, multi-line)
- Impact (text, multi-line)
- Critical Event (text)
- Decision Criteria (text, multi-line)

**Deal Metadata:**

- Deal Owner (AE assigned)
- Account Tier (Tier I, II, or III)
- Deal Amount
- Deal Close Date
- Sales Cycle Length (auto-calculated days since IPM)
- Buying Group Size (count of contacts on deal)
- Champion Identified (yes/no)
- Champion Contact (contact record linked)
- Economic Buyer Confirmed (yes/no)
- Technical Requester Identified (yes/no)
- Procurement Contact Added (yes/no)
- Competitive Situation (competing vendor name/list)
- Deal Stage (pipeline stage)
- Forecast Category
- Deal Tags (custom labels)
- Win/Loss Reason (populated on close)
- Expected Contract Value (ECV, 3-year equivalent)
- Deployment Timeline
- Integration Requirements (text)

### Account Planning (6 properties)

- Strategic Priorities (text; what the customer is trying to achieve)
- Competitive Landscape (text; competitors or alternative solutions in use)
- Expansion Opportunities (multi-select; modules/use cases to upsell)
- Account Risk Flag (churn risk assessment)
- Customer Success Owner
- Renewal Date

---

## Property Groups & Organization

Properties are organized in HubSpot tabs for clarity and reduce clutter:

1. **Firmographic Core** – Basic company identification and classification
2. **Funding & Ownership** – Capital structure and investor profile
3. **Workforce & Tech Intelligence** – Operational and technology metrics
4. **AI-Computed Fields** – ICP scoring and account intelligence
5. **Enrichment Metadata** – Data quality and freshness indicators
6. **Deal Properties** – SPICED fields and deal tracking
7. **Account Planning** – Upsell/expansion and risk management

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

**Use:** Contact reachability and prospecting data

- Email addresses and verified phone numbers
- Job title and seniority
- Employment history
- Boolean match status (verified, partial, unverified)
- Last updated timestamp

**Integration:** Manual upload via Apollo API, enrichment runs on contact creation

**Rules:** Do not override Apollo data manually; always refresh via API if data is stale.

### HubSpot Breeze

**Use:** Automated basic firmographic enrichment

- Company name, industry, employee count, annual revenue
- Website and location
- Triggered automatically on company creation

**Rules:** Do not disable; allows baseline enrichment with zero manual effort.

### AI/Claude Enrichment

**Use:** ICP scoring, persona classification, account summaries

- ICP Score (0–100) – computational assessment of ICP fit
- ICP Score Explanation – plain-language reasoning
- Primary Persona – role of key contact
- Account Summary – 2–3 sentence business description
- Content Spend Estimate – AI estimate of annual spend
- Digital Transformation Stage – maturity assessment
- Competitive Threat – likely competing vendor
- Expansion Opportunity – AI-generated upsell pathway

**Refresh Cadence:** Quarterly or on-demand for high-priority accounts

**Input Data:** Reads from Apollo, company website, and SPICED notes

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

**See 03-Deal-Process-and-SPICED.md** for deal progression rules, stage gates, and SPICED field guidance.
