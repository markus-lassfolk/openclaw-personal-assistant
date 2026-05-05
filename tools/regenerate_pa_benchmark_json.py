"""Rebuild skills/personal-assistant/evals/results/benchmark.json from eval-workspace fixtures."""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EV = REPO / "skills/personal-assistant/evals/evals.json"
GR = REPO / "tools/pa_skill_grader.py"
ITER = REPO / "eval-workspace/iteration-1"
OUT = REPO / "skills/personal-assistant/evals/results/benchmark.json"
OUT_MD = REPO / "skills/personal-assistant/evals/results/benchmark.md"
# Rough GPT-style token estimate when replaying fixtures (no model tokenizer available).
_CHARS_PER_TOKEN_EST = 4.0


def mean_std(xs: list[float]) -> dict:
    if not xs:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": round(statistics.mean(xs), 4),
        "stddev": round(statistics.pstdev(xs), 4) if len(xs) > 1 else 0.0,
        "min": round(min(xs), 4),
        "max": round(max(xs), 4),
    }


def _fmt_pct(mean: float, stddev: float) -> str:
    return f"{int(round(mean * 100))}% +/- {int(round(stddev * 100))}%"


def _write_benchmark_md(bench: dict) -> None:
    rs = bench["run_summary"]
    ws_pr, wo_pr = rs["with_skill"]["pass_rate"], rs["without_skill"]["pass_rate"]
    ws_tok, wo_tok = rs["with_skill"]["tokens"], rs["without_skill"]["tokens"]
    ws_time, wo_time = rs["with_skill"]["time_seconds"], rs["without_skill"]["time_seconds"]
    delta = rs["delta"]
    meta = bench["metadata"]
    evals = ", ".join(str(x) for x in meta["evals_run"]) if meta.get("evals_run") else "(none)"
    body = f"""# Skill Benchmark: personal-assistant

**Model**: {meta.get("executor_model", "<model-name>")}
**Date**: {meta.get("timestamp", "")}
**Evals**: {evals} (1 fixture run per eval per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | {_fmt_pct(ws_pr["mean"], ws_pr["stddev"])} | {_fmt_pct(wo_pr["mean"], wo_pr["stddev"])} | {delta["pass_rate"]} |
| Time | {ws_time["mean"]}s +/- {ws_time["stddev"]}s | {wo_time["mean"]}s +/- {wo_time["stddev"]}s | {delta["time_seconds"]} |
| Tokens (est.) | {int(round(ws_tok["mean"]))} +/- {int(round(ws_tok["stddev"]))} | {int(round(wo_tok["mean"]))} +/- {int(round(wo_tok["stddev"]))} | {delta["tokens"]} |

*Fixture replay: token figures are `round(output_chars/4)`, not real tokenizer counts; see `benchmark.json` `metadata.tokens_note` and per-run `output_chars`.*
"""
    OUT_MD.write_text(body, encoding="utf-8")


def main() -> None:
    runs: list[dict] = []
    for eid in (1, 2, 3):
        for cfg in ("with_skill", "without_skill"):
            p = ITER / f"eval-{eid}" / cfg / "run-0" / "outputs" / "response.txt"
            if not p.exists():
                continue
            tmp = Path(tempfile.mkdtemp()) / "grading.json"
            subprocess.run(
                [sys.executable, str(GR), str(p), str(EV), str(eid), str(tmp)],
                check=True,
            )
            data = json.loads(tmp.read_text(encoding="utf-8"))
            exps = data["expectations"]
            passed = sum(1 for x in exps if x["passed"])
            total = len(exps)
            body = p.read_text(encoding="utf-8")
            out_chars = len(body)
            tok_est = max(1, int(round(out_chars / _CHARS_PER_TOKEN_EST)))
            runs.append(
                {
                    "eval_id": eid,
                    "configuration": cfg,
                    "run_number": 0,
                    "result": {
                        "pass_rate": round(passed / total, 4) if total else 0.0,
                        "passed": passed,
                        "failed": total - passed,
                        "total": total,
                        "time_seconds": 0.0,
                        "tokens": tok_est,
                        "output_chars": out_chars,
                        "tool_calls": 0,
                        "errors": 0,
                    },
                    "expectations": [
                        {"text": x["text"], "passed": x["passed"], "evidence": x["evidence"]} for x in exps
                    ],
                    "notes": [],
                }
            )

    ws_pr = [r["result"]["pass_rate"] for r in runs if r["configuration"] == "with_skill"]
    wo_pr = [r["result"]["pass_rate"] for r in runs if r["configuration"] == "without_skill"]
    ws_tok = [r["result"]["tokens"] for r in runs if r["configuration"] == "with_skill"]
    wo_tok = [r["result"]["tokens"] for r in runs if r["configuration"] == "without_skill"]
    m_ws = mean_std(ws_pr)["mean"]
    m_wo = mean_std(wo_pr)["mean"]
    evals_run = sorted({r["eval_id"] for r in runs})
    bench = {
        "metadata": {
            "skill_name": "personal-assistant",
            "skill_path": "<path/to/skill>",
            "executor_model": "<model-name>",
            "analyzer_model": "<model-name>",
            "timestamp": "2026-05-05T12:58:52Z",
            "evals_run": evals_run,
            "runs_per_configuration": 1,
            "fixture_replay": True,
            "tokens_note": (
                f"Fixture replay only: `tokens` is max(1, round(output_chars/{int(_CHARS_PER_TOKEN_EST)})); "
                "not tokenizer output. See `output_chars` per run."
            ),
        },
        "runs": runs,
        "run_summary": {
            "with_skill": {
                "pass_rate": mean_std(ws_pr),
                "time_seconds": mean_std(
                    [r["result"]["time_seconds"] for r in runs if r["configuration"] == "with_skill"]
                ),
                "tokens": mean_std(ws_tok),
            },
            "without_skill": {
                "pass_rate": mean_std(wo_pr),
                "time_seconds": mean_std(
                    [r["result"]["time_seconds"] for r in runs if r["configuration"] == "without_skill"]
                ),
                "tokens": mean_std(wo_tok),
            },
            "delta": {
                "pass_rate": f"{m_ws - m_wo:+.2f}",
                "time_seconds": "+0.0",
                "tokens": f"{int(mean_std(ws_tok)['mean'] - mean_std(wo_tok)['mean']):+d}",
            },
        },
        "notes": [],
    }
    OUT.write_text(json.dumps(bench, indent=2), encoding="utf-8")
    _write_benchmark_md(bench)
    print("Wrote", OUT)
    print("Wrote", OUT_MD)


if __name__ == "__main__":
    main()
