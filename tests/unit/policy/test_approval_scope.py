import pytest

from harness.policy.approval_scope import ApprovalScope


def test_approval_scope_requires_tool_name():
    scope = ApprovalScope(tool_name="read")
    
    assert scope.tool_name == "read"


@pytest.mark.parametrize("tool_name", ["", "  "])
def test_approval_scope_rejects_empty_tool_name(tool_name):
    with pytest.raises(ValueError):
        ApprovalScope(tool_name=tool_name)