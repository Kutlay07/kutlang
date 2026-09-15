from unittest.mock import Mock
import pytest

from harness.policy.approval_scope import ApprovalScope
from harness.policy.default_policy_engine import DefaultPolicyEngine
from harness.policy.policy_context import PolicyContext
from harness.policy.policy_decision import PolicyDecision
from harness.policy.risk_level import RiskLevel
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest
from harness.policy.trust_level import TrustLevel


class DummyRiskClassifier:
    def __init__(self, risk_level: RiskLevel):
        self.risk_level = risk_level

    def classify(self, request: ToolExecutionRequest) -> RiskLevel:
        return self.risk_level


@pytest.mark.parametrize(
    "trust_level",
    [
        TrustLevel.UNKNOWN,
        TrustLevel.UNTRUSTED,
    ],
)
def test_untrusted_tools_are_denied(trust_level):
    tool_execution_request = ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({}),
    )

    policy_context = PolicyContext(
        request=tool_execution_request,
        trust_level=trust_level
        )

    classifier = DummyRiskClassifier(RiskLevel.LOW)
    policy_engine = DefaultPolicyEngine(classifier)

    evaluation = policy_engine.evaluate(policy_context)
    
    assert evaluation.decision == PolicyDecision.DENY
    assert evaluation.risk_level is None
    assert evaluation.approval_scope is None


@pytest.mark.parametrize(
    "trust_level",
    [
        TrustLevel.UNKNOWN,
        TrustLevel.UNTRUSTED,
    ],
)
def test_risk_classifier_is_not_called_for_untrusted_or_unknown_tool(trust_level):
    tool_execution_request = ToolExecutionRequest(
        tool_name="external_tool",
        arguments=ToolArguments({}),
    )
        
    policy_context = PolicyContext(
        request=tool_execution_request,
        trust_level=trust_level,
        )
    
    classifier = Mock()
    policy_engine = DefaultPolicyEngine(classifier)
    
    evaluation = policy_engine.evaluate(policy_context)
    
    classifier.classify.assert_not_called()