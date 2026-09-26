from typing import Protocol


class ContextSection(Protocol):
    kind: str
    content: str
    priority: int
    estimated_tokens: int