from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.datasets.loader import load_jsonl, DatasetError
from app.repositories.datasets import DatasetRepo
from app.services.errors import error_response

router = APIRouter(prefix="/datasets", tags=["datasets"])
repo = DatasetRepo()


class ImportDataset(BaseModel):
    name: str
    task: str
    jsonl: str  # raw file contents


@router.post("/import")
def import_dataset(body: ImportDataset):
    try:
        raw_items = load_jsonl(body.jsonl)
    except DatasetError as exc:
        return error_response(400, "dataset_invalid", str(exc), {"line": exc.line_no})

    dataset_id = repo.ensure_dataset(body.name, body.task)
    for it in raw_items:
        repo.upsert_item(dataset_id, it.item_key, it.inputs, it.context, it.reference)
    return {"dataset_id": dataset_id, "n_items": len(raw_items)}
