"""Rolling quality monitor for a prompt. Looks at the last N complete runs and
flags the latest one if it falls below an absolute floor OR drops sharply below
the moving average of the prior runs. This is the production early-warning."""
from __future__ import annotations

from dataclasses import dataclass

from app.db.postgres import cursor

QUALITY_FLOOR = 0.65      # absolute overall below this is a hard alert
DROP_THRESHOLD = 0.05     # latest below (prior-average - this) is a relative alert
WINDOW = 5                # how many recent runs form the moving baseline


@dataclass
class MonitorResult:
    prompt_name: str
    latest_overall: float | None
    baseline_overall: float | None
    flagged: bool
    reasons: list[str]


def _recent_run_overalls(prompt_name: str, limit: int) -> list[float]:
    """Overall score per recent complete run of a prompt, newest first."""
    with cursor() as cur:
        cur.execute(
            """
            SELECT AVG(s.overall) AS overall
            FROM eval_runs r
            JOIN prompt_versions pv ON pv.id = r.prompt_version_id
            JOIN prompts p ON p.id = pv.prompt_id
            JOIN eval_scores s ON s.run_id = r.id
            WHERE p.name = %s AND r.status = 'complete'
            GROUP BY r.id, r.created_at
            ORDER BY r.created_at DESC
            LIMIT %s
            """,
            (prompt_name, limit),
        )
        return [float(row["overall"]) for row in cur.fetchall() if row["overall"] is not None]


def check_prompt(prompt_name: str) -> MonitorResult:
    overalls = _recent_run_overalls(prompt_name, WINDOW + 1)
    if not overalls:
        return MonitorResult(prompt_name, None, None, False, ["no runs yet"])

    latest = overalls[0]
    prior = overalls[1:]
    baseline = round(sum(prior) / len(prior), 4) if prior else None

    reasons: list[str] = []
    if latest < QUALITY_FLOOR:
        reasons.append(f"below floor {QUALITY_FLOOR}: latest {round(latest, 4)}")
    if baseline is not None and latest < baseline - DROP_THRESHOLD:
        reasons.append(f"dropped {round(baseline - latest, 4)} below baseline {baseline}")

    return MonitorResult(prompt_name, round(latest, 4), baseline, bool(reasons), reasons or ["ok"])
