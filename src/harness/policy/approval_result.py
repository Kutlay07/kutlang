from enum import Enum


class ApprovalResult(str, Enum):
    GRANTED = "granted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELED = "canceled"