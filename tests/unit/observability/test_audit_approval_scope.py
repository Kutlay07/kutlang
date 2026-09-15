from harness.observability.audit_approval_scope import AuditApprovalScope


def test_audit_approval_scope_has_expected_values():
    assert AuditApprovalScope.SINGLE_CALL.value == "single call"
    assert AuditApprovalScope.SESSION.value == "session"
    assert AuditApprovalScope.COMMAND_PATTERN.value == "command pattern"
    assert AuditApprovalScope.WORKSPACE.value == "workspace"


def test_audit_approval_scope_is_string_compatible():
    assert AuditApprovalScope.SINGLE_CALL == "single call"
    assert AuditApprovalScope.SESSION == "session"
    assert AuditApprovalScope.COMMAND_PATTERN == "command pattern"
    assert AuditApprovalScope.WORKSPACE == "workspace"