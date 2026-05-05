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


def _eval1_action_item_count(text: str) -> tuple[int, str]:
    """
    Count distinct prioritized actions for eval 1: markdown list lines, (1)/(2) lines,
    line-leading First/Second/Third, or prose sentences starting with those words
    (capitalized, to avoid matching "the first ...").
    """
    indices: set[int] = set()
    for i, line in enumerate(text.splitlines()):
        if re.match(r"^\s*\d+\.\s+\S", line) or re.match(r"^\s*[-*]\s+\S", line):
            indices.add(i)
        if re.match(r"^\s*\([1-3]\)\s+\S", line):
            indices.add(i)
        if re.match(r"^\s*(?:\*\*)?(?:First|Second|Third)\b", line):
            indices.add(i)
    line_count = len(indices)
    prose_markers = len(
        re.findall(
            r"(?:^|[\n.!?]\s+)(?:\*\*)?(?:First|Second|Third)\b\s*[,:-]?",
            text,
            re.M,
        )
    )
    count = max(line_count, prose_markers)
    if count == 0:
        return 0, "no list lines or prose enumeration markers"
    if line_count > 0 and prose_markers > 0:
        detail = f"max(structured lines={line_count}, prose markers={prose_markers})"
    elif line_count > 0:
        detail = f"structured list/enumeration lines={line_count}"
    else:
        detail = f"prose First/Second/Third markers={prose_markers}"
    return count, detail


def _eval2_structure_carrier(line: str) -> bool:
    """Lines that can carry owned action items (not loose narrative paragraphs)."""
    s = line.strip()
    return bool(
        s.startswith("|")
        or re.match(r"^\s*[-*]\s+\S", line)
        or re.match(r"^\s*\d+\.\s+\S", line)
    )


def _eval2_owner_task_linkage(text: str) -> tuple[bool, str]:
    """
    Pass if at least one transcript owner is clearly tied to their work item (eval expectation:
    "at least one clear owner or assignee"). Table rows and list/table-like lines count; pure
    name-drops without task linkage do not.
    """
    rows = [ln for ln in text.splitlines() if "|" in ln and ln.strip().startswith("|")]
    sep = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")
    data_rows = [ln for ln in rows if not sep.match(ln) and "owner" not in ln.lower()]

    def row_links(line: str, owner: str, keywords: tuple[str, ...]) -> bool:
        low = line.lower()
        if owner not in low:
            return False
        return any(k in low for k in keywords)

    alice_row = any(row_links(r, "alice", ("contract", "revised")) for r in data_rows)
    bob_row = any(row_links(r, "bob", ("sla", "planner", "review")) for r in data_rows)
    if alice_row or bob_row:
        detail = (
            "Table rows link Alice to contract work and Bob to SLA/Planner."
            if (alice_row and bob_row)
            else "Table row links at least one transcript owner to their work item."
        )
        return True, detail

    alice_ok = bob_ok = False
    for ln in text.splitlines():
        if not _eval2_structure_carrier(ln):
            continue
        if re.search(r"(?i)alice.{0,100}(contract|revised)", ln) or re.search(
            r"(?i)(contract|revised).{0,100}alice", ln
        ):
            alice_ok = True
        if re.search(r"(?i)bob.{0,100}(sla|planner)", ln) or re.search(
            r"(?i)(sla|planner).{0,100}bob", ln
        ):
            bob_ok = True
    if alice_ok or bob_ok:
        return True, "Found at least one structured owner-task pairing from the transcript."
    return (
        False,
        f"No clear owner-item linkage (alice_row={alice_row}, bob_row={bob_row}, "
        f"alice_struct={alice_ok}, bob_struct={bob_ok}).",
    )


# Match negation in the text immediately before a claimed "sent" / emailed phrase (substring).
_SENT_CLAIM_NEGATION = re.compile(
    r"(?:"
    r"\b(?:not|never)\b|"
    r"\b(?:haven't|hasn't|hadn't|didn't|don't|doesn't|won't|can't|cannot)\b|"
    r"\b(?:have|has|had|do|does|did|will|would)\s+not\b|"
    r"\bi'?ve\s+not\b|"
    r"\bwithout\s+(?:sending|having\s+sent)\b|"
    r"\bno\s+(?:mail|email)\s+(?:has\s+been\s+)?(?:sent|transmitted)\b"
    r")"
)


def _eval2_unnegated_bad_sent_phrase(text: str, phrase: str) -> bool:
    """True if phrase appears at least once without a negation scoped to that occurrence."""
    t = text.lower()
    p = phrase.lower()
    start = 0
    while True:
        i = t.find(p, start)
        if i == -1:
            return False
        window = t[max(0, i - 72) : i]
        if not _SENT_CLAIM_NEGATION.search(window):
            return True
        start = i + len(p)


def _eval3_inbox_priority_bullets(
    text: str,
) -> tuple[bool, int, bool, int, list[int]]:
    """
    Sum bullets across every markdown section whose header mentions inbox/priority/overdue.
    Pass iff at least one such header exists and the combined bullet count is 1-3 (max-three
    inbox-priority callouts cannot be reset by starting a second matching section).

    Returns (ok, total_in_priority_sections, saw_priority_header, total_bullets_in_doc, per_section_counts).
    """
    section_counts: list[int] = []
    current: int | None = None
    saw_header = False
    for line in text.splitlines():
        if re.match(r"^\s*#{1,6}\s+", line):
            hdr = line.lower()
            if any(k in hdr for k in ("inbox", "priority", "overdue")):
                if current is not None:
                    section_counts.append(current)
                current = 0
                saw_header = True
            else:
                if current is not None:
                    section_counts.append(current)
                    current = None
        elif current is not None and (
            re.match(r"^\s*[-*]\s+\S", line) or re.match(r"^\s*\d+\.\s+\S", line)
        ):
            current += 1
    if current is not None:
        section_counts.append(current)
    total_in_priority = sum(section_counts)
    total_bullets = len(re.findall(r"(?m)^\s*[-*]\s+.+", text)) + len(
        re.findall(r"(?m)^\s*\d+\.\s+.+", text)
    )
    ok = bool(saw_header and 1 <= total_in_priority <= 3)
    return ok, total_in_priority, saw_header, total_bullets, section_counts


def _markdown_header_level(line: str) -> int | None:
    """Return ATX heading depth (1–6) or None if the line is not a markdown header."""
    m = re.match(r"^(\s*)(#{1,6})(?:\s+|$)", line)
    return len(m.group(2)) if m else None


def _eval3_today_section_meetings(text: str) -> tuple[bool, str]:
    """Meetings must appear inside a Today-style markdown section (header contains word 'Today')."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        level = _markdown_header_level(line)
        if level is None or not re.search(r"(?i)\btoday\b", line):
            continue
        section_level = level
        chunk: list[str] = []
        for j in range(i + 1, len(lines)):
            nxt = lines[j]
            nxt_level = _markdown_header_level(nxt)
            if nxt_level is not None and nxt_level <= section_level:
                break
            chunk.append(nxt)
        joined = "\n".join(chunk)
        low = joined.lower()
        has_a = "10:00" in joined or "standup" in low
        has_b = "14:00" in joined or "vendor" in low
        ok = has_a and has_b
        return ok, (
            f"Today block (nested subheadings ok if deeper than level {section_level}) "
            f"lines={len(chunk)}: 10:00/standup={has_a}, 14:00/vendor={has_b} "
            f"(require both under a header matching 'Today')."
        )
    return False, "No markdown header containing the word 'Today' was found."


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
            count, detail = _eval1_action_item_count(text)
            ok = 1 <= count <= 3
            return ok, f"Action items={count} ({detail}; require 1-3, not an unfocused dump)."
        if index == 2:
            ok = any(w in t for w in ("inbox", "triage", "backlog", "pto", "catch-up", "catch up", "email"))
            return ok, "Checked for inbox/triage/backlog/PTO/email context."

    if eval_id == 2:
        if index == 0:
            ok, msg = _eval2_owner_task_linkage(text)
            return ok, msg
        if index == 1:
            bad_phrases = (
                "i've sent",
                "i have sent",
                "already sent the",
                "successfully sent",
                "sent the customer the",
                "emailed the customer the",
            )
            bad = any(_eval2_unnegated_bad_sent_phrase(text, p) for p in bad_phrases)
            ok = not bad
            return ok, f"Checked for false sent-mail claims (unnegated_match={bad})."
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
            ok, msg = _eval3_today_section_meetings(text)
            return ok, msg
        if index == 2:
            ok, total_pri, saw_header, total_bullets, per_sec = _eval3_inbox_priority_bullets(text)
            return ok, (
                f"Inbox-priority header={saw_header}, bullets per matching section={per_sec}, "
                f"total in priority sections={total_pri}, all bullet lines in doc={total_bullets} "
                f"(require 1-3 bullets summed across all inbox/priority/overdue sections)."
            )

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
