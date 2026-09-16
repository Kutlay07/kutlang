from dataclasses import dataclass

from harness.observability.audit_policy_decision import AuditPolicyDecision
from harness.observability.audit_policy_risk_level import AuditPolicyRiskLevel


@dataclass(frozen=True)
class PolicyAuditData:
    decision: AuditPolicyDecision
    risk_level: AuditPolicyRiskLevel | None