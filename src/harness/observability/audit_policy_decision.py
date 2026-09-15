from enum import Enum


class AuditPolicyDecision(str, Enum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"