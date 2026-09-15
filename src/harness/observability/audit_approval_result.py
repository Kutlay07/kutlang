from enum import Enum


class AuditApprovalResult(str, Enum):
    GRANTED = "granted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELED = "canceled"