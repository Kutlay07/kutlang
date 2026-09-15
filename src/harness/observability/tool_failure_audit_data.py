from dataclasses import dataclass


@dataclass(frozen=True)
class ToolFailureAuditData:
    arguments: dict
    error: str