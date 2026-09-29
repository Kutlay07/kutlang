from typing import Protocol


class ContextTelemetry(Protocol):
    def record(self, event: dict) -> None:
        ...