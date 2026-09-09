import pytest

from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_result import ApprovalResult
from harness.policy.approval_scope import ApprovalScope
from harness.policy.default_approval_handler import DefaultApprovalHandler
from harness.policy.risk_level import RiskLevel
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest


@pytest.mark.asyncio
async def test_handle_returns_rejected():
    approval_handler = DefaultApprovalHandler()
    
    tool_execution_request = ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({}),
    )
    
    request = ApprovalRequest(
        tool_execution_request=tool_execution_request,
        risk_level=RiskLevel.HIGH,
        scope=ApprovalScope.SINGLE_CALL
    )
    
    result = await approval_handler.handle(request)
    
    assert result == ApprovalResult.REJECTED