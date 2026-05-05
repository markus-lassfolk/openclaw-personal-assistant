# Weekly planning brief (email to proposed schedule to approval to calendar)

When the user asks for weekly planning help (or the environment triggers a weekly planning run), close the loop between:

*   Recent inbound signals (email)
*   The user's todo list
*   The coming week's calendar

The goal is to produce a proposed schedule and only write back to the calendar after explicit user approval.

## Step A — Gather inputs

*   Read recent emails (unread + recent relevant threads) and extract:
    - Meetings / appointments that need scheduling
    - Deadlines and time-specific commitments
    - Bills / administrative tasks
    - Work tasks and deliverables
*   Read the calendar for the coming week. *(m365-agent-cli: `calendar week [--mailbox <user_email>]`)*
*   Get the user's todo list:
    - From the user directly, OR
    - From previously extracted tasks (To Do / Planner), OR
    - By asking a single concise question if missing

## Step B — Generate a proposed schedule (do not write yet)

Generate a proposed schedule that follows these rules:

*   **No-overwrite rule:** never delete, modify, or move existing calendar events without explicit user approval.
*   **Time-specific first:** schedule time-specific tasks at their required times.
*   **Deep work first:** place harder / deeper work earlier in the day.
*   **Buffer time:** add 10–15 minutes buffer between work blocks.
*   **Grouping:** group similar tasks together to reduce context switching.
*   **Human constraints:** leave realistic space for meals, breaks, and travel.
*   **Conflicts:** flag conflicts and unclear items for user review (do not guess).

Output format (recommended):

*   A short "Week-at-a-glance" summary
*   Per-day proposed blocks with:
    - Title
    - Start/end time
    - Category (`deep work`, `admin`, `meeting`, `personal`, etc.)
    - Notes / assumptions
*   A "Conflicts & Questions" section

## Step C — Explicit approval gate

Before creating any calendar events:

*   Ask the user to approve the proposed schedule.
*   Offer granular approval: "approve all", "approve day X", or "approve only these blocks".
*   If the user requests changes, revise the proposal and re-confirm.

## Step D — Commit: create calendar events (write-back)

Only after approval, create the approved events in the calendar using whatever tooling is available. *(m365-agent-cli: `create-event <title> [start] [end] --day <date> [--mailbox <user_email>]`)*

Guardrails:

*   Create new events; do not edit existing events unless the user explicitly asked for edits.
*   If running in delegated mode, ensure the correct account is targeted. *(m365-agent-cli: include `--mailbox <user_email>`)*
*   After creating events, re-read the affected day/week and report what was created.
