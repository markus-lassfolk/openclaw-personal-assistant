# OpenClaw Personal Assistant Ecosystem

Welcome to the Master Guide for the OpenClaw Executive Assistant persona. This repository houses the **`personal-assistant`** skill (one skill directory with **`SKILL.md`** plus **`references/`** runbooks) and outlines the ecosystem for a capable, autonomous personal assistant inside OpenClaw.

## The Personal Assistant persona

The PA persona helps the agent act as a proactive executive assistant:

* **Inbox triage:** Reading, categorizing, summarizing, and prioritizing incoming communications.
* **Calendar defense:** Scheduling, conflicts, deep-work protection, and scheduling CC / Bcc rules from config.
* **Task extraction:** Action items from email, notes, and meetings; due-today draft pings (approval before send).
* **Proactive adaptation:** Preferences over time; **`{workspace}/style/`** for voice and tone.
* **Phishing defense:** Flagging suspicious or socially engineered communications.
* **Document collaboration:** OneDrive and SharePoint workflows via your tooling (for example **m365-agent-cli** plus Office document skills).

## Skill layout (OpenClaw + Anthropic patterns)

This repo follows [OpenClaw Skills](https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md) (AgentSkills-compatible: YAML frontmatter, progressive disclosure) and the directory conventions from [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) (`SKILL.md` + optional **`references/`**).

```text
skills/personal-assistant/
  SKILL.md              # Entry point (single-line frontmatter for OpenClaw)
  evals/
    evals.json          # Skill-creator eval prompts + verifiable expectations
  references/           # Runbooks loaded when cadence or user request matches
    morning-briefing.md
    due-today-drafts.md
    post-meeting.md
    weekly-planning.md
    m365-commands.md
    failure-modes.md
```

Instructions use **`{baseDir}`** for paths inside the skill folder and **`{workspace}`** for your OpenClaw workspace (config, style, state, logs).

## Required ecosystem

* **[m365-agent-cli](https://github.com/markus-lassfolk/m365-agent-cli):** Microsoft 365 reference implementation (Exchange, Calendar, To Do, Planner, OneDrive). The skill remains tool-agnostic; substitute other CLIs when needed.
* **[openclaw-hybrid-memory](https://github.com/markus-lassfolk/openclaw-hybrid-memory):** Semantic memory for preferences and context (recommended for OpenClaw).
* **[humanizer](https://github.com/brandonwise/humanizer):** Optional polish; **`{workspace}/style/`** wins on conflict.
* **[Anthropic Skills](https://github.com/anthropics/skills/tree/main/skills):** For example `doc-coauthoring`, `pptx`, `docx`, and `xlsx` for Office documents.

## Installation

1. Clone this repository.
2. Copy the skill folder into your OpenClaw workspace **`skills/`** directory:

```bash
cp -r skills/personal-assistant ~/.openclaw/workspace/skills/
```

3. Copy **config** and **style** templates into the workspace (same `workspace` root as above):

```bash
mkdir -p ~/.openclaw/workspace/config ~/.openclaw/workspace/style
cp config/user.example.json ~/.openclaw/workspace/config/user.json
cp style/voice.example.md ~/.openclaw/workspace/style/voice.md
```

Edit **`user.json`** with your emails, timezone, `workspace` absolute path, `signature`, and optional `scheduling_cc` / `scheduling_silent_cc`. Customize **`style/voice.md`** for tone.

4. Reload skills (new session or gateway restart). See [Creating skills](https://github.com/openclaw/openclaw/blob/main/docs/tools/creating-skills.md).

### Optional: load from a clone via `extraDirs`

If you prefer not to copy the skill, point OpenClaw at this repo (paths are examples):

```json5
{
  skills: {
    load: {
      extraDirs: ["/path/to/openclaw-personal-assistant/skills"],
    },
  },
}
```

Workspace skills override **`extraDirs`** when the same skill name is present in both—see [Skills — locations and precedence](https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md).

### State and logs

`state/` and `logs/` under the **git repo** are gitignored for local scratch. On the machine, you may create **`{workspace}/state/pa/`** and **`{workspace}/logs/pa/`** for optional PA caches and cron logs (see `SKILL.md`).

## Smoke tests

```bash
openclaw skills list
openclaw agent --message "Run the morning briefing cadence for the personal-assistant skill using its references file."
openclaw agent --message "List my tasks due today and draft follow-up emails for approval; use personal-assistant runbooks."
```

## Anthropic skill-creator: clone and benchmark

A local clone of the upstream repo is used to run the official eval tooling (aggregate viewer, schemas). Clone path used for this project:

`F:/GitHub/anthropics-skills` (repository: [anthropics/skills](https://github.com/anthropics/skills))

**Eval definitions** for this skill live in [`skills/personal-assistant/evals/evals.json`](skills/personal-assistant/evals/evals.json) (`skill_name` must match the skill frontmatter). Schema: [skill-creator `references/schemas.md`](https://github.com/anthropics/skills/blob/main/skills/skill-creator/references/schemas.md).

### Full pipeline (Claude Code + skill-creator)

The skill-creator [`SKILL.md`](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) describes the intended loop: for each eval, spawn **with-skill** and **baseline** runs, capture outputs under an iteration directory, add `grading.json` per run (see `agents/grader.md`), then aggregate:

```bash
cd F:/GitHub/anthropics-skills/skills/skill-creator
python scripts/aggregate_benchmark.py F:/GitHub/openclaw-personal-assistant/eval-workspace/iteration-1
```

Then launch the review viewer (from the same machine, with a display if available):

```bash
python eval-viewer/generate_review.py F:/GitHub/openclaw-personal-assistant/eval-workspace/iteration-1 --skill-name personal-assistant --benchmark F:/GitHub/openclaw-personal-assistant/eval-workspace/iteration-1/benchmark.json
```

Create `eval-workspace/iteration-1/` and the `eval-N/with_skill/` … `grading.json` tree as documented in skill-creator, or follow the **Improve** flow inside Claude Code with the **skill-creator** skill enabled.

### Quick check without the viewer

Run each `evals.json` prompt with OpenClaw (skill installed) and eyeball results against the `expectations` strings, or use Cursor with the `personal-assistant` skill folder attached.

### Reproducible numeric score (local fixture + grader)

Because `openclaw` / `claude` CLIs are not required on the machine that runs CI, this repo includes a **fixture benchmark**: authored **with_skill** vs **without_skill** responses for each eval, graded by `tools/pa_skill_grader.py` (deterministic checks aligned to `evals.json` expectations), then aggregated with Anthropic’s `aggregate_benchmark.py`.

```bash
python tools/run_pa_benchmark_fixture.py
```

Latest committed summary: [`skills/personal-assistant/evals/results/benchmark.md`](skills/personal-assistant/evals/results/benchmark.md) and full JSON: [`skills/personal-assistant/evals/results/benchmark.json`](skills/personal-assistant/evals/results/benchmark.json).

**Latest run (fixture + heuristic grader):** with-skill **100%** mean pass rate vs baseline **44%** mean pass rate (**delta +0.56** on expectations). Replace fixtures with live model transcripts and swap in an LLM grader (`agents/grader.md`) when you run the full skill-creator loop in Claude Code.

Further ideas: [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator).

## Further reading

* [OpenClaw — Skills](https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md)
* [OpenClaw — Creating skills](https://github.com/openclaw/openclaw/blob/main/docs/tools/creating-skills.md)
* [ClawHub](https://clawhub.ai) for publishing and discovering skills
