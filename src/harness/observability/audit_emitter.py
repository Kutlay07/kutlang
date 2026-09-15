from typing import Protocol

from harness.observability.audit_event import AuditEvent


class AuditEmitter(Protocol):
    
    def emit(self, event: AuditEvent) -> None:
        ...