from harness.policy.approval_scope import ApprovalScope
from harness.policy.policy_context import PolicyContext
from harness.policy.policy_decision import PolicyDecision
from harness.policy.policy_engine import PolicyEngine
from harness.policy.policy_evaluation import PolicyEvaluation
from harness.policy.risk_classifier import RiskClassifier
from harness.policy.risk_level import RiskLevel
from harness.policy.trust_level import TrustLevel


class DefaultPolicyEngine(PolicyEngine):

    def __init__(self, risk_classifier: RiskClassifier):
        self.risk_classifier = risk_classifier


    def evaluate(self, policy_context: PolicyContext) -> PolicyEvaluation:
        if policy_context.trust_level in (
            TrustLevel.UNKNOWN, 
            TrustLevel.UNTRUSTED):
            return PolicyEvaluation(
                decision=PolicyDecision.DENY,
                risk_level=None,
                approval_scope=None,
            )
            
        risk_level = self.risk_classifier.classify(
            policy_context.request
        )
        
        decision = self._decide(risk_level)
        
        approval_scope = self._scope(decision)
        
        return PolicyEvaluation(
            decision=decision,
            risk_level=risk_level,
            approval_scope=approval_scope,
        )


    def _decide(self, risk_level: RiskLevel) -> PolicyDecision:
        if risk_level == RiskLevel.LOW:
            return PolicyDecision.ALLOW
        elif risk_level == RiskLevel.MEDIUM:
            return PolicyDecision.ASK
        elif risk_level == RiskLevel.HIGH:
            return PolicyDecision.ASK
        elif risk_level == RiskLevel.CRITICAL:
            return PolicyDecision.DENY


    def _scope(self, decision: PolicyDecision) -> ApprovalScope | None:
        if decision == PolicyDecision.ALLOW:
            return None
        elif decision == PolicyDecision.ASK:
            return ApprovalScope.SINGLE_CALL
        elif decision == PolicyDecision.DENY:
            return None