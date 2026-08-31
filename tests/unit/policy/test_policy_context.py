import pytest
from dataclasses import FrozenInstanceError

from harness.policy.policy_context import PolicyContext
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest


def test_policycontext_correctly_passes_the_request():
    request = ToolExecutionRequest(
        tool_name="tool_name",
        arguments = ToolArguments(arguments={})
    )
    
    context = PolicyContext(request=request)
    
    assert request is context.request


def test_policycontext_is_frozen():
    request = ToolExecutionRequest(
        tool_name="tool_name",
        arguments = ToolArguments(arguments={})
    )
    
    context = PolicyContext(request=request)
    
    another_request = ToolExecutionRequest(
        tool_name="tool_name2",
        arguments = ToolArguments(arguments={})
    )
    
    with pytest.raises(FrozenInstanceError):
        context.request = another_request