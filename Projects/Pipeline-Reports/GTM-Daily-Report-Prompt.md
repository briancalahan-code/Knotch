You are running a daily GTM leadership metrics report for Knotch. Pull fresh data from HubSpot and report what happened yesterday (or since Friday if today is Monday).

## Data Sources

Use the HubSpot MCP connector (search_crm_objects, search_owners) to pull deal and engagement data.

**HubSpot Field Mapping:**

- Pipeline: "72018330" = New/Expansion (the only pipeline we track)
- Deal Stages: "152446547"=IPM, "152455272"=Qualification (Stage 1), "138620983"=Consensus (Stage 2), "138620984"=Proposal (Stage 3), "138620985"=Procurement (Stage 4), "138620988"=Closed Won, "138669962"=Closed Lost
- Key properties: dealname, dealtype, dealstage, pipeline, amount, platform_amt, ipm_held, closedate, createdate, hubspot_owner_id, hs_v2_date_entered_152455272 (date entered Qualification), lead_source, associated_company
- "New Biz" = dealtype "New License". Everything else (Cross-sell, Upsell, Consulting, Winback, Partnership) = "Upsell/Cross-sell"

**New Business Team (for Sales Activity metrics):**
Only track Sales Emails and External Meetings for these owners:

- 693091902=Don Vanderslice
- 349190077=Lee Fine
- 81700088=Tim Long
- 87170480=Pete Davies

**Owner IDs (full team):**
693091902=Don Vanderslice, 702586472=Eli Grant, 723668113=David Brown, 723668771=Andrew Bolton, 627390764=Ben Smith, 349190077=Lee Fine, 88616151=Brian Calahan, 889074486=Tommy Shaker, 758553440=Ryan Ruxton, 2110079045=Carolyn Scott, 81700088=Tim Long, 87170480=Pete Davies

**Fiscal Calendar:** FY runs Feb 1 - Jan 31. Q1=Feb-Apr, Q2=May-Jul, Q3=Aug-Oct, Q4=Nov-Jan. FY27 = Feb 2026 - Jan 2027.

**FY27 Targets:** IPMs Held = 250, Pipeline Created (Platform) = $25M, Bookings (Closed Won) = $7,302,938

## Steps

1. **Determine the lookback window.** Run `date +%u` to get the day of week (1=Monday, 5=Friday).
   - If Monday (1): lookback = Friday 00:00 through Sunday 23:59 (3 days)
   - If Tue-Fri (2-5): lookback = yesterday 00:00 through yesterday 23:59
     Use bash to compute the exact ISO dates for the window start and end.

2. **Pull 5 queries from HubSpot** (pipeline = "72018330" for deal queries):

   **Query A0 -- Recent Sales Emails:** Search engagements (type = EMAIL) where hs_timestamp is within the lookback window AND hubspot_owner_id is IN [693091902, 349190077, 81700088, 87170480]. Return total count, broken out by owner.

   **Query A1 -- Recent External Meetings:** Search engagements (type = MEETING) where hs_timestamp is within the lookback window AND hubspot_owner_id is IN [693091902, 349190077, 81700088, 87170480]. Return total count, broken out by owner.

   **Query A2 -- Today's Meetings (New Biz Team):** Search meetings (objectType = "meetings") where hs_meeting_start_time GTE [today 00:00:00 UTC] AND hs_meeting_start_time LTE [today 23:59:59 UTC] AND hubspot_owner_id IN [693091902, 349190077, 81700088, 87170480]. Properties: hs_meeting_title, hs_meeting_start_time, hs_meeting_end_time, hubspot_owner_id, hs_attendee_owner_ids. For each meeting returned, pull two association queries:
   - Associated contacts: search_crm_objects(objectType="contacts", associatedWith=[{objectType:"meetings", operator:"EQUAL", objectIdValues:[meeting_id]}]), properties: firstname, lastname, jobtitle, company. These are the external attendees.
   - Associated deals: search_crm_objects(objectType="deals", filterGroups=[{filters:[{propertyName:"pipeline", operator:"EQ", value:"72018330"}], associatedWith:[{objectType:"meetings", operator:"EQUAL", objectIdValues:[meeting_id]}]}]), properties: dealname, dealstage, platform_amt, dealtype, hubspot_owner_id. This gives the linked deal context.
     Map hs_attendee_owner_ids (semicolon-delimited) to names using the Owner IDs mapping -- these are internal Knotch attendees beyond the meeting owner. Sort meetings by hs_meeting_start_time ascending.

   **Query B -- Recent IPMs:** search_crm_objects with filter: ipm_held GTE [window_start_date] AND ipm_held LTE [window_end_date]. Properties: dealname, dealtype, dealstage, ipm_held, hubspot_owner_id, platform_amt, amount. This gives you NEW IPMs held in the lookback window.

   **Query C -- Recent Pipeline Created:** search_crm_objects with filter: hs_v2_date_entered_152455272 GTE [window_start_ISO] AND hs_v2_date_entered_152455272 LTE [window_end_ISO]. Properties: dealname, dealtype, platform_amt, hs_v2_date_entered_152455272, hubspot_owner_id. This gives you deals that entered Qualification in the lookback window.

   **Query D -- Recent Bookings:** search_crm_objects with filter: dealstage EQ "138620988" AND closedate GTE [window_start_ISO] AND closedate LTE [window_end_ISO]. Properties: dealname, dealtype, platform_amt, closedate, hubspot_owner_id. This gives you deals closed-won in the lookback window.

3. **Pull FY27 YTD totals** (all with dates >= 2026-02-01):

   **Query E -- YTD Sales Emails:** Engagements type EMAIL, hs_timestamp GTE "2026-02-01", owner IN [693091902, 349190077, 81700088, 87170480]. Total count.

   **Query F -- YTD External Meetings:** Engagements type MEETING, hs_timestamp GTE "2026-02-01", owner IN [693091902, 349190077, 81700088, 87170480]. Total count.

   **Query G -- YTD IPMs:** filter ipm_held GTE "2026-02-01", pipeline EQ "72018330". Just need the total count + count where dealtype = "New License". You can get total from the `total` field in the response and filter in code.

   **Query H -- YTD Pipeline:** filter hs_v2_date_entered_152455272 GTE "2026-02-01", pipeline EQ "72018330". Properties: platform_amt, dealtype. Sum platform_amt, split by New Biz vs Upsell.

   **Query I -- YTD Bookings:** filter dealstage EQ "138620988" AND closedate GTE "2026-02-01", pipeline EQ "72018330". Properties: platform_amt, dealtype. Sum platform_amt, split by New Biz vs Upsell.

   **IMPORTANT:** Paginate all queries if total > 200 using the offset parameter. Do not miss data.

4. **Pull Week-to-Date pacing data.** The WTD window runs Mon through YESTERDAY (not today). On Monday, skip WTD entirely (no prior weekdays yet). Use bash to compute three date windows:
   - **this_week_start**: Monday of the current week (00:00 UTC)
   - **yesterday_end**: Yesterday 23:59:59 UTC
   - **last_week_same_start**: this_week_start minus 7 days
   - **last_week_same_end**: yesterday_end minus 7 days
   - **last_week_start**: Monday of last week (00:00 UTC)
   - **last_week_end**: Friday of last week (23:59:59 UTC)

   Run the following for each of the three windows (this week so far, same days last week, full last week):

   **Query J -- Weekly Sales Emails:** Engagements type EMAIL, hs_timestamp within window, owner IN [693091902, 349190077, 81700088, 87170480]. Total count.

   **Query K -- Weekly External Meetings:** Engagements type MEETING, hs_timestamp within window, owner IN [693091902, 349190077, 81700088, 87170480]. Total count.

   **Query L -- Weekly IPMs:** search_crm_objects with filter: ipm_held GTE [window_start] AND ipm_held LTE [window_end], pipeline EQ "72018330". Total count.

   **Query M -- Weekly Pipeline:** search_crm_objects with filter: hs_v2_date_entered_152455272 GTE [window_start] AND hs_v2_date_entered_152455272 LTE [window_end], pipeline EQ "72018330". Properties: platform_amt. Sum platform_amt.

   **Query N -- Weekly Bookings:** search_crm_objects with filter: dealstage EQ "138620988" AND closedate GTE [window_start] AND closedate LTE [window_end], pipeline EQ "72018330". Properties: platform_amt. Sum platform_amt.

   **Query O -- Top 10 Open Pipeline Deals:** search_crm_objects with filter: pipeline EQ "72018330" AND dealstage IN ["152455272","138620983","138620984","138620985"]. Properties: dealname, dealstage, platform_amt, closedate, hubspot_owner_id. Sort by platform_amt descending, limit 10.

5. **Format the report.** Be concise and scannable. The report has four sections in this order:

```
GTM Daily Update -- [Day, Month Date, Year]

--- MEETINGS TODAY (NB Team [Day] [Mon] [Date]): [total count] ---

[For each meeting, sorted by start time:]
  [HH:MM AM/PM ET] [Meeting Title] -- [Owner Name]
    Attendees: [External Contact Name (Title, Company)], ...
    Internal: [Other Knotch attendee names from hs_attendee_owner_ids, if any]
    Deal: [Deal Name] | [Stage Name] | $[Platform Amt] (or "No linked deal" if none)

[If no meetings today, say "None scheduled"]

--- WHAT HAPPENED YESTERDAY ([Day] [Mon] [Date]) ---
[If Monday, header reads: "WHAT HAPPENED (Fri [Mon] [Date] - Sun [Mon] [Date])"]

Sales Emails (New Biz Team): [total count]
  Don: [n] | Lee: [n] | Tim: [n] | Pete: [n]

External Meetings (New Biz Team): [total count]
  Don: [n] | Lee: [n] | Tim: [n] | Pete: [n]

IPMs Held: [count new]
[For each new IPM, one line:]
  - [Deal Name] | [Owner Name] | [Deal Type] | [Platform Amt or "TBD"] | Held [date]

Pipeline Created: [count new deals] deals, $[total platform amt]
[For each new deal entering Qualification:]
  - [Deal Name] | [Owner Name] | [Deal Type] | $[Platform Amt] | Qualified [date]

Bookings (Closed Won): [count] deals, $[total platform amt]
[For each new closed-won deal:]
  - [Deal Name] | [Owner Name] | [Deal Type] | $[Platform Amt] | Closed [date]

[If nothing new in a category, say "None"]

--- WEEK-TO-DATE (Mon-[Yesterday's Day]) ---
```

**WEEK-TO-DATE pacing logic:** The WTD window covers Monday of the current week through YESTERDAY (not today). This requires two comparison windows:

- **This week so far:** Monday of the current week through yesterday 23:59:59 UTC.
- **Same days last week:** Monday of last week through the same weekday last week (i.e., 7 days before each boundary). This is the apples-to-apples pacing comparison.
- **Full last week:** Monday through Friday of last week. This gives the total to compare pace against.

Run Queries J through N for all three windows using the same query patterns as A0/A1/B/C/D but with adjusted date ranges.

On **Monday**, WTD is empty (no weekdays before today in the current week). Skip the WTD section entirely on Monday -- there is nothing to compare yet.

On **Tuesday**, WTD = Monday only. Show: "[n] (vs [n] Mon last week | [n] full last week)"

On **Wed-Thu**, WTD = Mon-[yesterday]. Show: "[n] (vs [n] through [Yesterday] last week | [n] full last week)"

On **Friday**, WTD = Mon-Thu. Show: "[n] (vs [n] through Thu last week | [n] full last week)"

```
Sales Emails (New Biz Team): [n] (vs [n] through [Yesterday] last week | [n] full last week)
External Meetings (New Biz Team): [n] (vs [n] through [Yesterday] last week | [n] full last week)
IPMs: [n] (vs [n] through [Yesterday] last week | [n] full last week)
Pipeline: $[n] (vs $[n] through [Yesterday] last week | $[n] full last week)
Bookings: $[n] (vs $[n] through [Yesterday] last week | $[n] full last week)

--- FY27 YTD (since Feb 1) ---

Sales Emails (New Biz Team): [YTD total]
External Meetings (New Biz Team): [YTD total]

IPMs Held: [YTD total] of 250 target ([%])
  New Biz: [n] | Upsell: [n]

Pipeline Created: $[YTD] of $25M target ([%])
  New Biz: $[n] | Upsell: $[n]

Bookings: $[YTD] of $7.3M target ([%])
  New Biz: $[n] | Upsell: $[n]

--- TOP 10 OPEN PIPELINE DEALS (BY AMOUNT) ---
[Query HubSpot for deals in pipeline "72018330" in stages Qualification/Consensus/Proposal/Procurement ("152455272","138620983","138620984","138620985"), sorted by platform_amt desc, top 10]
  1. [Deal Name] | [Owner] | [Stage] | $[Platform Amt] | Expected Close [date]
  2. ...
```

## Important Notes

- Always use platform_amt (not amount) for dollar figures. If null/empty, treat as 0.
- Map hubspot_owner_id to names using the owner mapping above. If an ID isn't in the map, call search_owners to look it up.
- Dollar amounts: $1,234,567 format. Percentages: 45.2% format.
- Sales Emails and External Meetings are scoped ONLY to the New Business Team (Don, Lee, Tim, Pete). Do not include other team members.
- No state files needed. Every run is self-contained -- just query HubSpot and report.
- Keep the output tight. Leadership should be able to scan it in 30 seconds.
