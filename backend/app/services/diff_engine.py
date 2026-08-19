"""Compare two eval runs of the SAME dataset. Produces axis-level deltas, the
per-item movers, and a ship verdict: does the candidate regress the baseline
beyond a tolerance on the composite score?"""
from __future__ import annotations

from dataclasses import dataclass

from app.db.postgres import cursor

REGRESSION_TOLERANCE = 0.02  # candidate may dip at most this much below baseline overall


@dataclass
class ItemDelta:
    item_key: str
    baseline_overall: float
    candidate_overall: float
    delta: float


def _run_scores(run_id: str) -> dict[str, dict]:
    """item_key -> {overall, accuracy, grounding, format_ok} for a run's scores."""
    with cursor() as cur:
        cur.execute(
            """
            SELECT di.item_key, s.overall, s.accuracy, s.grounding, s.format_ok
            FROM eval_scores s JOIN dataset_items di ON di.id = s.item_id
            WHERE s.run_id = %s
            """,
            (run_id,),
        )
        return {r["item_key"]: r for r in cur.fetchall()}


def _avg(run_id: str) -> dict:
    with cursor() as cur:
        cur.execute(
            "SELECT AVG(accuracy) a, AVG(grounding) g, AVG(format_ok) f, AVG(overall) o "
            "FROM eval_scores WHERE run_id=%s",
            (run_id,),
        )
        return cur.fetchone()


def diff_runs(baseline_run: str, candidate_run: str) -> dict:
    base, cand = _run_scores(baseline_run), _run_scores(candidate_run)
    shared = sorted(set(base) & set(cand))

    movers: list[ItemDelta] = []
    for key in shared:
        d = round(cand[key]["overall"] - base[key]["overall"], 4)
        movers.append(ItemDelta(key, base[key]["overall"], cand[key]["overall"], d))
    # Biggest drops first — the items a reviewer must look at before shipping.
    movers.sort(key=lambda m: m.delta)

    ba, ca = _avg(baseline_run), _avg(candidate_run)
    overall_delta = round((ca["o"] or 0) - (ba["o"] or 0), 4)
    regressed = overall_delta < -REGRESSION_TOLERANCE

    return {
        "overall_delta": overall_delta,
        "accuracy_delta": round((ca["a"] or 0) - (ba["a"] or 0), 4),
        "grounding_delta": round((ca["g"] or 0) - (ba["g"] or 0), 4),
        "format_delta": round((ca["f"] or 0) - (ba["f"] or 0), 4),
        "verdict": "regressed" if regressed else "pass",
        "worst_items": [m.__dict__ for m in movers[:5]],
    }
