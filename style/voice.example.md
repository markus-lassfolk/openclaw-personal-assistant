# Voice and style (example)

Copy this file to `{workspace}/style/voice.md` and customize. The PA skill reads markdown in `{workspace}/style/` before drafting external email.

## Tone

- Professional, warm, concise. No filler or AI clichés.
- Match the executive's level of formality per recipient (internal vs external).

## Sign-off

- Use `signature` from `{workspace}/config/user.json` unless the user specifies otherwise.

## Taboo

- Phrases to avoid: "I hope this email finds you well", "just circling back", "leverage", "synergy" unless the user uses them.

## Scheduling emails

- If `scheduling_cc` is set in `{workspace}/config/user.json`, include those addresses on scheduling-related drafts when appropriate.
- If `scheduling_silent_cc` is set, add as Bcc (or platform equivalent); never mention silent recipients in the body.
