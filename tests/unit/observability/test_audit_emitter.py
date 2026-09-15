import pytest
from datetime import datetime

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

class FakeAuditEmitter:
    def __init__(self):
        self.events = []
        
    def emit(self, event: AuditEvent) -> None:
        self.events.append(event)


def test_audit_emitter_(audit_event):
    fake = FakeAuditEmitter()
    
    fake.emit(audit_event)
    
    assert audit_event in fake.events