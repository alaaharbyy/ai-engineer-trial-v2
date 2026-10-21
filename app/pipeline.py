"""Tasks 1 and 2: answer a question with retrieval, generation and tool calls.

Model settings come from environment variables (see .env.example). How you
talk to the model is up to you, but tool calls must go through the model's
native function-calling interface.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.search import Chunk


@dataclass
class ToolCall:
    name: str
    arguments: dict
    result: dict


@dataclass
class Answer:
    text: str
    cited_chunk_ids: list[str] = field(default_factory=list)
    retrieved: list[Chunk] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    grounded: bool | None = None
    grounding_reasons: list[str] = field(default_factory=list)
    model: str = ""


def check_grounding(answer_text: str, cited_chunk_ids: list[str], chunks: list[Chunk]) -> tuple[bool, list[str]]:
    """Return (passed, reasons).

    Must fail when:
      - a cited chunk id is not among the retrieved chunks, or
      - a key claim (number, date, name) is not found in the chunks it cites.
    """
    raise NotImplementedError


def answer(question: str, user_id: str) -> Answer:
    """Answer the question for this user.

    - Retrieve with app.search.search(question, user_id).
    - Give the model the DSCR tool (app.tools) through its function-calling API.
    - If the model requests a tool call, run it in code and send the result back.
    - Return the final text, the chunk ids it cites, what was retrieved, every
      tool call made, and the grounding result.
    """
    raise NotImplementedError
