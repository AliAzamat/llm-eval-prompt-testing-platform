"""Pydantic contracts for the API. These types ARE the interface — the request
shape, the validation rules, and the response shape all live here, typed."""
from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterVersion(BaseModel):
    prompt_name: str = Field(..., min_length=1, max_length=120)
    task: str = Field(..., pattern="^(qa|summarize|extract|classify)$")
    template: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    notes: str | None = Field(None, max_length=500)


class VersionOut(BaseModel):
    id: str
    prompt_id: str
    version: int
    model: str
    notes: str | None = None


class RunRequest(BaseModel):
    prompt_version_id: str
    dataset_name: str
    judge_model: str = "gpt-4o"


class RunOut(BaseModel):
    run_id: str
    status: str
    n_items: int


class RunReport(BaseModel):
    run_id: str
    prompt_version_id: str
    version: int
    n_items: int
    accuracy: float
    grounding: float
    format_ok: float
    overall: float
