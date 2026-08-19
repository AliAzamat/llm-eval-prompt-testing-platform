from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.diff_engine import diff_runs

router = APIRouter(prefix="/diff", tags=["diff"])


class DiffRequest(BaseModel):
    baseline_run_id: str
    candidate_run_id: str


@router.post("")
def diff(body: DiffRequest):
    return diff_runs(body.baseline_run_id, body.candidate_run_id)
