from enum import Enum


class ApprovalScope(str, Enum):
    SINGLE_CALL = "single call"
    SESSION = "session"
    COMMAND_PATTERN = "command pattern"
    WORKSPACE = "workspace"