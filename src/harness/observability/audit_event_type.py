from enum import Enum


class AuditEventType(str, Enum):
    POLICY_EVALUATED = "policy evaluated"
    APPROVAL_REQUESTED = "approval requested"
    APPROVAL_COMPLETED = "approval completed"
    TOOL_INVOKED = "tool invoked"
    TOOL_COMPLETED = "tool completed"
    TOOL_FAILED = "tool failed"