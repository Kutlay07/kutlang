from pathlib import Path
from unittest.mock import MagicMock

from pydantic import ValidationError
import pytest

from harness.application.dependencies import (
    get_context_assembler,
    build_context_assembler, 
    get_tool_registry,
    get_context_telemetry,
    get_agent_runtime,
    READ_FILE_OUTPUT_BUDGET_CHARS
)
from harness.config.settings import Settings
from harness.context.budgeted_context_assembler import BudgetedContextAssembler
from harness.context.logging_context_telemetry import LoggingContextTelemetry
from harness.context.section_producer import ConversationSectionProducer
from harness.llm.local import LocalLLM
from harness.observability.audit_emitter import AuditEmitter
from harness.policy.approval_broker import ApprovalBroker
from harness.policy.policy_engine import PolicyEngine


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


def test_get_agent_runtime_wires_all_dependencies():
    llm = MagicMock(spec=LocalLLM)
    registry = get_tool_registry(settings)
    policy_engine = MagicMock(spec=PolicyEngine)
    approval_broker = MagicMock(spec=ApprovalBroker)
    audit_emitter = MagicMock(spec=AuditEmitter)
    assembler = build_context_assembler(settings)
    conversation_section_producer = MagicMock(spec=ConversationSectionProducer)

    runtime = get_agent_runtime(
        llm=llm,
        registry=registry,
        policy_engine=policy_engine,
        approval_broker=approval_broker,
        audit_emitter=audit_emitter,
        context_assembler=assembler,
        conversation_section_producer=conversation_section_producer,
        settings=settings,
    )

    assert runtime.llm is llm
    assert runtime.tools is registry
    assert runtime.policy_engine is policy_engine
    assert runtime.approval_broker is approval_broker
    assert runtime.audit_emitter is audit_emitter
    assert runtime.context_assembler is assembler
    assert runtime.max_iterations == settings.max_iterations


def test_build_context_assembler_direct_call_gets_concrete_telemetry():
    assembler = build_context_assembler(settings)

    assert isinstance(assembler.telemetry, LoggingContextTelemetry)


def test_get_tool_registry_configures_read_file_output_budget():
    registry = get_tool_registry(settings)
    read_file_tool = registry.get("read_file")

    assert read_file_tool.output_budget.max_chars == READ_FILE_OUTPUT_BUDGET_CHARS