import pytest
from datetime import datetime

from dataclasses import is_dataclass, FrozenInstanceError

from harness.observability.audit_event import AuditEvent
from harness.observability.audit_event_type import AuditEventType
from harness.observability.audit_outcome import AuditOutcome
from harness.observability.audit_policy_decision import AuditPolicyDecision
from harness.observability.audit_policy_risk_level import AuditPolicyRiskLevel
from harness.observability.policy_audit_data import PolicyAuditData


@pytest.fixture
def policy_audit_data():
    return PolicyAuditData(
        decision=AuditPolicyDecision.ALLOW,
        risk_level=AuditPolicyRiskLevel.LOW,
    )

@pytest.fixture
def audit_event(policy_audit_data):
    return AuditEvent(
        event_type=AuditEventType.TOOL_COMPLETED,
        timestamp=datetime(2026, 12, 25, 14, 30, 0),
        tool_call_id="123",
        tool_name="run_command",
        outcome=AuditOutcome.SUCCESS,
        payload=policy_audit_data,
    )


def test_is_audit_event_dataclass():
    
    assert is_dataclass(AuditEvent) == True


def test_audit_event_is_immutable(audit_event):
    
    with pytest.raises(FrozenInstanceError):
        audit_event.event_type = "something"


def test_audit_event_has_expected_values(audit_event):
    
    assert audit_event.event_type == AuditEventType.TOOL_COMPLETED
    assert audit_event.timestamp == datetime(2026, 12, 25, 14, 30, 0)
    assert audit_event.tool_call_id == "123"
    assert audit_event.tool_name == "run_command"
    assert audit_event.outcome == AuditOutcome.SUCCESS