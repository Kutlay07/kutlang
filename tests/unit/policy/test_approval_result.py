from harness.policy.approval_result import ApprovalResult


def test_approval_scope_has_expected_values():
    assert ApprovalResult.GRANTED == "granted"
    assert ApprovalResult.REJECTED == "rejected"
    assert ApprovalResult.EXPIRED == "expired"
    assert ApprovalResult.CANCELED == "canceled"