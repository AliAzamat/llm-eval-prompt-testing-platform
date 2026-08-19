from __future__ import annotations

import uuid
from typing import Any, Optional

from app.db.postgres import cursor
from app.judge.schema import Verdict


class RunRepo:
    def create_run(self, prompt_version_id: str, dataset_id: str, judge_model: str) -> str:
        run_id = str(uuid.uuid4())
        with cursor() as cur:
            cur.execute(
                """
                INSERT INTO eval_runs (id, prompt_version_id, dataset_id, judge_model, status)
                VALUES (%s, %s, %s, %s, 'running')
                """,
                (run_id, prompt_version_id, dataset_id, judge_model),
            )
        return run_id

    def add_score(self, run_id: str, item_id: str, output: str, v: Verdict) -> None:
        with cursor() as cur:
            cur.execute(
                """
                INSERT INTO eval_scores
                  (id, run_id, item_id, output, accuracy, grounding, format_ok, overall, rationale)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (run_id, item_id) DO NOTHING
                """,
                (str(uuid.uuid4()), run_id, item_id, output,
                 v.accuracy, v.grounding, v.format_ok, v.overall, v.rationale),
            )

    def finish(self, run_id: str, status: str) -> None:
        with cursor() as cur:
            cur.execute("UPDATE eval_runs SET status=%s WHERE id=%s", (status, run_id))

    def aggregate(self, run_id: str) -> Optional[dict[str, Any]]:
        """Average each axis across the run's scored items into one report row."""
        with cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS n_items,
                       AVG(accuracy)  AS accuracy,
                       AVG(grounding) AS grounding,
                       AVG(format_ok) AS format_ok,
                       AVG(overall)   AS overall
                FROM eval_scores WHERE run_id=%s
                """,
                (run_id,),
            )
            row = cur.fetchone()
        return row if row and row["n_items"] else None
