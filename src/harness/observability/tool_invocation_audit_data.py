from dataclasses import dataclass


@dataclass(frozen=True)
class ToolInvocationAuditData:
    arguments: dict