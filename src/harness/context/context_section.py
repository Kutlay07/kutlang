from dataclasses import dataclass
from typing import Protocol


class ContextSection(Protocol):
    kind: str
    content: str
    priority: int
    estimated_tokens: int


@dataclass(frozen=True)
class Section:
    kind: str
    content: str
    priority: int
    estimated_tokens: int