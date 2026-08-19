LLM Feature Eval & Prompt-Testing Platform

An advanced, end-to-end eval-platform capstone. You model the domain in Postgres — immutable prompt versions, eval datasets, and per-run judge scores — behind a typed FastAPI service with Pydantic contracts. You build an eval-input dataset, an LLM-as-a-judge harness that scores each generation against an accuracy/grounding/format rubric, a run engine that persists every score keyed to a prompt version, a regression differ that compares two versions before a change ships, a monitoring view that flags a quality drop below threshold, and a one-command CLI/SDK an ML engineer runs to evaluate a prompt. The whole thing mirrors the internal tooling an Adobe AI-platform team uses so a feature ships on evidence, not vibes.

## Stack
- Python
- FastAPI
- Pydantic
- PostgreSQL
- LLM-as-a-judge
