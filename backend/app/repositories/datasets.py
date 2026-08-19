from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from app.db.postgres import cursor


class DatasetRepo:
    def ensure_dataset(self, name: str, task: str) -> str:
        dataset_id = str(uuid.uuid4())
        with cursor() as cur:
            cur.execute(
                """
                INSERT INTO datasets (id, name, task) VALUES (%s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """,
                (dataset_id, name, task),
            )
            row = cur.fetchone()
            if row is None:
                cur.execute("SELECT id FROM datasets WHERE name=%s", (name,))
                row = cur.fetchone()
        return row["id"]

    def upsert_item(self, dataset_id: str, item_key: str, inputs: dict[str, Any],
                    context: Optional[str], reference: Optional[str]) -> str:
        """Idempotent on (dataset_id, item_key): re-importing the same key overwrites
        it, so a dataset file is the source of truth and re-imports never duplicate."""
        item_id = str(uuid.uuid4())
        with cursor() as cur:
            cur.execute(
                """
                INSERT INTO dataset_items (id, dataset_id, item_key, inputs, context, reference)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (dataset_id, item_key)
                DO UPDATE SET inputs=EXCLUDED.inputs, context=EXCLUDED.context, reference=EXCLUDED.reference
                RETURNING id
                """,
                (item_id, dataset_id, item_key, json.dumps(inputs), context, reference),
            )
            return cur.fetchone()["id"]

    def items(self, dataset_id: str) -> list[dict[str, Any]]:
        with cursor() as cur:
            cur.execute(
                "SELECT id, item_key, inputs, context, reference FROM dataset_items "
                "WHERE dataset_id=%s ORDER BY item_key ASC",
                (dataset_id,),
            )
            return list(cur.fetchall())
