# Due today: draft pings and notify

Run this checklist when the **due-today** cadence fires (for example a morning cron), or when the user asks to clear tasks due today. Follow the main `SKILL.md` for delegation flags, autonomy envelope, and **never send external email without explicit approval** in the current session.

## Before you start

1. Load `{workspace}/config/user.json` if it exists (see main `SKILL.md` workspace layout).
2. Resolve the executive mailbox / user context for task and mail commands.

## Steps

1. **List tasks due today** using the user's task system (e.g. Microsoft To Do / Planner via `m365-agent-cli`, or equivalent). Prefer the same system the user actively uses; deduplicate vs Planner if both exist.
2. **Classify each item:**
   - **Internal** (no external ping): skip drafting mail; optionally update notes or remind in-channel only.
   - **External follow-up owed** (user promised someone something today, or a stakeholder is waiting): prepare a **draft** reply or new message.
3. **Draft pings:** For each external follow-up, create a **draft** (thread-aware reply when possible). Apply voice/style from `{workspace}/style/` if present. Do not send.
4. **Scheduling visibility:** If `scheduling_cc` / `scheduling_silent_cc` exist in `user.json`, apply them to scheduling-related drafts per main `SKILL.md` scheduling rules.
5. **Notify the user** with a compact checklist:
   - Task title (and due date)
   - Draft location / thread summary
   - What requires their approval to send
6. If nothing needs external mail, still send a short "due today" summary of internal tasks.

## After

Optionally append one line to `{workspace}/logs/pa/due-today.log` with date and count of drafts prepared.
