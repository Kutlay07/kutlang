from enum import Enum


class AuditApprovalScope(str, Enum):
    SINGLE_CALL = "single call"
    SESSION = "session"
    COMMAND_PATTERN = "command pattern"
    WORKSPACE = "workspace"