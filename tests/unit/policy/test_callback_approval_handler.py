import pytest
from unittest.mock import AsyncMock

from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_result import ApprovalResult
from harness.policy.approval_scope import ApprovalScope
from harness.policy.callback_approval_handler import CallbackApprovalHandler
from harness.policy.risk_level import RiskLevel
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest


@pytest.mark.asyncio
async def test_handle_calls_the_callback_with_the_correct_approval_request():
    callback = AsyncMock()
    
    callback.return_value = ApprovalResult.GRANTED
    
    tool_arguments = ToolArguments({})
    
    tool_execution_request = ToolExecutionRequest(
        tool_name="read_file",
        arguments=tool_arguments,
    )
    
    request = ApprovalRequest(
        tool_execution_request=tool_execution_request,
        risk_level=RiskLevel.MEDIUM,
        scope=ApprovalScope.SINGLE_CALL,
    )
    
    handler = CallbackApprovalHandler(callback)
    
    result = await handler.handle(request)
    
    callback.assert_awaited_once_with(request)
    assert result == ApprovalResult.GRANTED