import pytest

from harness.policy.approval_scope import ApprovalScope
from harness.policy.policy_decision import PolicyDecision
from harness.policy.policy_evaluation import PolicyEvaluation
from harness.policy.risk_level import RiskLevel


@pytest.mark.parametrize(
    "decision, approval_scope, should_raise, expected_error",
    [
        (PolicyDecision.ALLOW, None, False, None),
        (PolicyDecision.DENY, None, False, None),
        (PolicyDecision.ASK, ApprovalScope.SINGLE_CALL, False, None),
        
        (PolicyDecision.ASK, None, True, "approval_scope must be provided"),
        (PolicyDecision.ALLOW, ApprovalScope.SINGLE_CALL, True, "approval_scope must be empty"),
        (PolicyDecision.DENY, ApprovalScope.SINGLE_CALL, True, "approval_scope must be empty"),
    ],
)
def test_policy_evaluation_all_situations(decision, approval_scope, should_raise, expected_error):
    if should_raise:
        with pytest.raises(ValueError, match=expected_error):
            PolicyEvaluation(
                decision=decision,
                risk_level=RiskLevel.HIGH,
                approval_scope=approval_scope,
            )
    else:
        evaluation=PolicyEvaluation(
            decision=decision,
            risk_level=RiskLevel.HIGH,
            approval_scope=approval_scope,
        )
        
        assert evaluation.decision == decision
        assert evaluation.approval_scope == approval_scope