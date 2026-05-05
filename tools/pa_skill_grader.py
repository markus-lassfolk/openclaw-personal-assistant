#!/usr/bin/env python3
"""
Deterministic grader for personal-assistant evals (no LLM).
Maps each (eval_id, expectation_index) to checks against response text.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def grade_expectation(eval_id: int, index: int, text: str, expectation: str) -> tuple[bool, str]:
    t = text.lower()
    exp = expectation.lower()

    if eval_id == 1:
        if index == 0:
            ok = bool(
                re.search(r"approval|approve", t)
                and re.search(r"draft|not send|without sending|will not send|do not send", t)
            )
            return ok, "Checked for approval language and draft/no-send wording."
        if index == 1:
            # Expectation: at most three distinct prioritized actions (prompt also asks for focused triage).
            action_line_indices: set[int] = set()
            for i, line in enumerate(text.splitlines()):
                if re.match(r"^\s*\d+\.\s+\S", line) or re.match(r"^\s*[-*]\s+\S", line):
                    action_line_indices.add(i)
            count = len(action_line_indices)
            ok = 1 <= count <= 3
            return ok, f"Distinct list-style action lines={count} (require 1-3, not an unfocused dump)."
        if index == 2:
            ok = any(w in t for w in ("inbox", "triage", "backlog", "pto", "catch-up", "catch up", "email"))
            return ok, "Checked for inbox/triage/backlog/PTO/email context."

    if eval_id == 2:
        if index == 0:
            ok = ("bob" in t and "alice" in t) or ("planner" in t and "sla" in t) or ("action" in t and "owner" in t)
            return ok, "Checked for owners/assignees or Planner/SLA references from transcript."
        if index == 1:
            bad_phrases = (
                "i've sent",
                "i have sent",
                "already sent the",
                "successfully sent",
                "sent the customer the",
                "emailed the customer the",
            )
            bad = any(p in t for p in bad_phrases)
            ok = not bad
            return ok, f"Checked for false sent-mail claims (triggered={bad})."
        if index == 2:
            ok = ("draft" in t or "awaiting" in t or "approval" in t) and (
                "customer" in t or "kickoff" in t or "deck" in t
            )
            return ok, "Checked draft/approval path tied to customer or kickoff/deck."

    if eval_id == 3:
        if index == 0:
            wc = word_count(text)
            ok = wc <= 250
            return ok, f"Word count={wc} (limit 250 per eval prompt)."
        if index == 1:
            ok = ("10:00" in text or "standup" in t) and ("14:00" in text or "vendor" in t)
            return ok, "Checked both meetings or times present."
        if index == 2:
            bullets = re.findall(r"(?m)^\s*[-*]\s+.+", text)
            inbox_section = False
            count_in_inbox = 0
            for line in text.splitlines():
                if "inbox" in line.lower() or "priority" in line.lower():
                    inbox_section = True
                elif inbox_section and re.match(r"^\s*#+\s", line):
                    break
                elif inbox_section and re.match(r"^\s*[-*]\s", line):
                    count_in_inbox += 1
            # Expectation: ≤3 inbox/task callouts in the inbox/priority-adjacent block (eval 3).
            ok = count_in_inbox <= 3
            return ok, f"Inbox-adjacent bullets={count_in_inbox}, total bullets={len(bullets)} (require <=3 in inbox/priority section)."

    return False, f"No grader rule for eval_id={eval_id} index={index}: {exp[:60]}..."


def grade_file(response_path: Path, evals_path: Path, eval_id: int) -> dict:
    text = response_path.read_text(encoding="utf-8")
    data = json.loads(evals_path.read_text(encoding="utf-8"))
    eval_entry = next(e for e in data["evals"] if e["id"] == eval_id)
    expectations = eval_entry.get("expectations", [])
    graded = []
    passed = 0
    for i, exp in enumerate(expectations):
        ok, evidence = grade_expectation(eval_id, i, text, exp)
        graded.append({"text": exp, "passed": ok, "evidence": evidence})
        if ok:
            passed += 1
    total = len(graded)
    failed = total - passed
    return {
        "expectations": graded,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
        "timing": {"total_duration_seconds": 0.0},
        "execution_metrics": {
            "total_tool_calls": 0,
            "errors_encountered": 0,
            "output_chars": len(text),
        },
    }


def main() -> None:
    if len(sys.argv) < 4:
        print(
            "Usage: pa_skill_grader.py <response.txt> <evals.json> <eval_id> [grading.json]",
            file=sys.stderr,
        )
        sys.exit(2)
    response_path = Path(sys.argv[1])
    evals_path = Path(sys.argv[2])
    eval_id = int(sys.argv[3])
    out = grade_file(response_path, evals_path, eval_id)
    if len(sys.argv) >= 5:
        Path(sys.argv[4]).write_text(json.dumps(out, indent=2), encoding="utf-8")
    else:
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
