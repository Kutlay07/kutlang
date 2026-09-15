from harness.observability.audit_event_type import AuditEventType


def test_audit_event_type_has_expected_values():
    assert AuditEventType.POLICY_EVALUATED.value == "policy evaluated"
    assert AuditEventType.APPROVAL_REQUESTED.value == "approval requested"
    assert AuditEventType.APPROVAL_COMPLETED.value == "approval completed"
    assert AuditEventType.TOOL_INVOKED.value == "tool invoked"
    assert AuditEventType.TOOL_COMPLETED.value == "tool completed"
    assert AuditEventType.TOOL_FAILED.value == "tool failed"


def test_audit_event_type_is_string_compatible():
    assert AuditEventType.POLICY_EVALUATED == "policy evaluated"
    assert AuditEventType.APPROVAL_REQUESTED == "approval requested"
    assert AuditEventType.APPROVAL_COMPLETED == "approval completed"
    assert AuditEventType.TOOL_INVOKED == "tool invoked"
    assert AuditEventType.TOOL_COMPLETED == "tool completed"
    assert AuditEventType.TOOL_FAILED == "tool failed"