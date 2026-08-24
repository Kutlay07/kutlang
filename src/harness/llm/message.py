from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    role: str
    content: str