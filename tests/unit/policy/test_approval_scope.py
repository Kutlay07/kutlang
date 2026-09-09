from harness.policy.approval_scope import ApprovalScope


def test_approval_scope_has_expected_values():
    assert ApprovalScope.SINGLE_CALL == "single call"
    assert ApprovalScope.SESSION == "session"
    assert ApprovalScope.COMMAND_PATTERN == "command pattern"
    assert ApprovalScope.WORKSPACE == "workspace"