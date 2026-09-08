from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_scope import ApprovalScope
from harness.policy.default_risk_classifier import DefaultRiskClassifier
from harness.policy.risk_level import RiskLevel
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest


def test_approval_request_has_expected_values():
    classifier = DefaultRiskClassifier()
    
    tool_execution_request=ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({}),
        )
    request = ApprovalRequest(
        tool_execution_request=tool_execution_request,
        risk_level=RiskLevel.HIGH,
        scope=ApprovalScope.SINGLE_CALL,
    )
    
    assert request.tool_execution_request == tool_execution_request
    assert request.risk_level == RiskLevel.HIGH
    assert request.scope == ApprovalScope.SINGLE_CALL