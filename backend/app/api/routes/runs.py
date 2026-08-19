from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import RunRequest, RunOut
from app.repositories.prompts import PromptRepo
from app.repositories.datasets import DatasetRepo
from app.services import run_engine
from app.services.errors import error_response
from app.db.postgres import cursor

router = APIRouter(prefix="/runs", tags=["runs"])
prompts = PromptRepo()


def _dataset_for(name: str):
    with cursor() as cur:
        cur.execute("SELECT id, task FROM datasets WHERE name=%s", (name,))
        return cur.fetchone()


@router.post("", response_model=RunOut)
def start_run(body: RunRequest):
    version = prompts.get_version(body.prompt_version_id)
    if version is None:
        return error_response(404, "not_found", "prompt version not found")
    ds = _dataset_for(body.dataset_name)
    if ds is None:
        return error_response(404, "not_found", "dataset not found")

    result = run_engine.run_eval(body.prompt_version_id, ds["id"], ds["task"], body.judge_model)
    return RunOut(run_id=result["run_id"], status="complete", n_items=result["n_items"])
