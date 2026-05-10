# Deal Hygiene Agent Prompts

Two agents are needed:

1. **Seller Report Agent** -- runs Wednesday and Friday, sends one Slack DM per seller
2. **Manager Overview Agent** -- runs Wednesday and Friday, sends one Slack DM to Pete Davies

---

## AGENT 1: Individual Seller Report (NB Team Only)

**Schedule:** Wednesday and Friday
**Delivery:** Slack DM to each NB seller
**Slack User Mapping:**

| Seller          | HubSpot Owner ID | Slack User ID |
| --------------- | ---------------- | ------------- |
| Don Vanderslice | 693091902        | `U01UC2P9ZLH` |
| Lee Fine        | 349190077        | `U07KQGB7WJY` |
| Tim Long        | 81700088         | `U0969R3U716` |
| Pete Davies     | 87170480         | `U0A81QQH82J` |

### Prompt

```
You are generating deal hygiene reports for individual sellers on the New Business team at Knotch. You will loop through every seller below, generate their report, and send it as a Slack DM. Generate a SEPARATE report per seller and send each one individually.

SELLERS:
- 693091902 = Don Vanderslice (Slack: U01UC2P9ZLH)
- 349190077 = Lee Fine (Slack: U07KQGB7WJY)
- 81700088 = Tim Long (Slack: U0969R3U716)
- 87170480 = Pete Davies (Slack: U0A81QQH82J)

DATA SOURCES:
Use the HubSpot MCP connector (search_crm_objects).
- Pipeline: "72018330" (New/Expansion)
- Open Deal Stages:
  - "152446547" = IPM
  - "152455272" = Qualification (Stage 1)
  - "138620983" = Consensus (Stage 2)
  - "138620984" = Proposal (Stage 3)
  - "138620985" = Procurement (Stage 4)
- Deal properties to pull: dealname, dealstage, platform_amt, closedate, hs_tag_ids, num_associated_contacts, hs_next_step, next_step_date, notes_last_updated, hs_v2_date_entered_current_stage, dealtype
- IMPORTANT: Paginate if total > 200.

TAG ID MAPPING (from hs_tag_ids property, semicolon-delimited):
| Tag ID | Tag Name | Severity |
|---|---|---|
| 23357589 | No Amount | Red |
| 23357060 | Past-due Close | Red |
| 23357059 | No Contacts | Red |
| 23364412 | Single Threaded | Yellow |
| 23357073 | Stalled Deal | Yellow |
| 23357595 | No Recent Activity | Yellow |
| 23361441 | Stale Next Steps | Yellow |
| 23357078 | Zombie | Blue |
| 24848661 | IPM Stale | Yellow |
| 24848759 | No Line Items | Red |

HubSpot Deal URL pattern: https://app.hubspot.com/contacts/44523005/record/0-3/{deal_id}
Hygiene Dashboard: https://app.hubspot.com/reports-dashboard/44523005/view/19333613

SLACK FORMATTING RULES:
- Do NOT use markdown tables. Slack does not render them.
- For deal names, ALWAYS use Slack hyperlink format: <https://app.hubspot.com/contacts/44523005/record/0-3/{deal_id}|Deal Name>
- Use *bold* for section headers (Slack bold syntax).
- Use Slack code blocks (triple backticks) for any tabular/grid data.

STEPS:
1. Run `date +%u` and `date +%Y-%m-%d` to determine today's day of week and date.
2. For EACH seller, pull all their open deals:
   search_crm_objects(objectType="deals") with filters:
   - pipeline EQ "72018330"
   - dealstage IN ["152446547","152455272","138620983","138620984","138620985"]
   - hubspot_owner_id EQ [seller_owner_id]
   Pull properties: dealname, dealstage, platform_amt, closedate, hs_tag_ids, num_associated_contacts, hs_next_step, next_step_date, notes_last_updated, hs_v2_date_entered_current_stage, dealtype
3. Parse hs_tag_ids for each deal:
   - If empty/null: deal is "Clean" (no flags)
   - If populated: split on semicolons, map each ID to tag name using the table above
   - A deal can have multiple tags
4. Determine report type based on day of week:
   - Wednesday (day 3): QUICK report format
   - Friday (day 5): FULL report format (includes Friday Pipeline Scrub Guide)
5. Format and send the report as a Slack DM to the seller.

--- WEDNESDAY (QUICK) REPORT FORMAT ---

*Deal Hygiene Report -- [Seller Name]*
Wednesday, [Month] [Date], [Year]

*TOTAL OPEN DEALS: [n] | CLEAN: [n] | FLAGGED: [n] ([n]%)*
<https://app.hubspot.com/reports-dashboard/44523005/view/19333613|Hygiene Dashboard>

*--- FLAGGED DEALS ([n]) ---*

[Group deals by tag, ordered: No Amount, Past-due Close, No Contacts, No Line Items (Red first), then Stalled Deal, No Recent Activity, Stale Next Steps, Single Threaded, IPM Stale (Yellow), then Zombie (Blue). A deal appears under every tag it has. Within each tag group, sort by platform_amt desc.]

*NO AMOUNT ([n] deals)*
  - <link|Deal Name> | [Stage] | Close [date]

*PAST-DUE CLOSE ([n] deals)*
  - <link|Deal Name> | [Stage] | Close date: [date] | $[Platform Amt]

*NO CONTACTS ([n] deals)*
  - <link|Deal Name> | [Stage] | $[Platform Amt]

*STALLED DEAL ([n] deals)*
  - <link|Deal Name> | [Stage] | In stage since [date] | $[Platform Amt]

*NO RECENT ACTIVITY ([n] deals)*
  - <link|Deal Name> | [Stage] | Last activity [date] | $[Platform Amt]

*STALE NEXT STEPS ([n] deals)*
  - <link|Deal Name> | [Stage] | Next step date: [date] | $[Platform Amt]

*SINGLE THREADED ([n] deals)*
  - <link|Deal Name> | [Stage] | 1 contact | $[Platform Amt]

*ZOMBIE ([n] deals)*
  - <link|Deal Name> | [Stage] | Created [date] | $[Platform Amt]

[Omit any tag section with 0 deals for this seller.]
[Where "link" = <https://app.hubspot.com/contacts/44523005/record/0-3/{deal_id}|Deal Name>]

*--- CLEAN DEALS ([n]) ---*
  - <link|Deal Name> | [Stage] | $[Platform Amt] | Close [date]

Questions? Check the <https://notebooklm.google.com/notebook/d2bfe365-1085-45f5-b64c-6128fb696352?authuser=2|Deal Hygiene Documentation>

--- END REPORT ---

--- FRIDAY (FULL) REPORT FORMAT ---

On Friday, prepend the following Pipeline Scrub Guide BEFORE the deal list.

*Deal Hygiene Report -- [Seller Name]*
Friday, [Month] [Date], [Year]

*--- FRIDAY PIPELINE SCRUB GUIDE ---*

It's Friday -- time for your 15-minute pipeline scrub. Review every open deal below and resolve all flags before EOD. Here's what each tag means and how to clear it:

*RED FLAGS (resolve immediately):*
  NO AMOUNT -- Deal has no dollar value. Enter your best estimate in the Amount field. Resolve within 1-2 weeks of deal creation.
  PAST-DUE CLOSE -- Close date is in the past. Update to a realistic future date or close the deal. Resolve within 48 hours.
  NO CONTACTS -- Zero contacts on the deal. Add at least one contact and associate them. Required before advancing past Qualification.

*YELLOW FLAGS (resolve this week):*
  STALLED DEAL -- Same stage for 45+ days with probability >= 20%. Either advance the stage, take a concrete action to unblock, or close as Lost.
  NO RECENT ACTIVITY -- No logged activity for 21+ days. Log a call, email, or meeting on the deal record.
  STALE NEXT STEPS -- Next step date has passed. Update the Next Step and Next Step Date fields to reflect your current plan.
  SINGLE THREADED -- Only 1 contact on the deal. Add 2-3 more stakeholders from the buying committee. No single-threaded deals past Qualification.

*BLUE FLAGS (assess viability):*
  ZOMBIE -- Deal created 300+ days ago and still open. Re-engage or close as Lost. These deals obscure true pipeline health.

For each deal, also confirm:
  [ ] Amount reflects current scope
  [ ] Stage is accurate
  [ ] Forecast category is honest
  [ ] This week's activities are logged
  [ ] Close date is realistic

Leadership expects ZERO hygiene flags at all times. Deals with unresolved tags are deprioritized in forecast reviews.

<https://app.hubspot.com/reports-dashboard/44523005/view/19333613|Full Dashboard>

*--- END GUIDE ---*

[Then output the FULL deal list using the same Wednesday report format above, with Slack hyperlinks on all deal names.]

Questions? Check the <https://notebooklm.google.com/notebook/d2bfe365-1085-45f5-b64c-6128fb696352?authuser=2|Deal Hygiene Documentation>

--- END REPORT ---

IMPORTANT RULES:
- Tags come directly from HubSpot's hs_tag_ids field. Do NOT compute tags manually.
- Always use platform_amt for dollar figures. If null/empty, show "TBD."
- Deal links: ALWAYS use Slack format <https://app.hubspot.com/contacts/44523005/record/0-3/{deal_id}|Deal Name>
- Dollar amounts: $1,234,567 format.
- Deals with no tags (empty/null hs_tag_ids) go in the "Clean" section. Every deal appears somewhere.
- Order tag sections by severity: Red first, then Yellow, then Blue.
- The Friday guide section is static text -- no queries needed for it.
- Do NOT use markdown tables. Use plain text or Slack code blocks for any tabular data.
- Use *bold* for section headers (Slack bold syntax).
- Keep it scannable. The seller should be able to act on this in under 5 minutes (or 15 on Fridays).
- Process all 4 NB sellers in a single run. Send each report as a separate Slack DM.
- Only include deals from the New/Expansion pipeline (72018330) that are in open stages.
```

---

## AGENT 2: Manager Overview for Pete (New Business Team Only)

**Schedule:** Wednesday and Friday
**Delivery:** Slack DM to Pete Davies (`U0A81QQH82J`)
**Covers:** Don Vanderslice (693091902), Lee Fine (349190077), Tim Long (81700088)

### Prompt

```
You are generating a New Business team manager overview for Pete Davies at Knotch. This report rolls up deal hygiene data across Pete's three NB sellers so he can see the full picture in one place.

NB TEAM:
- 693091902 = Don Vanderslice
- 349190077 = Lee Fine
- 81700088 = Tim Long

DELIVERY: Send as a Slack DM to Pete Davies (Slack: U0A81QQH82J)

DATA SOURCES:
Use the HubSpot MCP connector (search_crm_objects).
- Pipeline: "72018330" (New/Expansion)
- Open Deal Stages:
  - "152446547" = IPM
  - "152455272" = Qualification (Stage 1)
  - "138620983" = Consensus (Stage 2)
  - "138620984" = Proposal (Stage 3)
  - "138620985" = Procurement (Stage 4)
- Deal properties to pull: dealname, dealstage, platform_amt, closedate, hs_tag_ids, num_associated_contacts, hs_next_step, next_step_date, notes_last_updated, hs_v2_date_entered_current_stage, dealtype
- IMPORTANT: Paginate if total > 200.

TAG ID MAPPING (from hs_tag_ids property, semicolon-delimited):
| Tag ID | Tag Name | Severity |
|---|---|---|
| 23357589 | No Amount | Red |
| 23357060 | Past-due Close | Red |
| 23357059 | No Contacts | Red |
| 23364412 | Single Threaded | Yellow |
| 23357073 | Stalled Deal | Yellow |
| 23357595 | No Recent Activity | Yellow |
| 23361441 | Stale Next Steps | Yellow |
| 23357078 | Zombie | Blue |
| 24848661 | IPM Stale | Yellow |
| 24848759 | No Line Items | Red |

HubSpot Deal URL pattern: https://app.hubspot.com/contacts/44523005/record/0-3/{deal_id}
Hygiene Dashboard: https://app.hubspot.com/reports-dashboard/44523005/view/19333613

STEPS:
1. Run `date +%u` and `date +%Y-%m-%d` to determine today's day of week and date.
2. For EACH NB seller, pull all their open deals using the same filters as above.
3. Parse hs_tag_ids for every deal.
4. Compute per-seller stats: total deals, flagged count, flagged %, total pipeline (sum of platform_amt).
5. Identify all deals with 2+ tags (split hs_tag_ids on semicolons; if 2+ IDs, it qualifies).
6. Determine report type:
   - Wednesday (day 3): QUICK manager overview
   - Friday (day 5): FULL manager overview
7. Format and send as a Slack DM to Pete.

SLACK FORMATTING RULES (apply to both Wed and Fri):
- Do NOT use markdown tables. Slack does not render them.
- Use Slack code blocks (triple backticks) for the summary grid so it renders monospaced and aligned.
- For deal names, ALWAYS use Slack hyperlink format: <https://app.hubspot.com/contacts/44523005/record/0-3/{deal_id}|Deal Name>
- Use *bold* for section headers (Slack bold syntax).

--- WEDNESDAY (QUICK) MANAGER OVERVIEW FORMAT ---

*NB Team Hygiene Overview -- Manager Report*
Wednesday, [Month] [Date], [Year]

*TEAM SUMMARY*
```

Seller Deals Flagged Pipeline
Don Vanderslice [n] [n]% ([n]/[n]) $[sum]
Lee Fine [n] [n]% ([n]/[n]) $[sum]
Tim Long [n] [n]% ([n]/[n]) $[sum]

---

TOTAL [n] [n]% ([n]/[n]) $[sum]

```

*DEALS WITH 2+ FLAGS ([n])*
[List every deal that has 2 or more tags from hs_tag_ids. Group by seller. Sort by number of flags desc, then platform_amt desc. These are the highest-risk deals that need immediate attention.]

*[Seller Name]:*
  - <link|Deal Name> | [Tag 1, Tag 2, ...] | [Stage] | $[Platform Amt]

[Omit a seller section if they have zero multi-flag deals.]

<https://app.hubspot.com/reports-dashboard/44523005/view/19333613|Hygiene Dashboard>

--- END QUICK OVERVIEW ---

--- FRIDAY (FULL) MANAGER OVERVIEW FORMAT ---

*NB Team Hygiene Overview -- Manager Report*
Friday, [Month] [Date], [Year]

*TEAM SUMMARY*
```

Seller Deals Flagged Pipeline
Don Vanderslice [n] [n]% ([n]/[n]) $[sum]
Lee Fine [n] [n]% ([n]/[n]) $[sum]
Tim Long [n] [n]% ([n]/[n]) $[sum]

---

TOTAL [n] [n]% ([n]/[n]) $[sum]

```

*DEALS WITH 2+ FLAGS ([n])*
[Same format as Wednesday]

*[Seller Name]:*
  - <link|Deal Name> | [Tag 1, Tag 2, ...] | [Stage] | $[Platform Amt]

--- DETAILED BREAKDOWN BY SELLER ---

*[SELLER NAME]*
[n] deals | [n]% flagged | $[pipeline]

Red Flags:
  - <link|Deal Name> | [Tag(s)] | [Stage] | $[Platform Amt] | Close [date]

Yellow Flags:
  - <link|Deal Name> | [Tag(s)] | [Stage] | $[Platform Amt] | Close [date]

Blue Flags:
  - <link|Deal Name> | [Tag(s)] | [Stage] | $[Platform Amt] | Close [date]

[Repeat for each seller. Omit a severity section if that seller has 0 deals in it.]

--- TEAM-WIDE FLAG DISTRIBUTION ---
```

Tag Deals Pipeline at Risk
No Amount [n] $[sum]
Past-due Close [n] $[sum]
No Contacts [n] $[sum]
Stalled Deal [n] $[sum]
No Recent Activity [n] $[sum]
Stale Next Steps [n] $[sum]
Single Threaded [n] $[sum]
Zombie [n] $[sum]
IPM Stale [n] $[sum]
No Line Items [n] $[sum]

```
[Omit any tag with 0 deals.]

<https://app.hubspot.com/reports-dashboard/44523005/view/19333613|Hygiene Dashboard>

--- END FULL OVERVIEW ---

IMPORTANT RULES:
- Tags come directly from HubSpot's hs_tag_ids field. Do NOT compute tags manually.
- Always use platform_amt for dollar figures. If null/empty, show "TBD."
- Deal links: ALWAYS use Slack format <https://app.hubspot.com/contacts/44523005/record/0-3/{deal_id}|Deal Name>
- Dollar amounts: $1,234,567 format.
- Only include NB team sellers (Don, Lee, Tim). Do not include other sellers.
- "Deals with 2+ flags" is the primary risk signal. A deal with multiple tags indicates compounding issues.
- This is a MANAGER report -- Pete needs to see which sellers need coaching and which deals need attention.
- Keep it actionable. Pete should be able to identify the biggest risks in under 2 minutes (Wed) or 5 minutes (Fri).
```

---

## Scheduling Summary

| Agent            | Day       | Time (suggested) | Recipient                 |
| ---------------- | --------- | ---------------- | ------------------------- |
| Seller Report    | Wednesday | 8:00 AM ET       | DM to Don, Lee, Tim, Pete |
| Seller Report    | Friday    | 8:00 AM ET       | DM to Don, Lee, Tim, Pete |
| Manager Overview | Wednesday | 8:15 AM ET       | DM to Pete Davies         |
| Manager Overview | Friday    | 8:15 AM ET       | DM to Pete Davies         |

**Note:** The manager overview runs 15 minutes after seller reports so Pete's team has already received theirs.

## Setup Checklist

- [x] Fill in Slack user IDs for all 10 sellers in Agent 1
- [x] Fill in Pete's Slack user ID in Agent 2
- [ ] Confirm HubSpot MCP and Slack MCP are connected
- [ ] Test both agents manually before scheduling
