from dataclasses import dataclass


@dataclass(frozen=True)
class ApprovalScope:
    tool_name: str
    
    def __post_init__(self) -> None:
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise ValueError("tool_name must not be empty")