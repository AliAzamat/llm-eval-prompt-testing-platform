from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from typing import Optional

from app.db.postgres import cursor


@dataclass
class PromptVersion:
    id: str
    prompt_id: str
    version: int
    template: str
    content_hash: str
    model: str
    notes: Optional[str] = None


def template_hash(template: str) -> str:
    return hashlib.sha256(template.encode("utf-8")).hexdigest()


class PromptRepo:
    def ensure_prompt(self, name: str, task: str) -> str:
        """Return the prompt id for a name, creating the stable prompt row once."""
        prompt_id = str(uuid.uuid4())
        with cursor() as cur:
            cur.execute(
                """
                INSERT INTO prompts (id, name, task) VALUES (%s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """,
                (prompt_id, name, task),
            )
            row = cur.fetchone()
            if row is None:
                cur.execute("SELECT id FROM prompts WHERE name=%s", (name,))
                row = cur.fetchone()
        return row["id"]

    def add_version(self, prompt_id: str, template: str, model: str,
                    notes: Optional[str] = None) -> PromptVersion:
        """Append an IMMUTABLE version. Re-registering identical text returns the
        existing version (content_hash conflict) instead of minting a new number."""
        chash = template_hash(template)
        with cursor() as cur:
            # Next version number is max(version)+1 for this prompt, computed in-txn.
            cur.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 AS next FROM prompt_versions WHERE prompt_id=%s",
                (prompt_id,),
            )
            next_version = cur.fetchone()["next"]
            cur.execute(
                """
                INSERT INTO prompt_versions (id, prompt_id, version, template, content_hash, model, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (prompt_id, content_hash) DO NOTHING
                RETURNING *
                """,
                (str(uuid.uuid4()), prompt_id, next_version, template, chash, model, notes),
            )
            row = cur.fetchone()
            if row is None:  # identical body already registered -> return it
                cur.execute(
                    "SELECT * FROM prompt_versions WHERE prompt_id=%s AND content_hash=%s",
                    (prompt_id, chash),
                )
                row = cur.fetchone()
        return PromptVersion(**{k: row[k] for k in PromptVersion.__annotations__})

    def get_version(self, prompt_version_id: str) -> Optional[PromptVersion]:
        with cursor() as cur:
            cur.execute("SELECT * FROM prompt_versions WHERE id=%s", (prompt_version_id,))
            row = cur.fetchone()
        return PromptVersion(**{k: row[k] for k in PromptVersion.__annotations__}) if row else None
