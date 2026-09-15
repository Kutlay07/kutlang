from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from harness.observability.audit_event_type import AuditEventType
from harness.observability.audit_outcome import AuditOutcome

T = TypeVar("T")

@dataclass(frozen=True)
class AuditEvent(Generic[T]):
    event_type: AuditEventType
    timestamp: datetime
    tool_call_id: str
    tool_name: str
    outcome: AuditOutcome
    payload: T | None = None