import pytest

from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest


@pytest.mark.parametrize("tool_name", ["", "  "])
def test_tool_execution_request_rejects_empty_tool_name(tool_name):
    with pytest.raises(ValueError):
        ToolExecutionRequest(
            arguments=ToolArguments(arguments={}), 
            tool_name=tool_name
            )