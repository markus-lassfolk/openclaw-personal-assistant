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


def mean_std(xs: list[float]) -> dict:
    if not xs:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": round(statistics.mean(xs), 4),
        "stddev": round(statistics.pstdev(xs), 4) if len(xs) > 1 else 0.0,
        "min": round(min(xs), 4),
        "max": round(max(xs), 4),
    }


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
            tok = len(p.read_text(encoding="utf-8"))
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
                        "tokens": tok,
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
    bench = {
        "metadata": {
            "skill_name": "personal-assistant",
            "skill_path": "<path/to/skill>",
            "executor_model": "<model-name>",
            "analyzer_model": "<model-name>",
            "timestamp": "2026-05-05T12:58:52Z",
            "evals_run": [1, 2, 3],
            "runs_per_configuration": 1,
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
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
