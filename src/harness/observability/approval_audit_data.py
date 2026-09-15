from dataclasses import dataclass
from typing import Generic, TypeVar


from harness.observability.audit_approval_scope import AuditApprovalScope
from harness.observability.audit_policy_risk_level import AuditPolicyRiskLevel


T = TypeVar("T")

@dataclass(frozen=True)
class ApprovalAuditData(Generic[T]):
    risk_level: AuditPolicyRiskLevel
    scope: AuditApprovalScope
    result: T