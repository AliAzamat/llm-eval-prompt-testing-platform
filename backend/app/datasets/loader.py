"""Load and validate a JSONL eval dataset before it touches the DB. A malformed
line is rejected loudly with its line number — bad ground truth poisons every
score computed against it, so we validate hard at import."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional


class DatasetError(Exception):
    def __init__(self, line_no: int, message: str) -> None:
        super().__init__(f"line {line_no}: {message}")
        self.line_no = line_no


@dataclass
class RawItem:
    item_key: str
    inputs: dict[str, Any]
    context: Optional[str]
    reference: Optional[str]


def load_jsonl(text: str) -> list[RawItem]:
    items: list[RawItem] = []
    seen: set[str] = set()
    for i, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DatasetError(i, f"invalid JSON: {exc.msg}")
        key = obj.get("item_key")
        if not key or not isinstance(key, str):
            raise DatasetError(i, "missing or non-string 'item_key'")
        if key in seen:
            raise DatasetError(i, f"duplicate item_key '{key}'")
        seen.add(key)
        if not isinstance(obj.get("inputs", {}), dict):
            raise DatasetError(i, "'inputs' must be an object")
        items.append(
            RawItem(
                item_key=key,
                inputs=obj.get("inputs", {}),
                context=obj.get("context"),
                reference=obj.get("reference"),
            )
        )
    if not items:
        raise DatasetError(0, "dataset is empty")
    return items
