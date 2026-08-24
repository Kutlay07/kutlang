from dataclasses import dataclass

from .tool_call import ToolCall


@dataclass(frozen=True)
class AgentResponse:
    text: str | None = None
    tool_calls: list[ToolCall] | None = None