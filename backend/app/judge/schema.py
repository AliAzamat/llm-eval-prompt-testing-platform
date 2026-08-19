"""The judge's scored verdict. Weights turn three axes into one composite the
platform ranks versions by — accuracy dominates, grounding guards hallucination,
format is a smaller gate."""
from __future__ import annotations

from dataclasses import dataclass

WEIGHTS = {"accuracy": 0.5, "grounding": 0.3, "format_ok": 0.2}


@dataclass
class Verdict:
    accuracy: float
    grounding: float
    format_ok: float
    rationale: str

    @property
    def overall(self) -> float:
        return round(
            self.accuracy * WEIGHTS["accuracy"]
            + self.grounding * WEIGHTS["grounding"]
            + self.format_ok * WEIGHTS["format_ok"],
            4,
        )


def clamp(x: float) -> float:
    """Judges occasionally return 1.2 or -0.1; keep every axis inside [0, 1]."""
    return max(0.0, min(1.0, float(x)))
