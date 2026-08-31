from harness.policy.policy_context import PolicyContext
from harness.policy.policy_decision import PolicyDecision
from harness.policy.policy_engine import PolicyEngine
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest


class FakePolicyEngine:
    def evaluate(
        self,
        policy_context: PolicyContext,
    ) -> PolicyDecision:
        return PolicyDecision.ALLOW


def test_policy_engine_evaluates_context():
    request = ToolExecutionRequest(
        tool_name="tool_name",
        arguments=ToolArguments(arguments={}),
    )
    context = PolicyContext(request=request)

    engine: PolicyEngine = FakePolicyEngine()

    result = engine.evaluate(context)

    assert result is PolicyDecision.ALLOW