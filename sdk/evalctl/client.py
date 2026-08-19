"""A thin Python SDK over the eval platform's HTTP API. Every method mirrors one
endpoint and raises on the standard error envelope, so the CLI (and any CI
script) composes the platform in plain Python."""
from __future__ import annotations

from typing import Any

import httpx


class EvalClient:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 120.0) -> None:
        self._http = httpx.Client(base_url=base_url, timeout=timeout)

    def _post(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        resp = self._http.post(path, json=json)
        body = resp.json()
        if resp.status_code >= 400:
            err = body.get("error", {})
            raise RuntimeError(f"{err.get('code', 'error')}: {err.get('message', resp.text)}")
        return body

    def register_version(self, prompt_name: str, task: str, template: str,
                         model: str, notes: str | None = None) -> dict[str, Any]:
        return self._post("/prompts/versions", {
            "prompt_name": prompt_name, "task": task, "template": template,
            "model": model, "notes": notes,
        })

    def import_dataset(self, name: str, task: str, jsonl_path: str) -> dict[str, Any]:
        with open(jsonl_path, "r", encoding="utf-8") as fh:
            jsonl = fh.read()
        return self._post("/datasets/import", {"name": name, "task": task, "jsonl": jsonl})

    def run(self, prompt_version_id: str, dataset_name: str, judge_model: str = "gpt-4o") -> dict[str, Any]:
        return self._post("/runs", {
            "prompt_version_id": prompt_version_id,
            "dataset_name": dataset_name, "judge_model": judge_model,
        })

    def diff(self, baseline_run_id: str, candidate_run_id: str) -> dict[str, Any]:
        return self._post("/diff", {
            "baseline_run_id": baseline_run_id, "candidate_run_id": candidate_run_id,
        })
