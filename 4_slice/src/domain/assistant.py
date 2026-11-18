from typing import Protocol
from .points import Point


class AssistantUnavailable(Exception):
    pass


class CitizenAssistant(Protocol):
    def answer(self, point: Point, question: str) -> str: ...


def safe_answer(point: Point, question: str, assistant: CitizenAssistant) -> str:
    """Domain stays independent from a particular LLM or SDK."""
    return assistant.answer(point, question)
