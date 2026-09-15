from enum import Enum


class AuditOutcome(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"
    APPROVED = "approved"
    PENDING = "pending"