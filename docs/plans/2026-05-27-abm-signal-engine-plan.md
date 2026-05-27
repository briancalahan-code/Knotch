# ABM Signal Engine Implementation Plan

> **For Claude:** REQUIRED: Use using-git-worktrees for isolation, then parallel subagent execution (see Execution Model below).

**Goal:** Build an account-level ABM signal engine that recycles 16 existing HubSpot assets into a scored awareness pipeline with tiered activation routing.

**Architecture:** External Python script (no Operations Hub) computes Signal Score (0-100) and Awareness Stage per company from cross-object HubSpot data. Three routing workflows deliver tier-appropriate activation (Slack alerts, auto-nurture, content drip). Visitor ID integration and job change detection add new signal sources in Phase 2.

**Tech Stack:** Python 3, HubSpot API (CRM v3), HubSpot Workflows (UI-configured), Slack (via HubSpot workflow actions), Apollo API (existing)

**Test command:** `python3 abm-signal-score.py --dry-run --limit 20 && python3 abm-validate.py`
**Pre-execution baseline:** No test suite — ops/CRM project. Validation is API-based (verify properties exist, verify score output against manual assessment).
**Execution mode:** parallel (within phases), sequential (across phases)
**MCP servers:** HubSpot MCP (for property verification and data reads)

---

## Discoveries

_Updated by orchestrator at session end. Captures what agents found that the plan didn't anticipate._

---

## Success Criteria

- [ ] 3 new company properties (`abm_awareness_stage`, `abm_signal_score`, `abm_signal_last_updated`) exist in HubSpot and are populated for all 1,092 tiered accounts
- [ ] Signal Score script runs successfully in dry-run and push modes, producing scores within 0-100 for all tiered accounts
- [ ] `lead_status_numeric` contact property exists and is populated by workflow for all contacts with a Lead Status
- [ ] `previous_jobtitle` contact property exists and snapshot script captures titles before Apollo enrichment
- [ ] Awareness Stage updater workflow fires on `abm_signal_score` change and sets correct stage
- [ ] Tier I Slack alert workflow fires when Signal Score crosses threshold (≥40) for ICP 70+ accounts, with 7-day per-account throttle
- [ ] Tier II weekly digest workflow sends summary of signal-active accounts to AEs
- [ ] Account Signal Dashboard shows awareness stage distribution, signal scores, and tier breakdown
- [ ] Job change detection script identifies title changes between Apollo enrichment runs
- [ ] `icp-score-automation.py` updated to read `abm_signal_score` as engagement input; ICP refresh produces updated scores
- [ ] Attribution Dashboard tracks signal → IPM → deal chain
- [ ] QA validation: 20 manually-assessed accounts match script-computed Signal Scores within ±10 points

---

## Sprint Overview

| Sprint | Name         | Purpose                                                          | Sessions | Status      |
| ------ | ------------ | ---------------------------------------------------------------- | -------- | ----------- |
| 1      | Foundation   | Properties, Signal Score script, Lead Status conversion workflow | 2-3      | NOT STARTED |
| 2      | Routing      | Awareness Stage workflow, Slack alerts, digest, dashboard        | 2        | NOT STARTED |
| 3      | Signals      | Job change detection, visitor ID integration guide, activation   | 2        | NOT STARTED |
| 4      | Intelligence | ICP v3 integration, attribution dashboard, QA, ops runbook       | 2        | NOT STARTED |

### Sprint 1 Complete When:

- [ ] 3 company properties + 2 contact properties created in HubSpot
- [ ] Signal Score script passes dry-run with 1,092 accounts scored
- [ ] Signal Score script pushes successfully to HubSpot (all tiered accounts have `abm_signal_score` > 0 where data exists)
- [ ] `lead_status_numeric` workflow populates numeric values for all contacts

### Sprint 2 Complete When:

- [ ] Awareness Stage workflow transitions accounts correctly based on score thresholds
- [ ] Tier I Slack alert fires (verified with a test account)
- [ ] Weekly digest workflow configured and tested
- [ ] Account Signal Dashboard live in HubSpot with correct data

### Sprint 3 Complete When:

- [ ] Job change detection script captures title diffs from Apollo enrichment
- [ ] Visitor ID integration guide complete (vendor selection, filters, HubSpot config)
- [ ] 3-tier activation sequence configurations documented

### Sprint 4 Complete When:

- [ ] `icp-score-automation.py` reads `abm_signal_score`; ICP refresh produces updated scores
- [ ] Attribution Dashboard live in HubSpot
- [ ] 20-account QA validation passes (±10 points)
- [ ] Ops runbook documented

---

### Task 1: Create ABM HubSpot Properties

**Parallelizable with:** Task 2

**Files:**

- Create: `abm-create-properties.py`
- Reference: `icp-score-automation.py:187-211` (property creation pattern)

**Step 1: Write property creation script**

Write a Python script that creates 5 new HubSpot properties via the CRM v3 Properties API. Follow the pattern from `icp-score-automation.py` (`create_property_if_missing` function). The script should be idempotent — skip properties that already exist.

```python
#!/usr/bin/env python3
"""
Create ABM Signal Engine properties in HubSpot.

Company properties:
  - abm_awareness_stage (dropdown: Unaware, Aware, Engaged, Active, In Pipeline)
  - abm_signal_score (number: 0-100)
  - abm_signal_last_updated (date)

Contact properties:
  - lead_status_numeric (number: 1-5, hidden from UI)
  - previous_jobtitle (text, hidden from UI)

Usage:
  python3 abm-create-properties.py              # dry run
  python3 abm-create-properties.py --push       # execute
"""

import os
import sys
import logging
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip3 install requests")
    sys.exit(1)

HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")
if not HUBSPOT_API_KEY:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
    HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")

if not HUBSPOT_API_KEY:
    print("ERROR: HUBSPOT_API_KEY not set")
    sys.exit(1)

BASE_URL = "https://api.hubapi.com"

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def headers():
    return {"Authorization": f"Bearer {HUBSPOT_API_KEY}", "Content-Type": "application/json"}


def create_property_if_missing(object_type, name, label, prop_type, field_type, group, description, options=None):
    url = f"{BASE_URL}/crm/v3/properties/{object_type}/{name}"
    resp = requests.get(url, headers=headers())
    if resp.status_code == 200:
        log.info(f"  Property '{name}' already exists on {object_type}")
        return True

    url = f"{BASE_URL}/crm/v3/properties/{object_type}"
    payload = {
        "name": name,
        "label": label,
        "type": prop_type,
        "fieldType": field_type,
        "groupName": group,
        "description": description,
    }
    if options:
        payload["options"] = options

    resp = requests.post(url, headers=headers(), json=payload)
    if resp.status_code in (200, 201):
        log.info(f"  Created property '{name}' on {object_type}")
        return True
    else:
        log.error(f"  Failed to create '{name}': {resp.status_code} {resp.text[:300]}")
        return False


def main():
    dry_run = "--push" not in sys.argv
    mode = "DRY RUN" if dry_run else "LIVE"
    log.info(f"ABM Property Creation — {mode}")

    company_props = [
        {
            "name": "abm_awareness_stage",
            "label": "ABM Awareness Stage",
            "type": "enumeration",
            "fieldType": "select",
            "group": "companyinformation",
            "description": "Account-level awareness stage in ABM funnel (Unaware → Aware → Engaged → Active → In Pipeline)",
            "options": [
                {"label": "Unaware", "value": "Unaware", "displayOrder": 0},
                {"label": "Aware", "value": "Aware", "displayOrder": 1},
                {"label": "Engaged", "value": "Engaged", "displayOrder": 2},
                {"label": "Active", "value": "Active", "displayOrder": 3},
                {"label": "In Pipeline", "value": "In Pipeline", "displayOrder": 4},
            ],
        },
        {
            "name": "abm_signal_score",
            "label": "ABM Signal Score",
            "type": "number",
            "fieldType": "number",
            "group": "companyinformation",
            "description": "ABM signal score (0-100). Weighted composite of Lead Status, Event Attendance, Deal Activity, Contact Depth, and Website Engagement.",
        },
        {
            "name": "abm_signal_last_updated",
            "label": "ABM Signal Last Updated",
            "type": "datetime",
            "fieldType": "date",
            "group": "companyinformation",
            "description": "Timestamp of last ABM signal score computation.",
        },
    ]

    contact_props = [
        {
            "name": "lead_status_numeric",
            "label": "Lead Status Numeric",
            "type": "number",
            "fieldType": "number",
            "group": "contactinformation",
            "description": "Numeric conversion of Lead Status for ABM signal aggregation. Cold=1, Attempted=2, Connected=3, Meeting Booked=4, Open Opportunity=5. Auto-set by workflow.",
        },
        {
            "name": "previous_jobtitle",
            "label": "Previous Job Title",
            "type": "string",
            "fieldType": "text",
            "group": "contactinformation",
            "description": "Snapshot of job title before last Apollo enrichment run. Used for job change detection.",
        },
    ]

    if dry_run:
        log.info("Company properties to create:")
        for p in company_props:
            log.info(f"  [DRY RUN] {p['name']} ({p['type']}/{p['fieldType']})")
        log.info("Contact properties to create:")
        for p in contact_props:
            log.info(f"  [DRY RUN] {p['name']} ({p['type']}/{p['fieldType']})")
        log.info("Run with --push to create properties.")
        return

    log.info("Creating company properties...")
    for p in company_props:
        create_property_if_missing("companies", **p)

    log.info("Creating contact properties...")
    for p in contact_props:
        create_property_if_missing("contacts", **p)

    log.info("Done.")


if __name__ == "__main__":
    main()
```

**Step 2: Run dry run to verify**

Run: `python3 abm-create-properties.py`
Expected: Lists 5 properties to create with `[DRY RUN]` prefix. No API writes.

**Step 3: Run with --push**

Run: `python3 abm-create-properties.py --push`
Expected: 5 properties created (or "already exists" if re-run). Zero failures.

**Step 4: Verify properties in HubSpot**

Use HubSpot MCP or API to verify all 5 properties exist:

- Company: `abm_awareness_stage`, `abm_signal_score`, `abm_signal_last_updated`
- Contact: `lead_status_numeric`, `previous_jobtitle`

**Step 5: Commit**

```bash
git add abm-create-properties.py
git commit -m "feat: add ABM property creation script (5 HubSpot properties)"
```

---

### Task 2: Build Lead Status Numeric Conversion Workflow

**Parallelizable with:** Task 1

**Files:**

- Create: `Documentation/Workflows/ABM-Lead-Status-Numeric-Workflow.md` (workflow specification)
- Reference: `Enablement/09-Workflow-Automation-Reference.md` (workflow documentation pattern)

This task is configured in HubSpot UI, not in code. The deliverable is a workflow specification document and a configured HubSpot workflow.

**Step 1: Write workflow specification**

Create `Documentation/Workflows/ABM-Lead-Status-Numeric-Workflow.md` with the complete workflow spec:

```markdown
# ABM Lead Status Numeric Conversion Workflow

**Type:** Contact-based
**Trigger:** `hs_lead_status` field populated or changed
**Action:** Set `lead_status_numeric` property based on Lead Status value
**Re-enrollment:** Yes (if Lead Status changes, numeric value re-evaluated)

## Branch Logic

| Branch # | Condition                        | lead_status_numeric | Lead Status      |
| -------- | -------------------------------- | ------------------- | ---------------- |
| 0        | Lead Status = "Cold"             | 1                   | Cold             |
| 1        | Lead Status = "Attempted"        | 2                   | Attempted        |
| 2        | Lead Status = "Connected"        | 3                   | Connected        |
| 3        | Lead Status = "Meeting Booked"   | 4                   | Meeting Booked   |
| 4        | Lead Status = "Open Opportunity" | 5                   | Open Opportunity |
| 5        | Lead Status = "Bad Fit"          | 0                   | Bad Fit          |
| 6        | Lead Status = "Left Company"     | 0                   | Left Company     |
| 7        | Lead Status = "Junk"             | 0                   | Junk             |
| Default  | Any other value                  | 0                   | Unknown          |

## Exclusion Logic

Bad Fit, Left Company, and Junk contacts receive `lead_status_numeric` = 0.
These contacts are excluded from Signal Score aggregation (the Signal Score
script ignores contacts with `lead_status_numeric` = 0 when computing the
max across company contacts).

## HubSpot Build Steps

1. Navigate to Automation > Workflows > Create workflow > Contact-based
2. Name: `WF | ABM | Lead Status Numeric Conversion`
3. Trigger: Contact property `hs_lead_status` is known (any value)
4. Re-enrollment: ON — re-enroll when `hs_lead_status` changes
5. Add IF/THEN branch for each Lead Status value (8 branches + default)
6. Each branch: Set contact property `lead_status_numeric` to the mapped value
7. Turn ON the workflow
8. Manually enroll all existing contacts to backfill (Settings > Enrollment > Enroll existing)
```

**Step 2: Build the workflow in HubSpot**

Follow the specification above to create the workflow in HubSpot UI:

1. Go to Automation > Workflows > Create workflow > Contact-based
2. Set trigger: `hs_lead_status` is known
3. Enable re-enrollment on `hs_lead_status` change
4. Build 8 IF/THEN branches per the mapping table
5. Turn ON
6. Enroll all existing contacts to backfill

**Step 3: Verify backfill**

After enrollment completes (may take 30-60 minutes for ~11,800 contacts), spot-check 10 contacts:

- Find a contact with Lead Status = "Connected" → verify `lead_status_numeric` = 3
- Find a contact with Lead Status = "Left Company" → verify `lead_status_numeric` = 0
- Find a contact with Lead Status = "Cold" → verify `lead_status_numeric` = 1

**Step 4: Commit the specification**

```bash
git add Documentation/Workflows/ABM-Lead-Status-Numeric-Workflow.md
git commit -m "docs: add ABM Lead Status numeric conversion workflow spec"
```

---

### Task 3: Build Signal Score Computation Script

**Parallelizable with:** None — depends on Task 1 (properties must exist) and Task 2 (lead_status_numeric must be populated)

**Files:**

- Create: `abm-signal-score.py`
- Reference: `icp-score-automation.py` (full script — API helpers, batch update, scoring patterns)
- Reference: `docs/plans/2026-05-27-abm-signal-engine-design.md:67-97` (Signal Score weights and computation)

This is the core deliverable of the ABM engine. The script reads cross-object HubSpot data, computes a weighted Signal Score per company, derives the Awareness Stage, and writes both back to HubSpot.

**Step 1: Write the Signal Score script**

Create `abm-signal-score.py`. The script must:

1. **Read company data:** Paginated search for all tiered companies (account_tier = I, II, or III). Properties needed: `name`, `account_tier`, `icp_score_composite`, `num_associated_contacts`, `num_associated_deals`, `fy25_event_attendance_count`, `fy26_event_attendance_count`, `abm_signal_score` (existing, for change detection), `abm_awareness_stage`, `hs_num_open_deals`, `hs_latest_meeting_activity`, `hs_last_sales_activity_date`.

2. **Read contact data per company:** For each company, fetch associated contacts with properties: `lead_status_numeric`, `hs_seniority`. Compute max `lead_status_numeric` (ignoring 0 values). Track VP+ seniority contacts (apply 2x weight to their Lead Status).

3. **Compute 5-pillar weighted score:**
   - **Lead Status Progression (30%):** Max numeric Lead Status across non-excluded contacts. Score = max_status / 5 \* 100. If any VP+ seniority contact has status ≥ 3, apply 1.3x multiplier (capped at 100).
   - **Event Attendance (20%):** Total events attended + registered. Recency bonus: events in last 90 days count 2x. Score curve: 0 events = 0, 1 event = 30, 2-3 events = 50, 4-5 events = 75, 6+ events = 100.
   - **Deal Activity (25%):** Based on `hs_num_open_deals` and deal pipeline scores. 0 deals = 0. 1+ open deal with pipeline score > 60 = 80. 1+ open deal with pipeline score ≤ 60 = 50. 3+ hygiene tags on any deal = apply 0.5x penalty. For now, simplify to: has_open_deal (yes=60, no=0) + has_recent_sales_activity_30d (yes=+20, no=0) + recent_meeting_30d (yes=+20, no=0). Capped at 100.
   - **Contact Depth (15%):** Associated contact count. Score curve: 0 = 0, 1 = 20, 2-3 = 40, 4-5 = 60, 6-10 = 80, 11+ = 100.
   - **Website Engagement (10%):** Set to 0 at launch (no visitor ID tool yet). The script accepts a `--visitor-data <file.json>` flag for future integration. For now, this pillar scores 0 for all accounts.

4. **Derive Awareness Stage from Signal Score:**
   - Score 0 = Unaware
   - Score 1-19 = Aware
   - Score 20-44 = Engaged
   - Score 45-69 = Active
   - Score 70+ OR has open deal = In Pipeline

5. **Decay logic:** If `abm_signal_last_updated` is > 90 days ago and no new signals detected (score unchanged from previous run), downgrade one stage (Active → Engaged, Engaged → Aware). Never decay below Aware if the account has any historical engagement.

6. **Change detection:** Only push updates for companies where `abm_signal_score` or `abm_awareness_stage` changed from their current HubSpot values.

7. **Batch write:** Use HubSpot batch update API (same pattern as `icp-score-automation.py`).

8. **Logging:** Write detailed run log to `logs/abm-signal-YYYYMMDD-HHMMSS.json` with per-company scores, pillar breakdowns, and stage transitions.

```python
#!/usr/bin/env python3
"""
ABM Signal Score Engine — Knotch HubSpot Portal 44523005

Computes Signal Score (0-100) and Awareness Stage for all tiered
companies based on cross-object HubSpot data. Writes results to
company properties via batch update.

Designed to run on a 6-hour cron. Safe to re-run — only updates
companies whose scores have changed.

Usage:
  python3 abm-signal-score.py                        # dry run, all tiers
  python3 abm-signal-score.py --push                  # execute
  python3 abm-signal-score.py --push --tier I         # single tier
  python3 abm-signal-score.py --dry-run --limit 20    # test with 20 accounts
  python3 abm-signal-score.py --push --visitor-data visitor-signals.json  # with visitor data
"""

import json
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip3 install requests")
    sys.exit(1)

HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")
if not HUBSPOT_API_KEY:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
    HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")

if not HUBSPOT_API_KEY:
    print("ERROR: HUBSPOT_API_KEY not set")
    sys.exit(1)

BASE_URL = "https://api.hubapi.com"
BATCH_SIZE = 100
RATE_LIMIT_DELAY = 0.15

SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"

# Signal Score weights (launch config — rebalanced per stress test)
WEIGHTS = {
    "lead_status": 0.30,
    "event_attendance": 0.20,
    "deal_activity": 0.25,
    "contact_depth": 0.15,
    "website_engagement": 0.10,
}

# Awareness Stage thresholds
STAGE_THRESHOLDS = [
    (70, "In Pipeline"),
    (45, "Active"),
    (20, "Engaged"),
    (1, "Aware"),
    (0, "Unaware"),
]

DECAY_DAYS = 90

COMPANY_PROPERTIES = [
    "name", "account_tier", "icp_score_composite",
    "num_associated_contacts", "num_associated_deals",
    "fy25_event_attendance_count", "fy26_event_attendance_count",
    "abm_signal_score", "abm_awareness_stage", "abm_signal_last_updated",
    "hs_num_open_deals", "hs_last_sales_activity_date",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

# --- The rest of the script follows the icp-score-automation.py patterns ---
# --- Full implementation in Step 3 below ---
```

The full implementation follows the `icp-score-automation.py` structure:

- `headers()` — auth helper (identical)
- `search_companies(filter_groups, properties, limit)` — paginated company search (identical pattern)
- `get_associated_contacts(company_id)` — fetch contacts for a company via associations API
- `batch_update(updates, dry_run)` — batch property writes (identical pattern)
- `score_lead_status(contacts)` — max numeric Lead Status with VP+ seniority bonus
- `score_events(event_count_fy25, event_count_fy26)` — event score with recency bonus
- `score_deal_activity(open_deals, last_sales_activity)` — deal score
- `score_contact_depth(contact_count)` — contact count curve
- `score_website(visitor_data)` — placeholder returning 0 (future: reads visitor-data.json)
- `compute_signal_score(pillars)` — weighted composite
- `derive_awareness_stage(score, has_open_deal)` — threshold-based stage assignment
- `apply_decay(current_stage, last_updated)` — 90-day decay logic
- `main()` — orchestration: parse args, read companies, compute scores, batch write, log results

**Step 2: Run dry run against 20 accounts**

Run: `python3 abm-signal-score.py --dry-run --limit 20`
Expected: 20 accounts scored with pillar breakdowns printed. No API writes. Verify:

- Scores are 0-100
- Companies with associated contacts score higher on Contact Depth
- Companies with events score higher on Event Attendance
- Awareness Stage derivation matches threshold table

**Step 3: Run dry run against all tiered accounts**

Run: `python3 abm-signal-score.py --dry-run`
Expected: 1,092 accounts scored. Review distribution:

- How many Unaware vs. Aware vs. Engaged vs. Active vs. In Pipeline?
- Score histogram: what's the median? What's the spread?
- Any obvious outliers (score 100 or score 0 for a known active account)?

**Step 4: QA 10 accounts manually**

Pick 10 accounts across tiers and manually verify each pillar:

- Check their contacts' Lead Status values against the computed max
- Check their Event Attendance record count against the event score
- Check their deal count against the deal score
- Confirm Awareness Stage matches the derived threshold

**Step 5: Push to HubSpot**

Run: `python3 abm-signal-score.py --push`
Expected: All tiered accounts updated. Log written to `logs/abm-signal-*.json`.

**Step 6: Commit**

```bash
git add abm-signal-score.py
git commit -m "feat: add ABM Signal Score computation script"
```

---

### Task 4: Build Validation Script

**Parallelizable with:** None — depends on Task 3

**Files:**

- Create: `abm-validate.py`
- Reference: `abm-signal-score.py` (reads the same properties)

A lightweight script that reads the ABM properties from HubSpot and validates:

1. All tiered accounts have `abm_signal_score` populated
2. All tiered accounts have `abm_awareness_stage` populated
3. Score distribution is reasonable (no clusters at 0 or 100)
4. `lead_status_numeric` is populated for contacts with Lead Status
5. Stage-to-score mapping is consistent (no Active accounts with score < 20)

```python
#!/usr/bin/env python3
"""
ABM Signal Engine Validation — Knotch HubSpot Portal 44523005

Reads ABM properties and validates data quality.

Usage:
  python3 abm-validate.py                 # full validation
  python3 abm-validate.py --verbose       # show per-account details
"""
# Implementation follows the same API read patterns as icp-score-automation.py
# Reads companies, checks each ABM property, prints summary report
```

**Step 1: Write the validation script**

The script should:

- Search all tiered companies and read `abm_signal_score`, `abm_awareness_stage`, `abm_signal_last_updated`
- Count: how many have score = None? How many have stage = None?
- Check consistency: every account with score ≥ 70 should be "In Pipeline" or "Active"
- Print histogram of scores (0-10, 11-20, 21-30, ..., 91-100)
- Print stage distribution (count per stage)
- Return exit code 0 if all checks pass, 1 if any fail

**Step 2: Run validation**

Run: `python3 abm-validate.py`
Expected: All checks pass. Score distribution printed.

**Step 3: Commit**

```bash
git add abm-validate.py
git commit -m "feat: add ABM validation script"
```

---

### Task 5: Build Awareness Stage Updater Workflow

**Parallelizable with:** Task 6

**Files:**

- Create: `Documentation/Workflows/ABM-Awareness-Stage-Workflow.md`
- Reference: `Documentation/Workflows/ABM-Lead-Status-Numeric-Workflow.md` (workflow doc pattern)

This workflow is a safety net — the Python script already computes and writes the Awareness Stage, but this workflow ensures the stage stays consistent if the score is manually adjusted or if a deal is created between script runs.

**Step 1: Write workflow specification**

```markdown
# ABM Awareness Stage Updater Workflow

**Type:** Company-based
**Trigger:** `abm_signal_score` property changes
**Action:** Set `abm_awareness_stage` based on score thresholds
**Re-enrollment:** Yes (on every score change)

## Branch Logic

| Branch # | Condition                                            | abm_awareness_stage |
| -------- | ---------------------------------------------------- | ------------------- |
| 0        | Company has 1+ open deals (num_associated_deals > 0) | In Pipeline         |
| 1        | abm_signal_score >= 70                               | In Pipeline         |
| 2        | abm_signal_score >= 45 AND abm_signal_score < 70     | Active              |
| 3        | abm_signal_score >= 20 AND abm_signal_score < 45     | Engaged             |
| 4        | abm_signal_score >= 1 AND abm_signal_score < 20      | Aware               |
| Default  | abm_signal_score = 0 or empty                        | Unaware             |

## HubSpot Build Steps

1. Navigate to Automation > Workflows > Create workflow > Company-based
2. Name: `WF | ABM | Awareness Stage Updater`
3. Trigger: Company property `abm_signal_score` is known (any value)
4. Re-enrollment: ON — re-enroll when `abm_signal_score` changes
5. Add IF/THEN branches per table above (check deal count first, then score ranges)
6. Each branch: Set company property `abm_awareness_stage` to mapped value
7. Turn ON (do NOT enroll existing — the Python script already populated stages)
```

**Step 2: Build the workflow in HubSpot UI**

Follow the spec. Configure trigger, branches, and actions.

**Step 3: Test with a single account**

Manually change `abm_signal_score` on a test account (e.g., set to 50). Verify:

- Workflow fires within 15 minutes
- `abm_awareness_stage` updates to "Active"
- Reset the score to its original value afterward

**Step 4: Commit**

```bash
git add Documentation/Workflows/ABM-Awareness-Stage-Workflow.md
git commit -m "docs: add ABM Awareness Stage updater workflow spec"
```

---

### Task 6: Build Tier I Signal Alert Workflow

**Parallelizable with:** Task 5

**Files:**

- Create: `Documentation/Workflows/ABM-Signal-Alert-Workflow.md`
- Reference: `Enablement/09-Workflow-Automation-Reference.md:444-452` (RSVP workflow pattern)

**Step 1: Write workflow specification**

```markdown
# ABM Tier I Signal Alert Workflow

**Type:** Company-based
**Trigger:** `abm_awareness_stage` changes to "Engaged", "Active", or "In Pipeline"
**Action:** Send Slack notification to deal owner / territory owner
**Re-enrollment:** Yes, with 7-day suppression window

## Enrollment Criteria

Company must meet ALL conditions:

- `abm_awareness_stage` is "Engaged" OR "Active" OR "In Pipeline"
- `icp_score_composite` >= 70 (Tier I accounts only)
- `hs_manual_forecast_category` is NOT "COMMIT" and NOT "CLOSED" (suppress for late-stage deals)

## Suppression Logic

- Max 1 alert per company per 7 days
- Implementation: use HubSpot's "Suppress re-enrollment for 7 days" setting on the workflow trigger
- If a company transitions through multiple stages rapidly (Aware → Engaged → Active in one script run), only the final stage triggers an alert

## Slack Notification Template

Channel: #sales-signals (create if needed)

Message format:
🔔 **Signal Alert: {Company Name}**
Tier: I | ICP Score: {icp_score_composite}
Stage: {abm_awareness_stage} | Signal Score: {abm_signal_score}
Owner: {hubspot_owner_id}
Action: Review account and reach out within 48 hours

## HubSpot Build Steps

1. Automation > Workflows > Create > Company-based
2. Name: `WF | ABM | Tier I Signal Alert`
3. Trigger: `abm_awareness_stage` changes
4. Filter: `icp_score_composite` >= 70 AND forecast NOT Commit/Closed
5. Action: Send Slack notification (requires HubSpot Slack integration)
6. Re-enrollment: 7-day suppression
7. Turn ON
```

**Step 2: Create #sales-signals Slack channel**

Ask the team admin to create `#sales-signals` in Slack (or confirm it exists).

**Step 3: Build workflow in HubSpot**

Follow spec. Connect HubSpot Slack integration to the channel.

**Step 4: Test with a test account**

Manually set a Tier I account's `abm_awareness_stage` to "Engaged". Verify Slack notification fires in `#sales-signals`. Reset afterward.

**Step 5: Commit**

```bash
git add Documentation/Workflows/ABM-Signal-Alert-Workflow.md
git commit -m "docs: add ABM Tier I signal alert workflow spec"
```

---

### Task 7: Build Weekly Signal Digest Workflow

**Parallelizable with:** None — depends on Task 5 and Task 6

**Files:**

- Create: `Documentation/Workflows/ABM-Weekly-Digest-Workflow.md`

**Step 1: Write workflow specification**

```markdown
# ABM Weekly Signal Digest Workflow

**Type:** Company-based (scheduled)
**Trigger:** Scheduled — runs every Monday at 8:00 AM ET
**Action:** Internal email to deal owners summarizing signal-active Tier II accounts

## Enrollment Criteria

Company must meet ALL conditions:

- `account_tier` = "II"
- `abm_signal_score` >= 55
- `abm_awareness_stage` is "Engaged" OR "Active"
- `hs_manual_forecast_category` is NOT "COMMIT" and NOT "CLOSED"

## Implementation Options

HubSpot does not natively support scheduled "digest" workflows that aggregate
multiple records into one email. Two approaches:

**Option A (Recommended): HubSpot List + Manual Review**

1. Create active list: "ABM | Tier II Signal Active" with the enrollment criteria
2. Create a recurring HubSpot task (every Monday) assigned to each AE: "Review Tier II signal-active accounts"
3. Task links to the active list for one-click access
4. AE reviews the list, takes action on top accounts

**Option B: External Script + Slack**

1. Python script runs every Monday at 8 AM via cron
2. Queries HubSpot for Tier II accounts meeting criteria
3. Groups by deal owner
4. Posts per-owner digest to Slack DM or #sales-signals

Recommend starting with Option A (zero code, uses existing HubSpot features).
Upgrade to Option B if reps want automated Slack delivery.

## HubSpot Build Steps (Option A)

1. Lists > Create active list > Name: `ABM | Tier II Signal Active`
2. Filter: account_tier = II AND abm_signal_score >= 55 AND abm_awareness_stage IN (Engaged, Active)
3. Create recurring task template for each AE (Automation > Tasks)
4. Link task to the active list URL
```

**Step 2: Build active list and recurring task in HubSpot**

Follow the spec. Create the list, create the recurring task.

**Step 3: Commit**

```bash
git add Documentation/Workflows/ABM-Weekly-Digest-Workflow.md
git commit -m "docs: add ABM weekly signal digest workflow spec"
```

---

### Task 8: Build Account Signal Dashboard

**Parallelizable with:** Task 7

**Files:**

- Create: `Documentation/Dashboards/ABM-Signal-Dashboard.md`
- Reference: `Enablement/04-Pipeline-Hygiene-and-Scoring.md:187-226` (dashboard layout pattern)

**Step 1: Write dashboard specification**

```markdown
# Account Signal Dashboard

**HubSpot Dashboard Name:** ABM Signal Engine
**Audience:** AEs, Sales Managers, RevOps

## Dashboard Layout

**Row 1: Overview**

- Awareness Stage funnel chart (company count per stage: Unaware → Aware → Engaged → Active → In Pipeline)
- Signal Score distribution histogram (0-20, 21-40, 41-60, 61-80, 81-100)

**Row 2: Tier Breakdown**

- Signal Score by Tier (bar chart: avg signal score per Tier I/II/III)
- Awareness Stage by Tier (stacked bar: stage distribution within each tier)

**Row 3: Movement**

- Stage transitions this week (table: company name, previous stage, new stage, signal score)
- New signals this week (table: companies with score increase > 10 points)

**Row 4: Rep View**

- Signal-active accounts by AE (grouped by deal owner, showing accounts at Engaged+ stage)
- Alert response rate (% of Tier I alerts with rep follow-up within 48 hours — tracked manually initially)

## Report Definitions

### Report 1: Awareness Stage Funnel

- Type: Company report
- Filter: `account_tier` is known
- Group by: `abm_awareness_stage`
- Display: Funnel chart
- Sort: stage order (Unaware first)

### Report 2: Signal Score Distribution

- Type: Company report
- Filter: `account_tier` is known, `abm_signal_score` is known
- Group by: `abm_signal_score` (binned: 0-20, 21-40, 41-60, 61-80, 81-100)
- Display: Bar chart

### Report 3: Signal Score by Tier

- Type: Company report
- Filter: `account_tier` is known
- Group by: `account_tier`
- Measure: AVG(`abm_signal_score`)
- Display: Bar chart

### Report 4: Awareness Stage by Tier

- Type: Company report
- Filter: `account_tier` is known
- Group by: `account_tier`, then `abm_awareness_stage`
- Display: Stacked bar chart

### Report 5: Stage Transitions This Week

- Type: Company report
- Filter: `abm_signal_last_updated` within last 7 days
- Columns: Company Name, `abm_awareness_stage`, `abm_signal_score`, `account_tier`, Company Owner
- Sort by: `abm_signal_score` descending
- Display: Table

### Report 6: Signal-Active Accounts by AE

- Type: Company report
- Filter: `abm_awareness_stage` in (Engaged, Active, In Pipeline)
- Group by: Company Owner
- Display: Table grouped by owner

## HubSpot Build Steps

1. Reporting > Dashboards > Create Dashboard
2. Name: "ABM Signal Engine"
3. Create each report per definitions above
4. Arrange reports in the 4-row layout
5. Set default filter: current user's accounts
6. Share with Sales team
```

**Step 2: Build dashboard in HubSpot**

Create each report and arrange in the dashboard. Start with Reports 1 and 2 (the overview charts) — the data from Task 3 must be populated first.

**Step 3: Verify data loads**

Confirm all reports render with actual data. Check that filters work (AE view, Tier filter).

**Step 4: Commit**

```bash
git add Documentation/Dashboards/ABM-Signal-Dashboard.md
git commit -m "docs: add ABM Signal Dashboard specification"
```

---

### Task 9: Build Job Change Detection Script

**Parallelizable with:** Task 10

**Files:**

- Create: `abm-job-change-detect.py`
- Create: `abm-snapshot-titles.py`
- Reference: `icp-score-automation.py` (API patterns)
- Reference: `Enablement/09-Workflow-Automation-Reference.md:20-65` (persona definitions for ICP relevance check)

Two scripts that work together around the Apollo weekly enrichment cycle:

**Script 1: `abm-snapshot-titles.py`** — Run BEFORE Apollo enrichment. Snapshots current `jobtitle` into `previous_jobtitle` for all contacts at tiered accounts.

**Script 2: `abm-job-change-detect.py`** — Run AFTER Apollo enrichment. Compares `jobtitle` to `previous_jobtitle`. Reports changes. Optionally sends Slack alerts for ICP-relevant title changes at Tier I/II accounts.

**Step 1: Write title snapshot script**

```python
#!/usr/bin/env python3
"""
ABM Title Snapshot — Run BEFORE Apollo weekly enrichment.

Copies current jobtitle to previous_jobtitle for all contacts at tiered accounts.
This creates the baseline for job change detection after enrichment.

Usage:
  python3 abm-snapshot-titles.py              # dry run
  python3 abm-snapshot-titles.py --push       # execute
"""
# Reads all contacts at tiered companies
# For each contact: set previous_jobtitle = current jobtitle
# Uses batch update API (same pattern as icp-score-automation.py)
```

**Step 2: Write job change detection script**

```python
#!/usr/bin/env python3
"""
ABM Job Change Detection — Run AFTER Apollo weekly enrichment.

Compares jobtitle to previous_jobtitle for all contacts at tiered accounts.
Reports changes. ICP-relevant changes at Tier I/II accounts get flagged.

ICP-relevant personas (from Enablement/09):
  persona_1 (Demand Gen/Content), persona_3 (Digital Marketing),
  persona_9 (Marketing), persona_10 (Brand), persona_6 (MarTech)

Usage:
  python3 abm-job-change-detect.py                   # detect and report
  python3 abm-job-change-detect.py --slack            # also post to Slack
"""
# Reads contacts at tiered companies
# Compares jobtitle vs previous_jobtitle
# Filters: only report if title actually changed (not None→None)
# Classifies: is new title ICP-relevant? (check against persona keyword lists)
# Output: JSON report to logs/abm-job-changes-YYYYMMDD.json
# Optional: Slack webhook post for Tier I/II ICP-relevant changes
```

**Step 3: Test with dry run**

Run: `python3 abm-snapshot-titles.py` (dry run)
Expected: Lists contacts and their current titles. No writes.

Run: `python3 abm-job-change-detect.py`
Expected: Reports "0 changes detected" (snapshot hasn't been pushed yet, so previous_jobtitle is empty for everyone — this is correct. After the first snapshot + enrichment cycle, real changes will appear.)

**Step 4: Commit**

```bash
git add abm-snapshot-titles.py abm-job-change-detect.py
git commit -m "feat: add job change detection scripts (pre/post Apollo enrichment)"
```

---

### Task 10: Write Visitor ID Integration Guide

**Parallelizable with:** Task 9

**Files:**

- Create: `Documentation/Integrations/Visitor-ID-Integration-Guide.md`
- Reference: `docs/plans/2026-05-27-abm-signal-engine-design.md:131-142` (quality filters)

This is a documentation task, not a code task. The visitor ID tool (RB2B or Warmly) requires procurement and vendor evaluation. This guide documents the integration requirements so the team can evaluate, procure, and configure the tool.

**Step 1: Write integration guide**

```markdown
# Visitor ID Integration Guide

## Purpose

Deanonymize website visitors and push identified contacts to HubSpot,
feeding the ABM Signal Score's Website Engagement pillar (10% weight).

## Vendor Options

| Vendor | Monthly Cost | Key Differentiator                                        |
| ------ | ------------ | --------------------------------------------------------- |
| RB2B   | $500-1,000   | B2B-focused, strong Salesforce/HubSpot native integration |
| Warmly | $700-1,200   | Real-time visitor intent scoring, Slack integration       |

Pricing depends on monthly website traffic. Get Knotch website traffic
volume from Google Analytics before requesting vendor quotes.

## HubSpot Integration Requirements

The visitor ID tool must:

1. Create or match contacts in HubSpot automatically
2. Set `hs_lead_status` to "Cold" for new contacts (default)
3. Associate contacts to existing companies (by domain match)
4. Populate `jobtitle` (triggers persona + seniority auto-assignment)
5. Support filtering by page views (2+) and time on site (30+ seconds)
6. Exclude domains: knotch.com, [competitor domains], gmail.com, yahoo.com, outlook.com

## Quality Filter Configuration

Contacts that do NOT meet quality thresholds:

- Created in HubSpot (for data completeness)
- Lead Status = Cold
- lead_status_numeric = 1
- Do NOT increment Signal Score
- Do NOT trigger Slack alerts

Filter thresholds:

- Page views per session: >= 2
- Time on site: >= 30 seconds
- Company domain: must match existing tiered company OR be ICP-relevant industry

## Signal Score Integration

Once visitor ID is live, update `abm-signal-score.py`:

1. Add --visitor-data flag to accept a JSON file of qualified visitor events
2. The visitor ID tool exports daily visitor data (or the script queries the tool's API)
3. Website Engagement pillar (10% weight) scores based on:
   - 0 qualified visits = 0
   - 1-2 qualified visits in 30 days = 30
   - 3-5 qualified visits = 60
   - 6+ qualified visits = 100

## Privacy Review Checklist

- [ ] Confirm Knotch website privacy policy covers third-party visitor identification
- [ ] Confirm GDPR compliance for EU visitors (consent banner, opt-out mechanism)
- [ ] Confirm CCPA compliance for California visitors
- [ ] Review vendor's data processing agreement (DPA)
- [ ] Confirm data retention policy aligns with Knotch requirements

## Procurement Steps

1. Get website traffic volume from Google Analytics
2. Request quotes from RB2B and Warmly (share traffic volume)
3. Complete privacy review checklist
4. Select vendor and sign contract
5. Configure HubSpot integration per requirements above
6. Implement quality filters
7. Update `abm-signal-score.py` to consume visitor data
8. Monitor first 2 weeks: check contact quality, alert volume, noise level
```

**Step 2: Commit**

```bash
git add Documentation/Integrations/Visitor-ID-Integration-Guide.md
git commit -m "docs: add Visitor ID integration guide with quality filters and privacy checklist"
```

---

### Task 11: Update ICP v3 Scoring Script

**Parallelizable with:** Task 12

**Files:**

- Modify: `icp-score-automation.py` (engagement pillar computation)
- Reference: `docs/plans/2026-05-27-abm-signal-engine-design.md:161-169` (ICP integration spec)
- Reference: `Documentation/CRM/ICP-Scoring-Model-v3.md` (current scoring model)

**Step 1: Read the current engagement pillar computation**

Read `icp-score-automation.py` and find the engagement pillar function. Currently it uses:

- Events (50%): `fy25_event_attendance_count` + `fy26_event_attendance_count`
- Contacts (30%): `num_associated_contacts`
- Deals (20%): `num_associated_deals`

**Step 2: Modify engagement pillar to incorporate Signal Score**

Update the engagement computation to read `abm_signal_score` as a direct input. When `abm_signal_score` is available and > 0, use it as the primary engagement signal (replacing the raw event/contact/deal sub-pillars). When it's 0 or unavailable, fall back to the existing sub-pillar computation.

Logic:

```python
def compute_engagement(events, contacts, deals, abm_signal_score):
    if abm_signal_score is not None and abm_signal_score > 0:
        # Signal Score already aggregates events + contacts + deals + more
        return round(abm_signal_score, 1)
    # Fallback: original sub-pillar computation
    event_score = score_events(events)
    contact_score = score_contacts(contacts)
    deal_score = score_deals(deals)
    return round(event_score * 0.50 + contact_score * 0.30 + deal_score * 0.20, 1)
```

**Step 3: Add `abm_signal_score` to the PROPERTIES list**

Add `"abm_signal_score"` to the `PROPERTIES` list at the top of the script so it's read during the company search.

**Step 4: Test with dry run**

Run: `python3 icp-score-automation.py --tier I`
Expected: Tier I accounts with non-zero `abm_signal_score` now use it for engagement. Compare a few accounts' scores vs. previous run to verify the change is directionally correct (engagement scores should generally increase because Signal Score captures more data).

**Step 5: Commit**

```bash
git add icp-score-automation.py
git commit -m "feat: integrate ABM Signal Score into ICP v3 engagement pillar"
```

---

### Task 12: Build Attribution Dashboard

**Parallelizable with:** Task 11

**Files:**

- Create: `Documentation/Dashboards/ABM-Attribution-Dashboard.md`
- Reference: `docs/plans/2026-05-27-abm-signal-engine-design.md:182-193` (attribution metrics)

**Step 1: Write dashboard specification**

```markdown
# ABM Attribution Dashboard

**HubSpot Dashboard Name:** ABM Signal Attribution
**Audience:** Sales Leadership, RevOps

## Purpose

Track the signal → pipeline → revenue conversion chain to measure
ABM Signal Engine ROI.

## Dashboard Layout

**Row 1: Signal to Pipeline**

- Signal-Attributed IPMs: Deals where company was Aware+ before deal creation
  (compare deal create date vs. abm_signal_last_updated; if signal predates deal, it's attributed)
- Aware-to-IPM Conversion Rate: % of Engaged+ accounts that generated an IPM within 90 days

**Row 2: Pipeline Value**

- Signal-Attributed Pipeline Value: Total deal amount where company had signal before deal
- Signal-Attributed vs. Non-Signal Pipeline (side-by-side bar chart)

**Row 3: Revenue Impact (6-month lag)**

- Signal-Attributed Closed Won: Revenue from deals at previously signal-active accounts
- Win Rate Comparison: Win rate of signal-attributed deals vs. non-signal deals

**Row 4: Leading Indicators**

- Awareness Stage progression velocity (avg days to move from Aware → Engaged → Active)
- Visitor-to-Contact Conversion (when visitor ID is live)

## Report Definitions

### Report 1: Signal-Attributed IPMs

- Type: Deal report
- Filter: Deal stage is IPM or beyond, deal create date >= Signal Engine launch date
- Cross-reference: Company `abm_signal_last_updated` < deal create date
- Note: This requires a custom report or external script — HubSpot cannot natively
  cross-reference company and deal dates in a single report. Use a Python script
  to compute and push a deal-level property `signal_attributed` (yes/no).

### Report 2: Aware-to-IPM Conversion Rate

- Type: Company report
- Numerator: Companies with `abm_awareness_stage` = Engaged/Active/In Pipeline AND associated deal created within 90 days
- Denominator: All companies with `abm_awareness_stage` = Engaged/Active/In Pipeline
- Display: Single number (percentage)

## Implementation Note

Several attribution metrics require cross-object date comparison that HubSpot
reports cannot do natively. Recommend adding a deal-level property
`abm_signal_attributed` (yes/no) populated by the Signal Score script or a
separate attribution script. This enables native HubSpot reporting on attributed deals.

## HubSpot Build Steps

1. Create deal property `abm_signal_attributed` (yes/no dropdown)
2. Write attribution script (or add to `abm-signal-score.py`) that checks:
   for each deal, was the company's `abm_signal_last_updated` before the deal create date?
3. Create dashboard "ABM Signal Attribution" with reports per definitions
4. Share with Sales Leadership
```

**Step 2: Add `abm_signal_attributed` deal property to creation script**

Update `abm-create-properties.py` to add a `deal_props` list with:

```python
deal_props = [
    {
        "name": "abm_signal_attributed",
        "label": "ABM Signal Attributed",
        "type": "enumeration",
        "fieldType": "select",
        "group": "dealinformation",
        "description": "Whether this deal was created at an account that had ABM signal activity before the deal was created.",
        "options": [
            {"label": "Yes", "value": "yes", "displayOrder": 0},
            {"label": "No", "value": "no", "displayOrder": 1},
        ],
    },
]
```

Add a `for p in deal_props: create_property_if_missing("deals", **p)` block in `main()`.
Re-run: `python3 abm-create-properties.py --push` to create the new property.

**Step 3: Build dashboard in HubSpot**

Create reports and arrange per spec.

**Step 4: Commit**

```bash
git add abm-create-properties.py Documentation/Dashboards/ABM-Attribution-Dashboard.md
git commit -m "docs: add ABM Attribution Dashboard spec; add signal_attributed deal property"
```

---

### Task 13: Write Enablement Documentation

**Parallelizable with:** Task 12

**Files:**

- Modify: `Enablement/09-Workflow-Automation-Reference.md` (add ABM workflow family)
- Modify: `Enablement/02-CRM-Architecture-and-Standards.md` (add ABM properties to property inventory)
- Modify: `Enablement/12-Seller-Quick-Reference.md` (add ABM section)
- Create: `Documentation/ABM/ABM-Signal-Engine-Ops-Runbook.md`

**Step 1: Update Workflow Automation Reference**

Add a new section "## ABM Signal Engine Workflows" to `Enablement/09-Workflow-Automation-Reference.md` documenting the 3 new workflows:

1. Lead Status Numeric Conversion
2. Awareness Stage Updater
3. Tier I Signal Alert

Follow the existing workflow documentation pattern (type, trigger, action, branches).

**Step 2: Update CRM Architecture**

Add the 3 new company properties and 2 new contact properties to the "Key Properties Tracked" section in `Enablement/02-CRM-Architecture-and-Standards.md`. Create a new subsection "### ABM Signal Properties" under the existing property groups.

**Step 3: Update Seller Quick Reference**

Add a short ABM section to `Enablement/12-Seller-Quick-Reference.md`:

- What the Signal Dashboard shows
- What Slack alerts mean and expected response
- Where to find signal-active accounts

**Step 4: Write Ops Runbook**

Create `Documentation/ABM/ABM-Signal-Engine-Ops-Runbook.md` covering:

- Script run schedule (Signal Score every 6 hours, title snapshot weekly before Apollo, job change detection weekly after Apollo)
- Cron job setup: document the exact crontab entries (or equivalent scheduler) for all 3 scripts
- Monitoring checklist (weekly alert volume, monthly score QA, quarterly weight review)
- Troubleshooting guide (score not updating, workflow not firing, Slack alerts missing)
- Weight rebalancing procedure
- Kill criteria and escalation path

**Step 5: Configure cron scheduling**

Set up the scheduled jobs for the Signal Score engine:

```bash
# Signal Score — every 6 hours
0 */6 * * * cd /path/to/Knotch && python3 abm-signal-score.py --push >> logs/cron-signal-score.log 2>&1

# Title snapshot — weekly, Sunday 6 PM (before Monday Apollo enrichment)
0 18 * * 0 cd /path/to/Knotch && python3 abm-snapshot-titles.py --push >> logs/cron-snapshot.log 2>&1

# Job change detection — weekly, Tuesday 6 AM (after Monday Apollo enrichment completes)
0 6 * * 2 cd /path/to/Knotch && python3 abm-job-change-detect.py --slack >> logs/cron-job-change.log 2>&1
```

Confirm with one manual run of each script before enabling cron. Document the scheduler host and access details in the ops runbook.

**Step 6: Commit**

```bash
git add Enablement/09-Workflow-Automation-Reference.md \
       Enablement/02-CRM-Architecture-and-Standards.md \
       Enablement/12-Seller-Quick-Reference.md \
       Documentation/ABM/ABM-Signal-Engine-Ops-Runbook.md
git commit -m "docs: add ABM Signal Engine to enablement docs and ops runbook"
```

---

### Task 14: QA Validation and Final Tuning

**Parallelizable with:** None — depends on all previous tasks

**Files:**

- Modify: `abm-signal-score.py` (threshold tuning if needed)
- Reference: `abm-validate.py` (validation output)

**Step 1: Run full validation**

Run: `python3 abm-validate.py --verbose`
Review output for:

- Any tiered accounts missing Signal Score
- Score distribution anomalies
- Stage-to-score consistency

**Step 2: Manual QA — 20 accounts**

Select 20 accounts (5 per tier + 5 mixed):

- 5 Tier I accounts with open deals
- 5 Tier II accounts with event attendance
- 5 Tier III accounts with no engagement
- 5 accounts spanning all tiers with various Lead Status profiles

For each, manually verify:

- Signal Score matches expected pillar contributions
- Awareness Stage matches score threshold
- Lead Status numeric conversion is correct
- If open deal exists, stage should be "In Pipeline"

Document findings in `logs/abm-qa-20-accounts.json`.

**Step 3: Tune thresholds if needed**

If QA reveals systematic scoring issues (e.g., too many accounts at "Active" when they shouldn't be, or too few at "Engaged"), adjust the score thresholds in the STAGE_THRESHOLDS config.

**Step 4: Run ICP refresh**

Run: `python3 icp-score-automation.py --push`
Verify: ICP scores update with new engagement data from Signal Score.

**Step 5: Final commit**

```bash
git add abm-signal-score.py logs/abm-qa-20-accounts.json
git commit -m "feat: ABM Signal Engine QA complete — thresholds tuned, ICP refresh validated"
```

---

## Execution Model

**Dependency Graph:**

```
Task 1 (properties) ──┐
Task 2 (LS workflow)  ─┤── Task 3 (Signal Score script) ── Task 4 (validation)
                       │
                       ├── Task 5 (Awareness workflow) ──┐
                       ├── Task 6 (Slack alert workflow) ─┤── Task 7 (digest)
                       │                                  │
                       │                                  ├── Task 8 (dashboard)
                       │                                  │
Task 9 (job change) ──────────────────────────────────────┤
Task 10 (visitor guide) ──────────────────────────────────┤
                       │                                  │
                       ├── Task 11 (ICP integration) ─────┤── Task 14 (QA)
                       ├── Task 12 (attribution dash) ────┤
                       └── Task 13 (enablement docs) ─────┘
```

**Parallel Waves:**

| Wave    | Tasks                           | Dependencies                                       |
| ------- | ------------------------------- | -------------------------------------------------- |
| Wave 1  | Task 1, Task 2                  | None (independent: properties vs. workflow)        |
| Wave 2  | Task 3                          | Requires Wave 1 (properties + LS workflow exist)   |
| Wave 3a | Task 4                          | Requires Wave 2 (validation of scored data)        |
| Wave 3b | Task 5, Task 6                  | Requires Wave 2; may start parallel with 3a        |
| Wave 4  | Task 7, Task 8, Task 9, Task 10 | Tasks 7+8 require Wave 3b; Tasks 9+10 independent  |
| Wave 5  | Task 11, Task 12, Task 13       | All require Wave 4 complete (data must be flowing) |
| Wave 6  | Task 14                         | Requires all prior waves (full system QA)          |

**Execution notes:**

- Wave 1-2 are the critical path. Task 3 (Signal Score script) is the largest single deliverable and blocks everything downstream.
- Tasks 9 and 10 have no technical dependencies on Waves 1-3 but are logically grouped with Wave 4 because they represent Phase 2 (Integration) work that should wait until Phase 1 (Foundation) is validated.
- Wave 5 tasks are all documentation/integration that require stable data from earlier waves.

**Explicitly deferred (not in scope for this plan):**

- **3-tier activation sequences** (Tier II auto-nurture enrollment, Tier III content drip sequence): The plan builds the routing infrastructure (alert, digest, dashboard) but the actual email/sequence content creation is a marketing deliverable. Document sequence requirements in the ops runbook (Task 13) for the marketing team to build.
- **Parent-child signal propagation**: Signal Score computes at the child company level (where deals and contacts live). Roll-up to parent companies is a Phase 2 consideration after the engine is validated at the child level.

**Test Gate (between waves):**

Script waves (Waves 1-2, 3a):

1. Run: `python3 abm-signal-score.py --dry-run --limit 20 && python3 abm-validate.py`
2. Compare: scores populate without errors, validation passes
3. **Pass:** proceed to next wave
4. **Fail:** stop, debug, fix. Common issues: API auth, missing properties, empty data

**Wave-Specific Completion Gates:**

- **Wave 3a complete when:** `abm-validate.py` passes — all tiered accounts have scores, stage-to-score consistency checks pass
- **Wave 3b complete when:** Awareness Stage workflow fires on a test account (manually change `abm_signal_score`, verify `abm_awareness_stage` updates); Slack alert fires in `#sales-signals` for a Tier I test account
- **Wave 4 complete when:** Weekly digest list populates with Tier II accounts; Account Signal Dashboard renders all 6 reports with data; `abm-snapshot-titles.py --push` runs on 10 test contacts and `abm-job-change-detect.py` runs without errors
- **Wave 5 complete when:** ICP refresh produces updated scores incorporating `abm_signal_score`; Attribution Dashboard has at least Report 1 rendering; enablement docs committed

---

## Recovery State

<!-- Auto-updated during execution. Read this first if resuming after compaction. -->

**Last completed:** {not started}
**Next:** Wave 1, Tasks 1 + 2
**Branch:** main
**Test baseline:** No test suite — validation via `abm-validate.py`
**Key decisions:** External Python script (no Operations Hub). Signal Score weights rebalanced per stress test.
**Blockers:** CRM Ownership cleanup (Jason Lee approval) is a prerequisite for routing workflows but NOT for Signal Score computation.
