# ICP Scoring Model v3 — Knotch

**Last Updated:** 2026-04-23
**HubSpot Portal:** 44523005
**Model Version:** v3 (replaced v2 on 2026-04-22)
**Script:** `icp-score-automation.py` (repo root)
**Agent Prompt:** `Agent-ICP-Scoring-Prompt.md` (repo root)
**Content Tech Map:** `content-tech-categories.json` (repo root)

---

## What This Is

A four-pillar ICP scoring model that assigns every tiered account (Tier I, II, III) a composite score from 0-100. The score answers: "How well does this company fit Knotch's ideal customer profile?"

v3 replaced v2 on 2026-04-22 because v2 depended 60% on Demandbase data that only covered 81% of accounts. The 203 companies without Demandbase data were capped at 40/100 regardless of actual fit. v3 uses only data sources we control: HubSpot, Apollo, and Clay.

---

## The Four Pillars

Each pillar contributes 25% of the composite score. Equal weights, no redistribution.

| Pillar             | Question It Answers                              | Weight |
| ------------------ | ------------------------------------------------ | ------ |
| Enterprise Fit     | Is this company the right size for Knotch?       | 25%    |
| Digital Maturity   | Is this company digitally sophisticated?         | 25%    |
| Content Investment | Is this company investing in content technology? | 25%    |
| Engagement         | Is this company aware of Knotch?                 | 25%    |

**Fixed penalty model:** If data is missing for a signal, it scores 0. No weight redistribution. A company missing all engagement data has a max composite of 75/100. This is intentional — it makes scores comparable across all accounts and incentivizes data enrichment.

---

## Pillar 1: Enterprise Fit (25%)

Measures whether the company is the right size for Knotch's enterprise motion.

| Signal         | Weight | Property            | Source          |
| -------------- | ------ | ------------------- | --------------- |
| Annual Revenue | 60%    | `annualrevenue`     | Clay enrichment |
| Employee Count | 40%    | `numberofemployees` | HubSpot/Apollo  |

### Revenue Scoring (log scale)

Revenue uses a logarithmic scale because the difference between $1M and $10M matters more than $10B and $11B.

| Revenue | Score    |
| ------- | -------- |
| $0      | 0        |
| $100K   | ~0       |
| $1M     | ~4       |
| $10M    | ~18      |
| $100M   | ~36      |
| $500M   | ~54      |
| $1B     | ~63      |
| $5B+    | 85 (cap) |

Cap is 85, not 100 — even the largest companies don't get a perfect revenue score because revenue alone doesn't make a great customer.

### Employee Scoring (stepped curve)

| Employees | Score |
| --------- | ----- |
| 0         | 0     |
| 1,000     | 10    |
| 5,000     | 30    |
| 10,000    | 50    |
| 50,000    | 80    |
| 100,000+  | 100   |

**Formula:** `enterprise_fit = revenue_score * 0.60 + employee_score * 0.40`

---

## Pillar 2: Digital Maturity (25%)

Measures whether the company has a sophisticated digital presence and technology stack.

| Signal              | Weight | Property                        | Source          |
| ------------------- | ------ | ------------------------------- | --------------- |
| Monthly Web Traffic | 50%    | `clay__website_traffic_monthly` | Clay/SimilarWeb |
| Tech Stack Breadth  | 30%    | `num_technologies`              | Clay/BuiltWith  |
| Content/SEO Proxy   | 20%    | derived from `num_technologies` | Calculated      |

### Web Traffic Scoring (log scale)

| Monthly Visits | Score |
| -------------- | ----- |
| 0              | 0     |
| 10K            | ~0    |
| 100K           | ~30   |
| 500K           | ~51   |
| 1M             | ~61   |
| 5M             | ~81   |
| 20M+           | 100   |

### Tech Stack Scoring (stepped)

| Technologies | Score |
| ------------ | ----- |
| 0            | 0     |
| 100          | 20    |
| 200          | 40    |
| 400          | 70    |
| 600+         | 100   |

### Content/SEO Proxy

Simple: `min(100, num_technologies / 6)`. Companies with 600+ technologies max out. This is a rough proxy for content/SEO sophistication based on overall tech investment.

**Formula:** `digital_maturity = traffic_score * 0.50 + tech_score * 0.30 + content_proxy * 0.20`

---

## Pillar 3: Content Investment (25%)

Measures whether the company is actively investing in content technology — Knotch's core market.

| Signal              | Weight | Property                        | Source                       |
| ------------------- | ------ | ------------------------------- | ---------------------------- |
| Content Tech Count  | 70%    | derived from `web_technologies` | BuiltWith via classification |
| Marketing Headcount | 30%    | `marketing_headcount`           | Apollo enrichment            |

### Content Tech Classification

The `web_technologies` field in HubSpot contains a semicolon-separated list of BuiltWith-detected technologies (internal enum values). The file `content-tech-categories.json` maps 152 of these to 8 content categories:

| Category             | Count | Examples                                              |
| -------------------- | ----- | ----------------------------------------------------- |
| analytics            | 41    | google_analytics, mixpanel, amplitude, hotjar         |
| marketing_automation | 32    | hubspot, marketo, pardot, eloqua                      |
| email_marketing      | 26    | sendgrid, mailchimp, klaviyo, constant_contact        |
| cms                  | 24    | wordpress, drupal, sitecore, adobe_experience_manager |
| personalization      | 20    | optimizely, dynamic_yield, monetate, mutiny           |
| tag_management       | 5     | google_tag_manager, tealium, segment                  |
| dam                  | 4     | cloudinary, contently, kapost, percolate              |

Technologies NOT in the mapping are non-content (infrastructure, CRM, e-commerce, etc.) and are ignored for this pillar.

### Content Tech Scoring

| Content Techs | Score |
| ------------- | ----- |
| 0             | 0     |
| 5             | 30    |
| 10            | 50    |
| 15            | 70    |
| 20            | 85    |
| 30+           | 100   |

### Marketing Headcount Scoring

| Headcount      | Score             |
| -------------- | ----------------- |
| None (missing) | 0 (fixed penalty) |
| 0              | 0                 |
| 1              | 30                |
| 6              | 60                |
| 21             | 80                |
| 50+            | 100               |

**Formula:** `content_investment = content_tech_score * 0.70 + marketing_hc_score * 0.30`

---

## Pillar 4: Engagement (25%)

Measures whether the company is already aware of and engaged with Knotch.

| Signal                       | Weight | Property                                                     | Source               |
| ---------------------------- | ------ | ------------------------------------------------------------ | -------------------- |
| Event Attendance (FY25+FY26) | 50%    | `fy25_event_attendance_count`, `fy26_event_attendance_count` | HubSpot lists        |
| Associated Contacts          | 30%    | `num_associated_contacts`                                    | HubSpot (calculated) |
| Associated Deals             | 20%    | `num_associated_deals`                                       | HubSpot (calculated) |

### Event Scoring

FY25 and FY26 event counts are summed.

| Total Events | Score |
| ------------ | ----- |
| 0            | 0     |
| 1            | 30    |
| 3            | 50    |
| 6            | 75    |
| 10+          | 100   |

### Contact Scoring

| Contacts | Score |
| -------- | ----- |
| 0        | 0     |
| 2        | 20    |
| 6        | 40    |
| 16       | 60    |
| 31       | 80    |
| 50+      | 100   |

### Deal Scoring

| Deals | Score |
| ----- | ----- |
| 0     | 0     |
| 1     | 40    |
| 2     | 60    |
| 4     | 80    |
| 7+    | 100   |

**Formula:** `engagement = event_score * 0.50 + contact_score * 0.30 + deal_score * 0.20`

---

## Composite Score

```
icp_composite = enterprise_fit * 0.25 + digital_maturity * 0.25 + content_investment * 0.25 + engagement * 0.25
```

### Score Bands

| Band   | Range  | Meaning                                |
| ------ | ------ | -------------------------------------- |
| High   | 70-100 | Strong ICP fit across multiple pillars |
| Medium | 50-69  | Good fit with some data or signal gaps |
| Low    | 0-49   | Weak fit or significant missing data   |

---

## Data Completeness

Each account gets a `icp_data_completeness` score (0-100) showing how much data backed its ICP score.

| Component           | Points | Condition                                     |
| ------------------- | ------ | --------------------------------------------- |
| Enterprise Fit      | 25     | Always present (employee count always exists) |
| Tech stack          | 25     | `num_technologies` > 0                        |
| Content tech        | 17.5   | Content tech count > 0                        |
| Marketing headcount | 7.5    | `marketing_headcount` is not null             |
| Events              | 12.5   | FY25 + FY26 event count > 0                   |
| Contacts            | 7.5    | `num_associated_contacts` > 0                 |
| Deals               | 5      | `num_associated_deals` > 0                    |

Use data completeness to filter reports. An account scoring 45 with 100% completeness is genuinely low-fit. An account scoring 45 with 50% completeness might score higher once enriched.

---

## HubSpot Properties

### Input Properties (data sources)

| Property                        | Type                    | Source                           | Coverage                          |
| ------------------------------- | ----------------------- | -------------------------------- | --------------------------------- |
| `account_tier`                  | Enum ("I", "II", "III") | Manual/workflow                  | 1,092 accounts                    |
| `numberofemployees`             | Number                  | HubSpot/Apollo                   | ~100%                             |
| `annualrevenue`                 | Number                  | Clay enrichment                  | ~100%                             |
| `clay__website_traffic_monthly` | Number                  | Clay/SimilarWeb                  | ~100%                             |
| `web_technologies`              | Multi-enum              | BuiltWith → HubSpot              | ~98%                              |
| `num_technologies`              | Number                  | Calculated from web_technologies | ~98%                              |
| `marketing_headcount`           | Number                  | Apollo dept headcount            | ~99% (enriched 2026-04-23)        |
| `fy25_event_attendance_count`   | Number                  | HubSpot list membership          | ~25% (engagement grows over time) |
| `fy26_event_attendance_count`   | Number                  | HubSpot list membership          | ~25%                              |
| `num_associated_contacts`       | Number                  | HubSpot calculated               | 100% (may be 0)                   |
| `num_associated_deals`          | Number                  | HubSpot calculated               | 100% (may be 0)                   |

### Output Properties (written by script)

| Property                       | Type     | Description                       |
| ------------------------------ | -------- | --------------------------------- |
| `icp_score_composite`          | Number   | Overall ICP score (0-100)         |
| `icp_enterprise_fit_score`     | Number   | Pillar 1 score (0-100)            |
| `clay__digital_maturity_score` | Number   | Pillar 2 score (0-100)            |
| `icp_content_investment_score` | Number   | Pillar 3 score (0-100)            |
| `icp_engagement_score`         | Number   | Pillar 4 score (0-100)            |
| `icp_data_completeness`        | Number   | Data backing percentage (0-100)   |
| `icp_model_version`            | String   | "v3"                              |
| `icp_score_last_updated`       | DateTime | UTC timestamp of last scoring run |

---

## How to Run

### Prerequisites

- Python 3 with `requests` and `python-dotenv`
- `.env` file in repo root with `HUBSPOT_API_KEY` and `APOLLO_API_KEY`
- `content-tech-categories.json` in repo root

### Commands

```bash
# Dry run — calculates scores, prints summary, does NOT write to HubSpot
python3 icp-score-automation.py

# Live — calculates and pushes all scores to HubSpot
python3 icp-score-automation.py --push
```

The script:

1. Creates any missing HubSpot properties (first run only)
2. Pulls all Tier I, II, III companies from HubSpot
3. Loads the content tech classification map
4. Computes all four pillar scores + composite + data completeness
5. Only pushes accounts where scores changed (skips unchanged)
6. Writes a JSON log to `logs/` with full results

### Run Order

If you've just done an enrichment push (marketing headcount, tech stack, etc.), re-run ICP scoring after:

```bash
# 1. Run any enrichment scripts first
python3 marketing-headcount-enrich.py --push

# 2. Then re-score
python3 icp-score-automation.py --push
```

### Recommended Cadence

- **Monthly** — or after any bulk enrichment push
- **After event attendance updates** — if FY25/FY26 event counts change
- **After new accounts are tiered** — new companies added to Tier I/II/III

---

## Marketing Headcount Enrichment

A companion script enriches the `marketing_headcount` field via Apollo's departmental headcount API.

```bash
# Dry run
python3 marketing-headcount-enrich.py

# Live
python3 marketing-headcount-enrich.py --push
```

The script:

1. Finds all tiered companies missing `marketing_headcount` in HubSpot
2. Enriches via Apollo bulk org enrichment (`departmental_head_count.marketing`)
3. Pushes results to HubSpot
4. Logs Apollo misses to `logs/` for manual follow-up

**As of 2026-04-23:** 493 companies enriched (454 bulk + 31 single-org retry + 7 alt-domain + 1 via Clay domain lookup). Coverage went from 55% to 99%.

---

## Current Score Distribution (2026-04-23)

| Band           | Count     | %     |
| -------------- | --------- | ----- |
| High (70+)     | 39        | 3.6%  |
| Medium (50-69) | 362       | 33.2% |
| Low (<50)      | 691       | 63.3% |
| **Total**      | **1,092** |       |

### Data Completeness

| Completeness | Count |
| ------------ | ----- |
| 100%         | 119   |
| 75-99%       | 962   |
| 50-74%       | 10    |
| <50%         | 1     |

### Top 10 Accounts

| Company        | Composite | Tier | EF   | DM   | CI    | EN    | DC   |
| -------------- | --------- | ---- | ---- | ---- | ----- | ----- | ---- |
| Salesforce     | 85.8      | II   | 89.0 | 75.1 | 100.0 | 79.2  | 100% |
| Google         | 85.3      | III  | 91.0 | 70.5 | 95.8  | 83.8  | 100% |
| TD Bank        | 84.9      | I    | 90.9 | 74.9 | 100.0 | 73.9  | 100% |
| Accenture      | 84.6      | I    | 91.0 | 75.0 | 79.0  | 93.3  | 100% |
| SAP            | 83.2      | II   | 91.0 | 70.8 | 79.0  | 92.0  | 100% |
| BlackRock      | 82.9      | I    | 77.0 | 54.5 | 100.0 | 100.0 | 100% |
| JPMorgan Chase | 81.2      | I    | 91.0 | 64.0 | 70.0  | 100.0 | 100% |
| IBM            | 80.3      | II   | 91.0 | 80.1 | 100.0 | 50.0  | 95%  |
| Intuit         | 78.1      | I    | 73.1 | 77.1 | 100.0 | 62.4  | 100% |
| PwC            | 77.5      | I    | 91.0 | 63.1 | 100.0 | 56.0  | 100% |

### Remaining Data Gaps

| Signal              | Missing | Impact                                            |
| ------------------- | ------- | ------------------------------------------------- |
| Events (FY25+FY26)  | 907     | Largest gap — most accounts have no event history |
| Deals               | 869     | Most accounts don't have deals yet                |
| Contacts            | 226     | Some accounts have no contacts in HubSpot         |
| Content tech        | 8       | Near-complete                                     |
| Marketing headcount | 8       | Near-complete after Apollo enrichment             |
| Employees           | 1       | Effectively complete                              |
| Revenue             | 0       | Complete                                          |

The engagement pillar (events + contacts + deals) is the primary driver of low scores. This is expected — engagement data grows as Knotch builds relationships with accounts. Companies scoring Medium with low engagement are strong enrichment-driven fits waiting for sales activity.

---

## Version History

| Version | Date       | Key Change                                                |
| ------- | ---------- | --------------------------------------------------------- |
| v3      | 2026-04-22 | Four-pillar model, removed Demandbase dependency entirely |
| v2      | 2026-03-25 | Three-pillar with 60% Demandbase dependency               |

---

## Related Files

| File                                             | Purpose                                   |
| ------------------------------------------------ | ----------------------------------------- |
| `icp-score-automation.py`                        | Scoring script (run this)                 |
| `marketing-headcount-enrich.py`                  | Marketing headcount enrichment via Apollo |
| `content-tech-categories.json`                   | 152-technology content classification map |
| `Agent-ICP-Scoring-Prompt.md`                    | AI agent prompt for running ICP scoring   |
| `docs/plans/2026-04-22-icp-scoring-v3-design.md` | Original design document                  |
| `logs/icp-score-*.json`                          | Run logs with full scoring details        |
| `logs/mktg-hc-enrich-*.json`                     | Marketing headcount enrichment logs       |
