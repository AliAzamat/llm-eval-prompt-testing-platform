"""LLM client abstraction. The interface (complete) is provider-agnostic so the
target model and the judge model can be different providers, swapped in one place.
Generation runs at temperature 0 for reproducibility across eval runs."""
from __future__ import annotations

import os
from typing import Protocol

from openai import OpenAI

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class LLM(Protocol):
    def complete(self, model: str, system: str, user: str, temperature: float) -> str: ...


class OpenAILLM:
    def complete(self, model: str, system: str, user: str, temperature: float = 0.0) -> str:
        resp = _client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return (resp.choices[0].message.content or "").strip()


llm: LLM = OpenAILLM()
