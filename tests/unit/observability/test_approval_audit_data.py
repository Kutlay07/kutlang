from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from harness.observability.approval_audit_data import ApprovalAuditData
from harness.observability.audit_approval_result import AuditApprovalResult
from harness.observability.audit_approval_scope import AuditApprovalScope
from harness.observability.audit_policy_risk_level import AuditPolicyRiskLevel


@pytest.fixture
def approval_audit_data():
    return ApprovalAuditData(
        risk_level=AuditPolicyRiskLevel.LOW,
        scope=AuditApprovalScope.SINGLE_CALL,
        result=AuditApprovalResult.GRANTED,
    )


def test_is_approval_audit_data_dataclass(approval_audit_data):
    
    assert is_dataclass(approval_audit_data)


def test_approval_audit_data_is_immutable(approval_audit_data):
    
    with pytest.raises(FrozenInstanceError):
        approval_audit_data.risk_level = AuditPolicyRiskLevel.MEDIUM


def test_approval_audit_data_has_expected_values(approval_audit_data):
    
    assert approval_audit_data.risk_level == AuditPolicyRiskLevel.LOW
    assert approval_audit_data.scope == AuditApprovalScope.SINGLE_CALL
    assert approval_audit_data.result == AuditApprovalResult.GRANTED