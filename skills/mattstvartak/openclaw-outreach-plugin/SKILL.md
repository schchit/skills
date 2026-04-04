# Finch Outreach - Lead Pipeline

You have access to a full outreach and lead tracking pipeline via the `lead_*` tools. Use them to manage the sales funnel for digital products and services.

## Session Start

Always call `lead_due` first to check for overdue follow-ups. Handle the most overdue leads before starting new outreach.

## After Sending Outreach

Every time you send an email (via gog/gmail), post on a forum, or DM someone:

1. Call `lead_contact` to log the interaction (type, channel, summary).
2. Call `lead_followup` to set the next action and date (typically 3-5 days out for first follow-up).

## After Receiving a Reply

1. Call `lead_contact` to log the inbound message.
2. Call `lead_stage` to advance the stage (e.g., contacted -> replied).
3. Call `lead_followup` to schedule the next step.

## Payment Confirmed

When a payment is confirmed via the payment plugin:

1. Call `lead_contact` with type `payment_received`.
2. Call `lead_stage` to move to `won`.
3. Call `lead_update` to set `actualValue`.

## Follow-up Cadence

- First follow-up: 3 days after initial contact.
- Second follow-up: 5 days after first follow-up.
- If no reply after 2 follow-ups, move to `lost` (if they showed interest) or `dead` (if no engagement at all).

## Weekly Report

At the end of each week:

1. Call `lead_stats` for pipeline summary.
2. Call `lead_export` with format `markdown` for the Notion report.
3. Write the report to Notion via the notion skill.

## Stage Flow

```
identified -> researched -> contacted -> replied -> negotiating -> won
                                      \-> lost (can re-engage -> contacted)
                         any stage -> dead (terminal)
```

## Tips

- Use tags to group leads by campaign, product, or priority.
- Set `estimatedValue` when creating leads to track pipeline value.
- Use the `notes` field to record context the agent needs for personalized follow-ups.
- Use `lead_search` with the `due` flag to find actionable leads.
