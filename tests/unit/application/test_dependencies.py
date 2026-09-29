from pathlib import Path

from pydantic import ValidationError
import pytest

from harness.application.dependencies import (
    get_context_assembler, 
    get_tool_registry,
    get_context_telemetry,
)
from harness.config.settings import Settings
from harness.context.budgeted_context_assembler import BudgetedContextAssembler
from harness.context.logging_context_telemetry import LoggingContextTelemetry


settings = Settings(
    local_llm_base_url="http://fake",
    local_llm_model="fake",
    max_iterations=10,
    workspace_root=Path("."),
)
def test_get_tool_registry_includes_glob():
    registry = get_tool_registry(settings)

    tool = registry.get("glob")

    assert tool.name == "glob"


def test_get_context_assembler_returns_budgeted_assembler_with_telemetry():
    assembler = get_context_assembler(
        settings,
        telemetry=get_context_telemetry(),
        )

    assert isinstance(assembler, BudgetedContextAssembler)
    assert isinstance(assembler.telemetry, LoggingContextTelemetry)


@pytest.mark.parametrize("invalid_budget", [0, -5])
def test_settings_rejects_non_positive_context_budget(invalid_budget):
    with pytest.raises(ValidationError):
        Settings(
            local_llm_base_url="http://fake",
            local_llm_model="fake",
            max_iterations=10,
            workspace_root=Path("."),
            max_context_tokens=invalid_budget,
        )