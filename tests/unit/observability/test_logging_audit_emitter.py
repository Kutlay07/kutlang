import logging
from datetime import datetime
from unittest.mock import ANY, Mock 

import pytest

from harness.observability.audit_event import AuditEvent
from harness.observability.audit_event_type import AuditEventType
from harness.observability.audit_outcome import AuditOutcome
from harness.observability.audit_policy_decision import AuditPolicyDecision
from harness.observability.audit_policy_risk_level import AuditPolicyRiskLevel
from harness.observability.redaction.default_entropy_detector import DefaultEntropyDetector
from harness.observability.logging_audit_emitter import LoggingAuditEmitter
from harness.observability.policy_audit_data import PolicyAuditData
from harness.observability.redaction.default_secret_redactor import DefaultSecretRedactor


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


def test_when_emit_is_called_the_audit_event_data_is_passed_to_logger(
    audit_event,
    ):
    
    secret_redactor = Mock()
    secret_redactor.redact.side_effect = lambda value: value
    
    logger = Mock()
    
    emitter = LoggingAuditEmitter(logger, secret_redactor)
    
    emitter.emit(audit_event)
    
    logger.log.assert_called_once_with(
        logging.INFO,
        ANY,
        extra={
            "event_type": audit_event.event_type,
            "timestamp": audit_event.timestamp,
            "tool_call_id": audit_event.tool_call_id,
            "tool_name": audit_event.tool_name,
            "outcome": audit_event.outcome,
            "payload": {
                "decision": AuditPolicyDecision.ALLOW,
                "risk_level": AuditPolicyRiskLevel.LOW,
            },
        },
    )


def test_when_payload_is_none_none_is_passed_to_logger():
    secret_redactor = Mock()
    logger = Mock()

    audit_event = AuditEvent(
        event_type=AuditEventType.TOOL_INVOKED,
        timestamp=datetime(2026, 12, 25, 14, 30, 0),
        tool_call_id="123",
        tool_name="run_command",
        outcome=AuditOutcome.PENDING,
        payload=None,
    )

    emitter = LoggingAuditEmitter(logger, secret_redactor)

    emitter.emit(audit_event)

    logger.log.assert_called_once_with(
        logging.INFO,
        ANY,
        extra={
            "event_type": audit_event.event_type,
            "timestamp": audit_event.timestamp,
            "tool_call_id": audit_event.tool_call_id,
            "tool_name": audit_event.tool_name,
            "outcome": audit_event.outcome,
            "payload": None,
        },
    )


def test_when_payload_contains_secret_it_is_redacted_before_logging():
    
    secret_redactor = Mock()
    secret_redactor.redact.side_effect = (
        lambda value: value.replace("SECRET", "[REDACTED]")
    )
    
    logger = Mock()
    
    audit_event = AuditEvent(
        event_type=AuditEventType.TOOL_COMPLETED,
        timestamp=datetime(2026, 12, 25, 14, 30, 0),
        tool_call_id="123",
        tool_name="run_command",
        outcome=AuditOutcome.SUCCESS,
        payload={
            "message": "hello SECRET world",
        },
    )
    
    emitter = LoggingAuditEmitter(logger, secret_redactor)
    
    emitter.emit(audit_event)
    
    logger.log.assert_called_once_with(
        logging.INFO,
        ANY,
        extra={
            "event_type": audit_event.event_type,
            "timestamp": audit_event.timestamp,
            "tool_call_id": audit_event.tool_call_id,
            "tool_name": audit_event.tool_name,
            "outcome": audit_event.outcome,
            "payload": {
                "message": "hello [REDACTED] world",
            },
        },
    )


def test_when_payload_is_nested_all_strings_are_redacted():
    
    secret_redactor = Mock()
    secret_redactor.redact.side_effect = (
        lambda value: value.replace("SECRET", "[REDACTED]")
    )
    
    logger = Mock()
    
    audit_event = AuditEvent(
        event_type=AuditEventType.TOOL_COMPLETED,
        timestamp=datetime(2026, 12, 25, 14, 30, 0),
        tool_call_id="123",
        tool_name="run_command",
        outcome=AuditOutcome.SUCCESS,
        payload={
            "command": "SECRET",
            "items": [
                "normal",
                "SECRET",
            ],
            "metadata": {
                "value": "SECRET",
            },
        }
    )
    
    emitter = LoggingAuditEmitter(logger, secret_redactor)
    
    emitter.emit(audit_event)
    
    logger.log.assert_called_once_with(
        logging.INFO,
        ANY,
        extra={
            "event_type": audit_event.event_type,
            "timestamp": audit_event.timestamp,
            "tool_call_id": audit_event.tool_call_id,
            "tool_name": audit_event.tool_name,
            "outcome": audit_event.outcome,
            "payload": {
                "command": "[REDACTED]",
                "items": [
                    "normal",
                    "[REDACTED]",
                ],
                "metadata": {
                    "value": "[REDACTED]",
                },
            }
        },
    )


def test_when_redaction_fails_raw_payload_is_not_logged():
    
    secret_redactor = Mock()
    secret_redactor.redact.side_effect = RuntimeError("redaction failed")
    
    logger = Mock()
    
    audit_event = AuditEvent(
        event_type=AuditEventType.TOOL_COMPLETED,
        timestamp=datetime(2026, 12, 25, 14, 30, 0),
        tool_call_id="123",
        tool_name="run_command",
        outcome=AuditOutcome.SUCCESS,
        payload={
            "output": "SUPER_SECRET_VALUE_123",
            },
        )
    
    emitter = LoggingAuditEmitter(logger, secret_redactor)
    
    with pytest.raises(RuntimeError, match="redaction failed"):
        emitter.emit(audit_event)
    
    logger.log.assert_not_called()


def test_book():
    secret_redactor = DefaultSecretRedactor(DefaultEntropyDetector())
    
    logger = Mock()
    
    audit_event = AuditEvent(
        event_type=AuditEventType.TOOL_COMPLETED,
        timestamp=datetime(2026, 12, 25, 14, 30, 0),
        tool_call_id="123",
        tool_name="run_command",
        outcome=AuditOutcome.SUCCESS,
        payload={
            "output": "API_KEY=super_secret_value",
        },
    )
    
    emitter = LoggingAuditEmitter(logger, secret_redactor)
    
    emitter.emit(audit_event)
    
    logger.log.assert_called_once_with(
        logging.INFO,
        ANY,
        extra={
            "event_type": audit_event.event_type,
            "timestamp": audit_event.timestamp,
            "tool_call_id": audit_event.tool_call_id,
            "tool_name": audit_event.tool_name,
            "outcome": audit_event.outcome,
            "payload": {
                "output": "API_KEY=[REDACTED.API_KEY]",
            },
        },
    )