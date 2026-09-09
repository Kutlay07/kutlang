import pytest

from harness.policy.approval_scope import ApprovalScope
from harness.policy.default_policy_engine import DefaultPolicyEngine
from harness.policy.policy_context import PolicyContext
from harness.policy.policy_decision import PolicyDecision
from harness.policy.risk_level import RiskLevel
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest


class DummyRiskClassifier:
    def __init__(self, risk_level: RiskLevel):
        self.risk_level = risk_level
        
    def classify(self, request: ToolExecutionRequest) -> RiskLevel:
        return self.risk_level


@pytest.mark.parametrize(
    "risk_level, decision, approval_scope",
    [
        (RiskLevel.LOW, PolicyDecision.ALLOW, None),
        (RiskLevel.MEDIUM, PolicyDecision.ASK, ApprovalScope.SINGLE_CALL),
        (RiskLevel.HIGH, PolicyDecision.ASK, ApprovalScope.SINGLE_CALL),
        (RiskLevel.CRITICAL, PolicyDecision.DENY, None),
    ]
)
def test_default_policy_engine_all_situations(risk_level, decision, approval_scope):
    tool_execution_request = ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({}),
    )
    
    policy_context = PolicyContext(
        tool_execution_request
    )
    
    classifier = DummyRiskClassifier(risk_level)
    
    policy_engine = DefaultPolicyEngine(classifier)
    
    evaluation = policy_engine.evaluate(policy_context)
    
    
    assert evaluation.risk_level == risk_level
    assert evaluation.decision == decision
    assert evaluation.approval_scope == approval_scope