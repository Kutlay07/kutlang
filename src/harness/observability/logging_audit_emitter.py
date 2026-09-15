from dataclasses import asdict, is_dataclass
import logging

from harness.observability.audit_emitter import AuditEmitter
from harness.observability.audit_event import AuditEvent
from harness.observability.redaction.secret_redactor import SecretRedactor


class LoggingAuditEmitter(AuditEmitter):
    def __init__(
        self, 
        logger: logging.Logger,
        secret_redactor: SecretRedactor,
    ):
        self.logger = logger
        self.secret_redactor = secret_redactor


    def emit(
        self,
        event: AuditEvent,
    ) -> None:
        
        sanitized_payload = self._sanitize_payload(event.payload)
        
        extra = {
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "tool_call_id": event.tool_call_id,
            "tool_name": event.tool_name,
            "outcome": event.outcome,
            "payload": sanitized_payload,
        }
        
        adapter = logging.LoggerAdapter(self.logger, extra)
        adapter.info("Audit event emitted")


    def _sanitize_payload(self, payload):
        if payload is None:
            return None
        
        if is_dataclass(payload) and not isinstance(payload, type):
            payload = asdict(payload)
            
        if isinstance(payload, dict):
            return {
                key: self._sanitize_payload(value)
                for key, value in payload.items()
            }
            
        if isinstance(payload, list):
            return [
                self._sanitize_payload(item)
                for item in payload
            ]
            
        if isinstance(payload, tuple):
            return tuple(
                self._sanitize_payload(item)
                for item in payload
            )
            
        if isinstance(payload, str):
            return self.secret_redactor.redact(payload)
        
        return payload