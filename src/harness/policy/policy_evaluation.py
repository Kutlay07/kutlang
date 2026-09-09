from dataclasses import dataclass

from harness.policy.approval_scope import ApprovalScope
from harness.policy.policy_decision import PolicyDecision
from harness.policy.risk_level import RiskLevel


@dataclass(frozen=True)
class PolicyEvaluation:
    decision: PolicyDecision
    risk_level: RiskLevel
    approval_scope: ApprovalScope | None = None
    
    def __post_init__(self):
        if self.decision == PolicyDecision.ASK and self.approval_scope is None:
            raise ValueError("approval_scope must be provided")
        
        if self.decision != PolicyDecision.ASK and self.approval_scope is not None:
            raise ValueError("approval_scope must be empty")