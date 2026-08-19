"""Render a prompt template against an item's inputs. We use explicit, named
placeholder substitution — NOT str.format — so a stray brace in the template or
a curly in the data can never trigger accidental formatting or a KeyError."""
from __future__ import annotations

import re

_PLACEHOLDER = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


class MissingPlaceholder(Exception):
    pass


def render(template: str, inputs: dict[str, str]) -> str:
    """Replace every {name} in the template with inputs[name]. A placeholder with
    no matching input is an error — a version must declare the inputs it needs."""
    missing: list[str] = []

    def sub(match: "re.Match[str]") -> str:
        name = match.group(1)
        if name not in inputs:
            missing.append(name)
            return match.group(0)
        return str(inputs[name])

    out = _PLACEHOLDER.sub(sub, template)
    if missing:
        raise MissingPlaceholder(f"template needs inputs not in the item: {sorted(set(missing))}")
    return out
