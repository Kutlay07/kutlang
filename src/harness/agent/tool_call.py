from dataclasses import dataclass

@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: dict