import pytest

from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_result import ApprovalResult
from harness.policy.approval_scope import ApprovalScope
from harness.policy.risk_level import RiskLevel
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest


class DummyApprovalBroker:
    async def request_approval(
        self,
        approval_request: ApprovalRequest,
    ) -> ApprovalResult:
        return ApprovalResult.GRANTED

@pytest.mark.asyncio
async def test_approval_broker_returns_expected_value():
    broker = DummyApprovalBroker()

    tool_execution_request=ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({}),
        )
    
    approval_request = ApprovalRequest(
        tool_execution_request=tool_execution_request,
        risk_level=RiskLevel.HIGH,
        scope=ApprovalScope.SINGLE_CALL,
    )
    
    assert await broker.request_approval(approval_request) == ApprovalResult.GRANTED