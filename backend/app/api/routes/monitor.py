from __future__ import annotations

from fastapi import APIRouter

from app.services.monitor import check_prompt

router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.get("/{prompt_name}")
def monitor(prompt_name: str):
    r = check_prompt(prompt_name)
    return {
        "prompt_name": r.prompt_name,
        "latest_overall": r.latest_overall,
        "baseline_overall": r.baseline_overall,
        "flagged": r.flagged,
        "reasons": r.reasons,
    }
