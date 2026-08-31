from dataclasses import dataclass
from .tool_arguments import ToolArguments


@dataclass(frozen=True)
class ToolExecutionRequest:
    tool_name: str
    arguments: ToolArguments
    
    def __post_init__(self) -> None:
        if not self.tool_name.strip():
            raise ValueError("tool_name must not be empty")