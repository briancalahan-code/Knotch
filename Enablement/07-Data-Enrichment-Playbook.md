# Data Enrichment Playbook

**Audience:** GTM Team (Sales, Marketing, Ops) | **Topics:** enrichment, Apollo, Clay, Breeze, phone, LinkedIn, email verification | **Last Updated:** May 2026

---

## Executive Summary

Our data enrichment program transforms baseline contact and company records into a complete, actionable GTM database. We operate a two-source enrichment stack — Apollo (primary) and HubSpot Breeze, with AI/Claude post-processing and a self-service Contact Enrichment Sheet for ad-hoc lookups. This playbook documents the baseline gaps, target outcomes, credit budgets, and operational workflows.

**Current Baseline (Pre-Enrichment, March 2026):**

- 2,000 companies / 11,493 contacts
- Critical gaps: Phone numbers 3.6% coverage (416 of 11,493)
- Web technologies 46% coverage
- LinkedIn URLs 76% coverage

**Current Coverage (May 2026 Enrichment Sprint):**

- ~2,005 companies / ~12,884 contacts
- Phone: 73.6% (8,686 contacts) — Clay waterfall is the only viable phone path
- LinkedIn URLs: 91.0% (10,743 contacts)
- Employment history: 88.5% (11,403 contacts) — new field via Apollo
- Apollo ID: 89.3% (11,500 contacts) — new field for direct lookups
- Apollo credits used to date: ~12,512 | Remaining: ~440K of 456K

---

## Enrichment Sources & Architecture

### 1. Apollo (Primary Contact & Company Enrichment)

**Role:** Primary contact reachability and company firmographics enrichment
**Status:** Active | Portal 44523005 connected
**Credit Budget:** ~440,000 remaining (of 456K) | Renews August 2026 | 1 credit = 1 contact

**Apollo Coverage:**

- **Contact fields:** Verified emails, direct dials, mobile phones, LinkedIn URLs, job-change detection
- **Company fields:** Founded year, description, phone, LinkedIn company page, web technologies, SIC codes, funding data, account IDs
- **Key advantage:** Direct dial and mobile phone enrichment (critical gap-filler)
- **Integration:** One-way sync (Apollo → HubSpot), "Do not overwrite existing values" enabled
- **Sync direction:** Apollo pushes enriched data; HubSpot never writes back to Apollo

**Credit Projection Through August 2026:**

- Credits used to date: ~12,512 (May 2026 sprint: ~11,500 employment history + ~1,012 other phases)
- Remaining: ~440,000 credits
- Remaining buffer: ~96% of total budget
- Note: Company enrichment uses separate quota (no credit cost per company)

**Fields Apollo Owns:**

- Contact: `phone`, `mobilephone`, `hs_linkedin_url` (verification focus), `employment_history` (JSON array), `apollo_id` (person ID for direct lookups)
- Company: `founded_year`, `description`, `about_us`, `phone`, `linkedin_company_page`, `hs_linkedin_handle`, `twitter_handle`, `facebook_company_page`, `web_technologies`, `hs_keywords`, `sic_code_1`, `sic_code_2`, `zip`, `apollo_account_id`, `funding_stage`, `total_funding_amount`, `is_public`, `ticker`

---

### 2. Contact Enrichment Sheet (Self-Service Tool)

**Role:** Ad-hoc contact lookup, enrichment, email validation, and HubSpot push
**Status:** Active | Google Sheets + Apps Script
**Sheet:** [Knotch Contact Enrichment Tool](https://docs.google.com/spreadsheets/d/1n_m-0GODGS0Lj9OCm_HENahzFvVVIND11zVgqcE-6wo/edit?usp=sharing)
**Walkthrough:** [Recording](https://drive.google.com/file/d/18C23TcPByFHDiJSrj1rUllDoneNF7eIU/view?usp=sharing)
**Source code:** `Projects/Enrichment-Sheet/apps-script/` (Code.gs, HubSpot.gs, Apollo.gs, EmailValidation.gs, Enrichment.gs)

**What it does:**

- Fill in name + company, highlight rows, run from the Enrichment menu
- **Full Cascade:** Searches HubSpot first (free), then Apollo (1 credit per match) for contacts not found
- **Email Validation:** Three-step check — format validation (free), domain MX record check (free), Apollo deliverability verification (1 credit)
- **Push to HubSpot:** Smart upsert with dedup (email → LinkedIn → name+company search before creating). Fill Gaps Only mode never overwrites existing data.
- **22 output columns:** Work email, personal email, direct phone, mobile phone, title, seniority, department, city/state/country, LinkedIn, Twitter, company, industry, employees, email status

**When to use:** One-off contact lookups, pre-meeting enrichment, event list enrichment, email validation before outbound campaigns. For bulk enrichment (1,000+ contacts), use the Apollo HubSpot integration instead.

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
| `web_technologies`          | Apollo            | Manual   | Fill if blank            |
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
| `employment_history`       | Apollo            | N/A      | Always write (textarea, JSON array)    |
| `apollo_id`                | Apollo            | N/A      | Always write                           |
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
3. Contact Enrichment Sheet for targeted gaps (ad-hoc, self-service)
4. AI/Claude tier and persona scoring after enrichment completes
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

### May 2026 Enrichment Sprint Results

**Executed:** May 28, 2026 | **Total credits used:** ~12,512 | **Remaining:** ~440K of 456K

| Phase | Description                    | Method                              | Matched | Updated                        | Credits |
| ----- | ------------------------------ | ----------------------------------- | ------- | ------------------------------ | ------- |
| 4     | Company name cascade           | HubSpot associated company backfill | 1,429   | 1,429                          | 0       |
| 5     | Location enrichment            | Apollo bulk_match                   | 329     | 24                             | ~329    |
| 7     | Phone enrichment               | Apollo bulk_match                   | 683     | 0                              | ~683    |
| 8     | Employment history + Apollo ID | Apollo bulk_match                   | 11,500  | 11,403 (history) / 11,500 (ID) | ~11,500 |

**New HubSpot Properties Created:**

- **`employment_history`** (textarea, max 65,000 chars) — Full employment history from Apollo as a JSON array. Each entry: `company` (string, required), `title` (string), `start` (YYYY-MM-01), `end` (YYYY-MM-01), `current` (boolean). Coverage: 11,403 / ~12,884 (88.5%).
- **`apollo_id`** (single-line text) — Apollo person ID for direct future lookups, bypassing name/email matching. Coverage: 11,500 / ~12,884 (89.3%).

**Key Findings:**

- **Phone:** Apollo has zero phone data for contacts already missing phones. Clay waterfall is the only viable phone enrichment path.
- **Location:** Apollo location data is sparse -- only 7% of matches (24 of 329) yielded new location data. Low ROI for location-specific enrichment via Apollo.
- **Employment history:** Extremely rich -- 99.2% of Apollo matches have employment history data. High-value field for persona scoring, org-chart mapping, and deal context.

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
- Apollo has zero phone data for contacts already missing phones in HubSpot. If Apollo doesn't have it on the first match, it won't have it later. Clay waterfall (Clay + Icypeas) is the only viable phone enrichment path.
- Apollo location data is sparse. In the May 2026 sprint, only 7% of matched contacts yielded new city/state/country data. Do not rely on Apollo for location gap-filling.
- Apollo employment history is extremely rich (99.2% of matches). Use `employment_history` for persona scoring, org-chart mapping, and competitive intelligence.

---

## Credit Budget & Projections

**Total Budget:** 456,000 credits
**Renewal Date:** August 2026
**Used to Date:** ~12,512 credits (May 2026 sprint) | **Remaining:** ~440,000 credits

**Usage Breakdown (as of May 2026):**

- May 2026 enrichment sprint: ~12,512 credits (employment history, location, phone phases)
- Phase 2 monthly net-new (ongoing): ~300/month
- **Remaining buffer:** ~440,000 credits (~96% of budget)

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

Applies to: `apollo_account_id`, `apollo_id`, `employment_history`, `account_tier`, `hs_ideal_customer_profile`, `hs_quick_context`, `hs_persona`, `enrichment_source`, `last_enrichment_date`

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
**Resolution:** Use Contact Enrichment Sheet for targeted lookups, manual B2B directory research, outreach to sales for corrections.

**Issue:** Email verification returns high bounce rate
**Resolution:** Quarterly re-verification, implement sender reputation warmup, review list quality.

**Issue:** LinkedIn URLs not syncing from Apollo
**Resolution:** Check Apollo integration sync status, verify field mapping, re-sync recent batch.

---

## Appendix: Integration Checklist

- [x] Apollo HubSpot integration verified (Portal 44523005)
- [ ] Breeze enrichment enabled on new companies
- [x] Contact Enrichment Sheet deployed and shared with team
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

**See 15-AI-Skills-and-Knotch-MCP.md** for the Knotch MCP tools that support enrichment workflows — including `enrich_contact` (Apollo enrichment + HubSpot push), `find_phone` (phone lookup), and `lookup_contact` / `find_contact_by_details` (contact search before enrichment).

**See the [Contact Enrichment Sheet](https://docs.google.com/spreadsheets/d/1n_m-0GODGS0Lj9OCm_HENahzFvVVIND11zVgqcE-6wo/edit?usp=sharing)** for self-service contact lookup, enrichment, and email validation. [Watch the walkthrough recording](https://drive.google.com/file/d/18C23TcPByFHDiJSrj1rUllDoneNF7eIU/view?usp=sharing) before first use.

---

**See Documentation/Events/Event-Lifecycle.md** for how RevOps uses Apollo and Clay to validate event invite lists (Step 1: Align on Invite List) — verifying titles, seniority, company firmographics, and enriching missing contact data before events.

**Questions?** Reach out to Ops. Last updated: May 28, 2026.
