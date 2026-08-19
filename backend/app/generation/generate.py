from __future__ import annotations

from app.generation.render import render
from app.llm.client import llm

GEN_SYSTEM = (
    "You are the feature under test. Follow the instructions in the user message "
    "exactly and return only the requested output, with no preamble."
)


def generate_output(template: str, model: str, inputs: dict[str, str], context: str | None) -> str:
    """Render the version's template with the item inputs, append grounding context
    if present, and generate at temperature 0 so the same version+item is stable."""
    user = render(template, {k: str(v) for k, v in inputs.items()})
    if context:
        user = f"{user}\n\nGrounding context:\n{context}"
    return llm.complete(model=model, system=GEN_SYSTEM, user=user, temperature=0.0)
