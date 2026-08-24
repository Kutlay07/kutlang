from dataclasses import dataclass


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    tool_name: str
    result: str
    is_error: bool = False