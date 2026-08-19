from __future__ import annotations

import json

from app.judge.rubric import JUDGE_SYSTEM, judge_user
from app.judge.schema import Verdict, clamp
from app.llm.client import llm


def judge_output(judge_model: str, task: str, output: str,
                 reference: str | None, context: str | None) -> Verdict:
    """Score one candidate output. On unparseable judge output, fail soft to a
    zero verdict with a rationale — one bad judge call must not crash the run."""
    user = judge_user(task, output, reference, context)
    raw = llm.complete(model=judge_model, system=JUDGE_SYSTEM, user=user, temperature=0.0)
    try:
        data = json.loads(raw)
        return Verdict(
            accuracy=clamp(data["accuracy"]),
            grounding=clamp(data["grounding"]),
            format_ok=clamp(data["format_ok"]),
            rationale=str(data.get("rationale", ""))[:500],
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return Verdict(0.0, 0.0, 0.0, "judge returned unparseable output")
