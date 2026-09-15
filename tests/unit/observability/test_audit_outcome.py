from harness.observability.audit_outcome import AuditOutcome


def test_audit_outcome_has_expected_values():
    assert AuditOutcome.SUCCESS.value == "success"
    assert AuditOutcome.FAILURE.value == "failure"
    assert AuditOutcome.DENIED.value == "denied"
    assert AuditOutcome.APPROVED.value == "approved"
    assert AuditOutcome.PENDING.value == "pending"


def test_audit_outcome_is_string_compatible():
    assert AuditOutcome.SUCCESS == "success"
    assert AuditOutcome.FAILURE == "failure"
    assert AuditOutcome.DENIED == "denied"
    assert AuditOutcome.APPROVED == "approved"
    assert AuditOutcome.PENDING == "pending"