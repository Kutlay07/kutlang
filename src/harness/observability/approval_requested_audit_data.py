from dataclasses import dataclass

from harness.observability.audit_approval_scope import AuditApprovalScope
from harness.observability.audit_policy_risk_level import AuditPolicyRiskLevel


@dataclass(frozen=True)
class ApprovalRequestedAuditData:
    risk_level: AuditPolicyRiskLevel
    scope: AuditApprovalScope