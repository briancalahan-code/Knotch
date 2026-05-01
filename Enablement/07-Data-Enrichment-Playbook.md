# Data Enrichment Playbook

**Effective Date:** March 2026
**Audience:** GTM Team (Sales, Marketing, Ops)
**Purpose:** Unified reference for data enrichment architecture, execution, and ongoing maintenance

---

## Executive Summary

Our data enrichment program transforms baseline contact and company records into a complete, actionable GTM database. We operate a three-source enrichment stack—Apollo (primary), Clay, and HubSpot Breeze, with AI/Claude post-processing—with clear ownership, field mappings, and execution timelines. This playbook documents the baseline gaps, target outcomes, credit budgets, and operational workflows.

**Current Baseline (Pre-Enrichment):**

- 2,000 companies / 11,493 contacts
- Critical gaps: Phone numbers 3.6% coverage (416 of 11,493)
- Web technologies 46% coverage
- LinkedIn URLs 76% coverage

---

## Enrichment Sources & Architecture

### 1. Apollo (Primary Contact & Company Enrichment)

**Role:** Primary contact reachability and company firmographics enrichment
**Status:** Active | Portal 44523005 connected
**Credit Budget:** 452,896 available | Renews August 2026 | 1 credit = 1 contact

**Apollo Coverage:**

- **Contact fields:** Verified emails, direct dials, mobile phones, LinkedIn URLs, job-change detection
- **Company fields:** Founded year, description, phone, LinkedIn company page, web technologies, SIC codes, funding data, account IDs
- **Key advantage:** Direct dial and mobile phone enrichment (critical gap-filler)
- **Integration:** One-way sync (Apollo → HubSpot), "Do not overwrite existing values" enabled
- **Sync direction:** Apollo pushes enriched data; HubSpot never writes back to Apollo

**Credit Projection Through August 2026:**

- Projected usage: ~120,000 credits (26% of budget)
- Remaining buffer: 332,000 credits (74%)
- Note: Company enrichment uses separate quota (no credit cost per company)

**Fields Apollo Owns:**

- Contact: `phone`, `mobilephone`, `hs_linkedin_url` (verification focus)
- Company: `founded_year`, `description`, `about_us`, `phone`, `linkedin_company_page`, `hs_linkedin_handle`, `twitter_handle`, `facebook_company_page`, `web_technologies`, `hs_keywords`, `sic_code_1`, `sic_code_2`, `zip`, `apollo_account_id`, `funding_stage`, `total_funding_amount`, `is_public`, `ticker`

---

### 2. Clay (Enrichment Workflows & Analysis)

**Role:** Workflow orchestration, data analysis, waterfall enrichment coordination
**Status:** Active | Workflow integration enabled

**Clay Responsibilities:**

- Orchestrate enrichment chains (fallback when Apollo partial)
- Perform secondary data lookups and validation
- Enable complex, multi-step enrichment logic
- Support waterfall rules (e.g., try Apollo, then Clay, then manual)

---

### 3. HubSpot Breeze (Native Company Enrichment)

**Role:** Automatic baseline company enrichment on record creation
**Status:** Active | Native to HubSpot
**Credit Model:** Uses Breeze credits (not Apollo)

**Breeze Coverage (on company creation):**

- Industry
- Employee count (range + exact if available)
- Annual revenue (range + exact if available)
- City, state, country
- Timezone
- Employee range bucket
- Revenue range bucket

**Breeze Advantages:**

- Fast, automatic, zero operational overhead
- Runs instantly on new company creation
- Complements Apollo for quick baseline
- Perfect for real-time, low-latency enrichment

**Contact enrichment via Breeze:**

- Job title (if searchable)
- Department
- City, state, country

---

### 4. AI/Claude (Post-Enrichment Intelligence)

**Role:** Computed intelligence and classification layers
**Status:** Active | Runs after Apollo and Breeze complete

**AI-Computed Fields:**

- `account_tier` (ICP tier scoring: Tier I, II, III, Out-of-Scope)
- `hs_ideal_customer_profile` (ICP classification rationale)
- `hs_quick_context` (Account summary: industry, size, geography, strategic fit)
- `hs_persona` (Contact persona classification)
- `sub_industry` (Refined industry classification)

**Execution Model:**

- Runs on-demand after Apollo/Breeze enrichment completes
- Uses company and contact data to infer strategic fit
- Provides human-readable context for sales teams

---

---

## Dropped Vendors

**Alysio/Explorium:** Originally evaluated but dropped due to:

- Could not write custom HubSpot properties
- Slow performance for batch enrichment
- Inconsistent data quality vs. Apollo
- Complex setup overhead not justified by ROI

---

## Company Field Source Map

| Field                       | Primary Source    | Fallback | Overwrite Rule           |
| --------------------------- | ----------------- | -------- | ------------------------ |
| `founded_year`              | Apollo            | Manual   | Fill if blank            |
| `description`               | Apollo            | Manual   | Fill if blank            |
| `about_us`                  | Apollo            | Manual   | Fill if blank            |
| `phone`                     | Apollo            | Manual   | Fill if blank            |
| `linkedin_company_page`     | Apollo            | Manual   | Fill if blank            |
| `hs_linkedin_handle`        | Apollo            | Manual   | Fill if blank            |
| `twitter_handle`            | Apollo            | Manual   | Fill if blank            |
| `facebook_company_page`     | Apollo            | Manual   | Fill if blank            |
| `web_technologies`          | Apollo            | Clay     | Fill if blank            |
| `hs_keywords`               | Apollo            | Manual   | Fill if blank            |
| `sic_code_1`, `sic_code_2`  | Apollo            | Manual   | Fill if blank            |
| `zip`                       | Apollo            | Breeze   | Fill if blank            |
| `apollo_account_id`         | Apollo            | N/A      | Always write             |
| `funding_stage`             | Apollo            | Manual   | Fill if blank            |
| `total_funding_amount`      | Apollo            | Manual   | Fill if blank            |
| `is_public`                 | Apollo            | Manual   | Fill if blank            |
| `ticker`                    | Apollo            | Manual   | Fill if blank            |
| `industry`                  | Breeze            | Apollo   | Fill if blank            |
| `numberofemployees`         | Breeze            | Apollo   | Fill if blank            |
| `annualrevenue`             | Breeze            | Apollo   | Fill if blank            |
| `city`, `state`, `country`  | Breeze            | Apollo   | Fill if blank            |
| `timezone`                  | Breeze            | Manual   | Fill if blank            |
| `employee_range`            | Breeze            | Manual   | Fill if blank            |
| `revenue_range`             | Breeze            | Manual   | Fill if blank            |
| `account_tier`              | AI/Claude         | Manual   | Always write (quarterly) |
| `hs_ideal_customer_profile` | AI/Claude         | Manual   | Always write (quarterly) |
| `hs_quick_context`          | AI/Claude         | Manual   | Always write (quarterly) |
| `sub_industry`              | AI/Claude         | Manual   | Always write (quarterly) |
| `enrichment_source`         | Workflow metadata | Manual   | Always write             |
| `last_enrichment_date`      | Workflow metadata | Manual   | Always write             |

---

## Contact Field Source Map

| Field                      | Primary Source    | Fallback | Overwrite Rule                         |
| -------------------------- | ----------------- | -------- | -------------------------------------- |
| `phone`                    | Apollo            | Manual   | Fill if blank                          |
| `mobilephone`              | Apollo            | Manual   | Fill if blank                          |
| `hs_linkedin_url`          | Apollo            | Manual   | Fill if blank                          |
| `email`                    | Apollo            | Manual   | Only replace if bounced/invalid        |
| `jobtitle`                 | Apollo            | Breeze   | Overwrite (Apollo detects job changes) |
| `department`               | Breeze            | Apollo   | Fill if blank                          |
| `city`, `state`, `country` | Breeze            | Apollo   | Fill if blank                          |
| `hs_persona`               | AI/Claude         | Manual   | Always write                           |
| `enrichment_source`        | Workflow metadata | Manual   | Always write                           |
| `last_enrichment_date`     | Workflow metadata | Manual   | Always write                           |

---

## Enrichment Execution Plan

### Phase 1: Batch Enrichment (Existing Base)

**Scope:** 2,000 companies + 11,493 contacts
**Timeline:** Immediate (Week 1-3)
**Approach:** Bulk API + Apollo integration + Clay workflows

**Process:**

1. Apollo auto-enrichment via HubSpot native integration (no manual action needed)
2. Breeze enrichment on company records (automatic)
3. Clay waterfall enrichment for phone/LinkedIn gaps
4. AI/Claude tier and persona scoring after step 3
5. QA pass on sample (100 records minimum)

**Expected Outcomes After Phase 1:**

- Phone fill: 3.6% → 40-60%
- LinkedIn URLs: 76% → 88%+
- Web technologies: 46% → 75%+
- Founded year: 38% → 75%+

---

### Phase 2: Real-Time Enrichment (Ongoing)

**Scope:** Every new company and contact created in HubSpot
**Automation:** HubSpot workflows + Apollo integration

**Trigger:** Company or contact record created
**Actions:**

1. Breeze enrichment (automatic via HubSpot)
2. Apollo enrichment (via native integration)
3. Set `enrichment_source` = "Apollo", `last_enrichment_date` = today
4. AI/Claude persona/tier scoring (webhook-triggered)

**SLA:** Enrichment complete within 5 minutes of record creation

---

### Phase 3: Scheduled Maintenance (Recurring)

**Weekly:** Contact enrichment via Apollo scheduled job (10,500 records/week, CRM field enrichment)
**Weekly:** Account enrichment via Apollo scheduled job (2,500 records/week, CRM field enrichment)
**Quarterly:** Email verification + job-change detection (Apollo)
**Quarterly:** Persona and ICP tier re-scoring (AI/Claude)
**Annual:** Full re-enrichment pass (all fields, all records)

---

## Apollo HubSpot Integration Setup

**Portal:** 44523005
**Status:** Connected and active

**Key Configuration:**

- **Overwrite setting:** "Do not overwrite existing values" enabled globally, with per-field exceptions below
- **Sync direction:** Apollo → HubSpot only (unidirectional). Pull every 15 min. Push DISABLED.
- **Field conflicts:** If HubSpot has a value, Apollo will not overwrite (unless explicitly configured otherwise per field)

**Per-Field Overwrite Rules (Data Writing Rules):**

- **Job Title:** Overwrite ON, Auto-fill ON (Apollo updates stale titles on job changes)
- **Phone numbers:** Overwrite OFF, Auto-fill ON
- **Emails:** Overwrite OFF, Auto-fill ON
- **Location (City/State/Country):** Overwrite OFF, Auto-fill ON
- **Links (LinkedIn):** Overwrite OFF, Auto-fill ON
- **Name:** Overwrite OFF, Auto-fill OFF
- **Company Name:** Overwrite OFF, Auto-fill OFF

**Contact Field Mappings (14 total):**

- First name, Last name, Current job (Job Title), Default number (Phone), Mobile number, Primary email, City, State, Country, LinkedIn URL, Owner, Company Name, Enrichment Source, Last Enrichment Date

**Fields NOT Mapped (Protected):**

- Company name (HubSpot owns this field, mapped but no overwrite)
- Company association (HubSpot owns record relationships)
- Email verification status (not available as a mappable Apollo field; see Known Limitations)

**Company Association Rules:**

- Do NOT enable bidirectional sync for company associations
- HubSpot maintains the primary company-contact relationships
- Apollo only enriches individual records, not relationships

**Scheduled Enrichment Jobs (Active):**

| Job Name                          | Object  | Type                                 | Cadence | Records/Run | Fields                                                                                   |
| --------------------------------- | ------- | ------------------------------------ | ------- | ----------- | ---------------------------------------------------------------------------------------- |
| Knotch HubSpot Contact Enrichment | Contact | CRM field enrichment                 | Weekly  | 10,500      | Job Title, Phone, Mobile, Email, City, State, Country, LinkedIn                          |
| Knotch HubSpot Account Enrichment | Account | Apollo-source / CRM field enrichment | Weekly  | 2,500       | Company Name, Website URL, Phone, Domain, Description, Employees, Industry, Sub-Industry |

**Known Limitations:**

- Apollo does not expose email verification status (Verified/Unverified/Guessed) as a mappable CRM field. This data is visible inside Apollo but cannot be synced to HubSpot via the native integration. Workaround options include Apollo API scripting, Apollo Workflows (Integrations action, currently in Beta), or middleware tools like Zapier/Make.
- Push records is currently disabled in sync settings. The "Push to HubSpot" workflow action will be skipped until push is enabled.

---

## Credit Budget & Projections

**Total Budget:** 452,896 credits
**Renewal Date:** August 2026

**Projected Usage Through August 2026:**

- Phase 1 bulk enrichment: ~80,000 credits (batch of 11,493 contacts)
- Phase 2 monthly net-new: ~40,000 credits (avg 300/month × 12 months)
- **Total projected:** ~120,000 credits (26% of budget)
- **Remaining buffer:** 332,000 credits (74%)

**Cost Model:**

- 1 credit = 1 contact enrichment
- Company enrichment = no credit cost (separate quota)
- Cost per contact: ~$0.015 (at $7k per 452k credits)

**Budget Health:** Green – well under budget, ample margin for expansion or ad-hoc lookups

---

## Target Outcomes

### Baseline → Target Coverage

| Metric                       | Baseline   | Target  | Outcome                           |
| ---------------------------- | ---------- | ------- | --------------------------------- |
| Phone fill (contacts)        | 3.6% (416) | 40-60%  | +4,000-6,500 contacts with phone  |
| LinkedIn URLs (contacts)     | 76%        | 88%+    | +1,400+ contacts with URLs        |
| Web technologies (companies) | 46%        | 75%+    | +580 companies with tech stack    |
| Founded year (companies)     | 38%        | 75%+    | +740 companies with founding date |
| Total contacts               | 11,493     | ~21,500 | +10,000 net-new from prospecting  |
| ICP tier scoring (companies) | 0%         | 100%    | All 2,000 companies scored        |

### Data Quality Metrics

| Metric                 | Target | Method                            |
| ---------------------- | ------ | --------------------------------- |
| Email deliverability   | >95%   | Quarterly verification via Apollo |
| Phone accuracy         | >90%   | Sample validation on outbound     |
| LinkedIn URL freshness | >95%   | Monthly Apollo sync               |
| Founded year accuracy  | >98%   | Apollo + manual spot-checks       |
| ICP tier consistency   | >95%   | AI/Claude + sales team review     |

---

## Overwrite Rules (Decision Framework)

### "Fill if Blank" (Standard)

Applies to: `founded_year`, `description`, `phone`, `linkedin_company_page`, `web_technologies`, `hs_keywords`, `sic_code_1`, `sic_code_2`, `department`, `city`, `state`, `country`

**Rule:** Only populate field if currently empty. Do NOT overwrite existing values.
**Exception:** If existing value is clearly wrong (e.g., typo, incorrect title), mark for manual review instead of auto-overwriting.

### "Overwrite" (Job-Change Sensitive)

Applies to: `jobtitle`

**Rule:** Apollo overwrites existing values when it detects a job change or updated title.
**Rationale:** Stale job titles are a top data quality issue. Apollo's job-change detection ensures titles stay current. Enabled March 2026.

### "Always Write" (Computed/Metadata)

Applies to: `apollo_account_id`, `account_tier`, `hs_ideal_customer_profile`, `hs_quick_context`, `hs_persona`, `enrichment_source`, `last_enrichment_date`

**Rule:** Always populate on enrichment execution, regardless of prior value.
**Rationale:** These fields track enrichment status and tier/persona logic which should always reflect current state.

### "Only Replace Bounced/Invalid" (Email Safety)

Applies to: `email`

**Rule:** Only overwrite if email is marked bounced, invalid, or opted-out.
**Rationale:** Protects intentional email changes and opt-out status.

---

## Operational Guardrails

### Do NOT Enrich These Fields Automatically

- Company name (HubSpot canonical)
- Manual deal notes or custom sales fields
- Opt-out or unsubscribe status

### Contact Records to Skip

- Test/fake emails (test@, demo@, noreply@)
- Bounced or invalid email markers
- Opted-out contacts
- Records flagged "Do not contact"

### Company Records to Skip

- Competitors (if flagged in system)
- Prospects with "Do not enrich" flag
- Companies with hard-block privacy policies

---

## Troubleshooting & Common Issues

**Issue:** Apollo credits exhausted mid-month
**Resolution:** Pause new enrichment, prioritize Tier I companies only, extend to Sept with Clay fallback.

**Issue:** Phone numbers still low after enrichment
**Resolution:** Clay waterfall secondary lookup, manual B2B directory research, outreach to sales for corrections.

**Issue:** Email verification returns high bounce rate
**Resolution:** Quarterly re-verification, implement sender reputation warmup, review list quality.

**Issue:** LinkedIn URLs not syncing from Apollo
**Resolution:** Check Apollo integration sync status, verify field mapping, re-sync recent batch.

---

## Appendix: Integration Checklist

- [x] Apollo HubSpot integration verified (Portal 44523005)
- [ ] Breeze enrichment enabled on new companies
- [ ] Clay account connected for waterfall workflows
- [ ] AI/Claude scoring configured for async execution
- [x] Field mapping validated (14 contact fields mapped, March 2026)
- [x] Overwrite rules configured in Apollo settings (Job Title overwrite enabled, March 2026)
- [ ] Credit budget monitored monthly
- [ ] Quarterly re-enrichment calendar blocked
- [ ] QA sample audit completed (100 records)
- [ ] Sales team trained on field sources and accuracy expectations

---

---

## Related Documentation

**See 15-AI-Skills-and-Knotch-MCP.md** for the Knotch MCP tools that support enrichment workflows — including `enrich_contact` (Apollo enrichment + HubSpot push), `clay_enrich` (Clay enrichment trigger), `find_phone` (phone waterfall lookup), and `lookup_contact` / `find_contact_by_details` (contact search before enrichment).

---

**Questions?** Reach out to Ops. Last updated: March 2026.
