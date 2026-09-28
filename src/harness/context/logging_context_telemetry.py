import json
import logging

from harness.context.context_telemetry import ContextTelemetry


class LoggingContextTelemetry(ContextTelemetry):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def record(self, event: dict) -> None:
        self.logger.info(json.dumps(event))