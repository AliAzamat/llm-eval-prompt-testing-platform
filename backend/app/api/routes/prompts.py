from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import RegisterVersion, VersionOut
from app.repositories.prompts import PromptRepo
from app.services.errors import error_response

router = APIRouter(prefix="/prompts", tags=["prompts"])
repo = PromptRepo()


@router.post("/versions", response_model=VersionOut)
def register_version(body: RegisterVersion):
    """Register an immutable prompt version. Pydantic has already validated the
    body against the contract before this function runs."""
    prompt_id = repo.ensure_prompt(body.prompt_name, body.task)
    v = repo.add_version(prompt_id, body.template, body.model, body.notes)
    return VersionOut(id=v.id, prompt_id=v.prompt_id, version=v.version, model=v.model, notes=v.notes)


@router.get("/versions/{version_id}", response_model=VersionOut)
def get_version(version_id: str):
    v = repo.get_version(version_id)
    if v is None:
        return error_response(404, "not_found", "prompt version not found")
    return VersionOut(id=v.id, prompt_id=v.prompt_id, version=v.version, model=v.model, notes=v.notes)
