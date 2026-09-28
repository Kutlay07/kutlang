import json
import logging

from harness.context.logging_context_telemetry import LoggingContextTelemetry


def test_telemetry_records_event_as_json_line(caplog):
    logger = logging.getLogger("harness.context.test")
    telemetry = LoggingContextTelemetry(logger)
    
    with caplog.at_level(logging.INFO, logger="harness.context.test"):
        telemetry.record({"sections_in": 2, "tokens_kept": 500})
        
    assert len(caplog.records) == 1
    parsed = json.loads(caplog.records[0].message)
    assert parsed["sections_in"] == 2