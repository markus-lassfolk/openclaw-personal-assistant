# OpenClaw Personal Assistant Ecosystem

Welcome to the Master Guide for the OpenClaw Executive Assistant persona. This repository houses the `personal-assistant` skill and outlines the required ecosystem needed to run a fully capable, highly autonomous personal assistant agent within OpenClaw.

## The Personal Assistant Persona

The Personal Assistant (PA) persona transforms an OpenClaw agent into a proactive, reliable executive assistant. Its core capabilities revolve around:

* **Inbox Triage:** Automatically reading, categorizing, summarizing, and prioritizing incoming communications.
* **Calendar Defense:** Managing scheduling, identifying conflicts, and protecting deep work blocks.
* **Task Extraction:** Parsing emails, meeting notes, and messages to extract actionable tasks and deadlines.
* **Proactive Adaptation:** Learning from your preferences over time to anticipate needs and streamline workflows.
* **Phishing Defense:** Identifying and flagging potentially malicious or socially engineered communications.

## The Required Ecosystem

To fully empower the Personal Assistant persona, several plugins and tools need to be integrated into your OpenClaw environment:

* **[m365-agent-cli](https://github.com/markus-lassfolk/m365-agent-cli):** The core Microsoft 365 tool integration for accessing Exchange, Calendar, Teams, and OneDrive.
* **[openclaw-hybrid-memory](https://github.com/markus-lassfolk/openclaw-hybrid-memory):** Essential for semantic memory, enabling the PA to remember preferences, past interactions, and ongoing context.
* **[humanizer](https://github.com/brandonwise/humanizer):** A tool to adapt writing styles, ensuring the PA communicates naturally and aligns with your personal tone.
* **[Anthropic Skills](https://github.com/anthropics/skills/tree/main/skills):** Specifically the `doc-coauthoring`, `pptx`, `docx`, and `xlsx` skills to allow the PA to read, draft, and modify Office documents seamlessly.

## Installation

To install the Personal Assistant skill into your local OpenClaw workspace:

1. Clone this repository to your local machine.
2. Copy the contents of the `skills/` directory to your OpenClaw workspace skills folder:

```bash
cp -r skills/* ~/.openclaw/workspace/skills/
```

3. Restart your OpenClaw gateway to load the new skill.
