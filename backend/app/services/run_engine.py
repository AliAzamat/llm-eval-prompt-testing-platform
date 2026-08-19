from __future__ import annotations

from app.repositories.prompts import PromptRepo
from app.repositories.datasets import DatasetRepo
from app.repositories.runs import RunRepo
from app.generation.generate import generate_output
from app.judge.judge import judge_output

prompts = PromptRepo()
datasets = DatasetRepo()
runs = RunRepo()


def run_eval(prompt_version_id: str, dataset_id: str, task: str, judge_model: str) -> dict:
    """Evaluate one prompt version over one dataset: for each item, generate then
    judge, persisting every score under the run. One item's failure marks that item
    but never aborts the run."""
    version = prompts.get_version(prompt_version_id)
    if version is None:
        raise ValueError("prompt version not found")

    run_id = runs.create_run(prompt_version_id, dataset_id, judge_model)
    items = datasets.items(dataset_id)

    for item in items:
        try:
            output = generate_output(version.template, version.model, item["inputs"], item["context"])
            verdict = judge_output(judge_model, task, output, item["reference"], item["context"])
        except Exception as exc:  # generation error -> record a zero, keep going
            from app.judge.schema import Verdict
            output, verdict = "", Verdict(0.0, 0.0, 0.0, f"generation error: {exc}")
        runs.add_score(run_id, item["id"], output, verdict)

    runs.finish(run_id, "complete")
    report = runs.aggregate(run_id)
    return {"run_id": run_id, "n_items": report["n_items"] if report else 0, "report": report}
