from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from harness.observability.audit_policy_decision import AuditPolicyDecision
from harness.observability.audit_policy_risk_level import AuditPolicyRiskLevel
from harness.observability.policy_audit_data import PolicyAuditData


@pytest.fixture
def policy_audit_data():
    return PolicyAuditData(
        decision=AuditPolicyDecision.ALLOW,
        risk_level=AuditPolicyRiskLevel.LOW,
    )


def test_is_policy_audit_data_dataclass(policy_audit_data):
    
    assert is_dataclass(policy_audit_data)


def test_policy_audit_data_is_immutable(policy_audit_data):
    
    with pytest.raises(FrozenInstanceError):
        policy_audit_data.decision = AuditPolicyDecision.DENY


def test_policy_audit_data_has_expected_values(policy_audit_data):
    
    assert policy_audit_data.decision == AuditPolicyDecision.ALLOW
    assert policy_audit_data.risk_level == AuditPolicyRiskLevel.LOW