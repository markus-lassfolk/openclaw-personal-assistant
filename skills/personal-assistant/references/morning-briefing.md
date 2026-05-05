# Structured morning briefing

Read this file when producing the **morning briefing** cadence (weekdays; skip only when a holiday source says so). Obey the main `SKILL.md` guardrails (never send external mail without approval; §6–7 security).

On weekdays, and on non-holidays when that information is available, send a concise, proactive morning briefing at the configured time. The briefing should be scannable and action-oriented rather than a dump of everything.

Recommended structure:

```text
Good morning [Name]!

Today:
[List only today's meetings with short context: who, why it matters]

Inbox priority:
[Max 3 items that need action — not a full inbox dump]

Proactive:
[1–2 things the assistant is handling or recommends]
```

Rules:

*   Only report meetings that have not already passed.
*   Distinguish clearly between **needs action** and **FYI**.
*   If the inbox is quiet and there are no meetings, send a short positive note rather than skipping the briefing entirely (for example: "Clear day ahead — no urgent items. Let me know if you'd like to use the time for deep work or catch-up."). Do NOT skip the briefing.
*   If a holiday source or cache exists in the environment, consult it before sending routine weekday briefings.
*   **Maximum length:** Keep the briefing to roughly **250 words** (same cap as the morning-briefing eval). If there is more to cover, prioritize ruthlessly and add a "Full details available on request" note at the end.
*   **Prioritization order:**
    1. Time-sensitive actions (deadlines today, meetings starting soon)
    2. Items requiring the user's decision or reply
    3. FYI items and proactive suggestions
*   **Definition of "actionable":** An item is actionable if it requires the user to reply, decide, approve, attend, or delegate within the current business day.

Optional: write a one-line run log to `{workspace}/logs/pa/morning-briefing.log` (append) if the user wants cron auditability.
