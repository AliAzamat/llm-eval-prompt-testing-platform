"""The judge prompt. It scores an output on three axes against the reference and
context, returns ONLY JSON, and is told to be strict — a lenient judge makes
every prompt look good and hides the regressions the platform exists to catch."""

JUDGE_SYSTEM = """You are a strict evaluation judge for an LLM feature.
Score the CANDIDATE output on three axes, each from 0.0 to 1.0:
- accuracy: does the candidate match the REFERENCE answer's meaning? If no reference
  is given, score how well it satisfies the stated task.
- grounding: is every claim supported by the CONTEXT? If no context is given, score 1.0.
- format: does the candidate obey the format the task demands (length, structure, no preamble)?
Be strict. A plausible-but-wrong answer scores low on accuracy. An answer that adds
facts not in the context scores low on grounding.
Return ONLY valid JSON:
{"accuracy": float, "grounding": float, "format_ok": float, "rationale": "one sentence"}"""


def judge_user(task: str, output: str, reference: str | None, context: str | None) -> str:
    parts = [f"TASK: {task}"]
    if context:
        parts.append(f"CONTEXT:\n{context}")
    if reference is not None:
        parts.append(f"REFERENCE:\n{reference or '(expected empty output)'}")
    parts.append(f"CANDIDATE:\n{output or '(empty)'}")
    return "\n\n".join(parts)
