# ICP Scoring Agent Prompt

**Purpose:** Reusable prompt for computing four-pillar ICP scores for any tier of accounts. Designed to be run by an AI agent with HubSpot MCP access and Python execution capability.

**Last Updated:** 2026-04-22
**Model Version:** v3 (Four-Pillar, no Demandbase)
**Design Doc:** docs/plans/2026-04-22-icp-scoring-v3-design.md

---

## Prompt

You are an ICP scoring agent for the Knotch HubSpot instance (Portal ID: 44523005). Your job is to compute four pillar scores and one composite score for a set of company accounts and push them to HubSpot.

### Scoring Model Overview

Four equal-weight pillars (25% each), fixed penalty model (missing data = 0, no weight redistribution):

| Pillar                   | Measures                   | Signals                                                    |
| ------------------------ | -------------------------- | ---------------------------------------------------------- |
| Enterprise Fit (25%)     | Right size for Knotch?     | Revenue (60%) + Employees (40%)                            |
| Digital Maturity (25%)   | Digitally sophisticated?   | Web traffic (50%) + Tech stack (30%) + Content proxy (20%) |
| Content Investment (25%) | Investing in content tech? | Content tech count (70%) + Marketing headcount (30%)       |
| Engagement (25%)         | Aware of Knotch?           | Events (50%) + Contacts (30%) + Deals (20%)                |

### Step 1: Pull Target Accounts from HubSpot

Use `search_crm_objects` to pull companies by tier. Filter on `account_tier` (values: "I", "II", "III"). Pull these properties:

- `name`, `account_tier`
- `numberofemployees`, `annualrevenue`
- `web_technologies`, `num_technologies`, `clay__website_traffic_monthly`
- `marketing_headcount`
- `fy25_event_attendance_count`, `fy26_event_attendance_count`
- `num_associated_contacts`, `num_associated_deals`

Paginate as needed (max 200 per page).

### Step 2: Load Content Tech Classification

Load `content-tech-categories.json` from the repo root. This maps HubSpot `web_technologies` internal enum values to content categories (cms, analytics, marketing_automation, personalization, tag_management, dam, email_marketing). Technologies not in the mapping are non-content (infrastructure, CRM, e-commerce, etc.).

Count content technologies per company: split `web_technologies` by semicolon, count values that appear in the mapping.

### Step 3: Compute Pillar Scores

#### Pillar 1: Enterprise Fit

```python
def score_revenue(revenue):
    if revenue <= 0: return 0
    if revenue >= 5_000_000_000: return 85
    log_val = math.log10(max(revenue, 1))
    return min(85, max(0, (log_val - 5) / 4.7 * 85))

def score_employees(employees):
    if employees >= 100_000: return 100
    if employees >= 50_000: return 80 + (employees - 50_000) / 50_000 * 20
    if employees >= 10_000: return 50 + (employees - 10_000) / 40_000 * 30
    if employees >= 5_000: return 30 + (employees - 5_000) / 5_000 * 20
    if employees >= 1_000: return 10 + (employees - 1_000) / 4_000 * 20
    return employees / 1_000 * 10

enterprise_fit = score_revenue(revenue) * 0.60 + score_employees(employees) * 0.40
```

#### Pillar 2: Digital Maturity

```python
# Web Traffic (50%) — log scale, 20M monthly = 100
if web_traffic <= 0: traffic_score = 0
elif web_traffic >= 20_000_000: traffic_score = 100
else:
    log_val = math.log10(max(web_traffic, 1))
    traffic_score = min(100, max(0, (log_val - 4) / 3.3 * 100))

# Tech Stack Breadth (30%)
if tech_count >= 600: tech_score = 100
elif tech_count >= 400: tech_score = 70 + (tech_count - 400) / 200 * 30
elif tech_count >= 200: tech_score = 40 + (tech_count - 200) / 200 * 30
else: tech_score = tech_count / 200 * 40

# Content/SEO Proxy (20%)
content_proxy = min(100, tech_count / 6)

digital_maturity = traffic_score * 0.50 + tech_score * 0.30 + content_proxy * 0.20
```

#### Pillar 3: Content Investment

```python
def score_content_tech(count):
    if count >= 30: return 100
    if count >= 20: return 85 + (count - 20) / 10 * 15
    if count >= 15: return 70 + (count - 15) / 5 * 15
    if count >= 10: return 50 + (count - 10) / 5 * 20
    if count >= 5: return 30 + (count - 5) / 5 * 20
    return count / 5 * 30

def score_marketing_headcount(headcount):
    if headcount is None: return 0  # fixed penalty when missing
    if headcount >= 50: return 100
    if headcount >= 21: return 80 + (headcount - 21) / 29 * 20
    if headcount >= 6: return 60 + (headcount - 6) / 15 * 20
    if headcount >= 1: return 30 + (headcount - 1) / 5 * 30
    return 0

content_investment = score_content_tech(content_tech_count) * 0.70 + score_marketing_headcount(marketing_hc) * 0.30
```

#### Pillar 4: Engagement

```python
def score_events(fy25, fy26):
    total = (fy25 or 0) + (fy26 or 0)
    if total >= 10: return 100
    if total >= 6: return 75 + (total - 6) / 4 * 25
    if total >= 3: return 50 + (total - 3) / 3 * 25
    if total >= 1: return 30 + (total - 1) / 2 * 20
    return 0

def score_contacts(count):
    if count >= 50: return 100
    if count >= 31: return 80 + (count - 31) / 19 * 20
    if count >= 16: return 60 + (count - 16) / 15 * 20
    if count >= 6: return 40 + (count - 6) / 10 * 20
    if count >= 2: return 20 + (count - 2) / 4 * 20
    return 0

def score_deals(count):
    if count >= 7: return 100
    if count >= 4: return 80 + (count - 4) / 3 * 20
    if count >= 2: return 60 + (count - 2) / 2 * 20
    if count >= 1: return 40
    return 0

engagement = score_events(fy25, fy26) * 0.50 + score_contacts(contacts) * 0.30 + score_deals(deals) * 0.20
```

#### Composite

```python
icp_composite = enterprise_fit * 0.25 + digital_maturity * 0.25 + content_investment * 0.25 + engagement * 0.25
```

No adaptive redistribution. If a pillar has missing data, it scores 0 and the company's max composite is reduced accordingly.

### Step 4: Compute Data Completeness

```python
completeness = 25  # Enterprise Fit always present
completeness += 25 if num_technologies > 0 else 0
completeness += 17.5 if content_tech_count > 0 else 0
completeness += 7.5 if marketing_headcount is not None else 0
completeness += 12.5 if (fy25_events + fy26_events) > 0 else 0
completeness += 7.5 if num_contacts > 0 else 0
completeness += 5 if num_deals > 0 else 0
```

### Step 5: Push Scores to HubSpot

Use `manage_crm_objects` to update each company with:

- `icp_score_composite` — overall score (0-100)
- `clay__digital_maturity_score` — Pillar 2 score
- `icp_enterprise_fit_score` — Pillar 1 score
- `icp_content_investment_score` — Pillar 3 score
- `icp_engagement_score` — Pillar 4 score
- `icp_data_completeness` — metadata (0-100)
- `icp_model_version` — "v3"
- `icp_score_last_updated` — current UTC timestamp

Batch in groups of 10 (HubSpot MCP limit). Track success/failure counts.

### Step 6: Verify

Spot-check 5-10 accounts by pulling them back from HubSpot and confirming scores match.

### Step 7: Report Results

Provide a summary with:

- Total accounts scored
- Score distribution: High (70+), Medium (50-69), Low (<50)
- Data completeness distribution: 100%, 75-99%, 50-74%, <50%
- Top 10 by ICP Composite with pillar breakdown
- Missing data counts per signal

---

## Formula Summary

### ICP Composite

| Pillar             | Weight | Signals                                                                                                                |
| ------------------ | ------ | ---------------------------------------------------------------------------------------------------------------------- |
| Enterprise Fit     | 25%    | Revenue (60%, log-scale, $5B cap) + Employees (40%, enterprise curve)                                                  |
| Digital Maturity   | 25%    | Web Traffic (50%, log-scale) + Tech Stack (30%, stepped curve) + Content Proxy (20%)                                   |
| Content Investment | 25%    | Content Tech Count (70%, from web_technologies classification) + Marketing Headcount (30%, fixed penalty when missing) |
| Engagement         | 25%    | Events FY25+FY26 (50%) + Associated Contacts (30%) + Associated Deals (20%)                                            |

### HubSpot Properties

| Property                        | Type         | Direction | Notes                               |
| ------------------------------- | ------------ | --------- | ----------------------------------- |
| `account_tier`                  | enum         | Input     | "I", "II", "III"                    |
| `numberofemployees`             | number       | Input     | HubSpot/Apollo                      |
| `annualrevenue`                 | number       | Input     | Clay enrichment                     |
| `web_technologies`              | enum (multi) | Input     | BuiltWith -> HubSpot                |
| `num_technologies`              | number       | Input     | Calculated from web_technologies    |
| `clay__website_traffic_monthly` | number       | Input     | Clay/SimilarWeb                     |
| `marketing_headcount`           | number       | Input     | Demandbase/Apollo (55% coverage)    |
| `fy25_event_attendance_count`   | number       | Input     | HubSpot lists                       |
| `fy26_event_attendance_count`   | number       | Input     | HubSpot lists                       |
| `num_associated_contacts`       | number       | Input     | HubSpot (calculated)                |
| `num_associated_deals`          | number       | Input     | HubSpot (calculated)                |
| `icp_score_composite`           | number       | Output    | 0-100, four-pillar weighted average |
| `clay__digital_maturity_score`  | number       | Output    | 0-100, Pillar 2                     |
| `icp_enterprise_fit_score`      | number       | Output    | 0-100, Pillar 1                     |
| `icp_content_investment_score`  | number       | Output    | 0-100, Pillar 3                     |
| `icp_engagement_score`          | number       | Output    | 0-100, Pillar 4                     |
| `icp_data_completeness`         | number       | Output    | 0-100, metadata                     |
| `icp_model_version`             | string       | Output    | "v3"                                |
| `icp_score_last_updated`        | datetime     | Output    | UTC timestamp                       |

---

## Notes

- **v3 replaces v2 (2026-03-25).** Demandbase dependency eliminated entirely.
- **Fixed penalty model.** Missing data scores 0 — no weight redistribution. A company missing engagement data has a max ICP of 75/100.
- **Data completeness.** `icp_data_completeness` shows how much data backed each score. Use it to filter reports (e.g., "show only accounts with 75%+ data completeness").
- **Refresh cadence.** Monthly, or after any enrichment push. Run order: `techstack-consolidate.py --push` -> `icp-score-automation.py --push`
- **Content tech classification.** Based on `content-tech-categories.json` (152 technologies across 8 categories). Update the JSON to add/remove technologies as HubSpot's enum evolves.
