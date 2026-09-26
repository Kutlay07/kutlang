from pathlib import Path

from harness.application.dependencies import get_context_assembler, get_tool_registry
from harness.config.settings import Settings
from harness.context.priority_order_assembler import PriorityOrderAssembler


def test_get_tool_registry_includes_glob():
    settings = Settings(
        local_llm_base_url="http://fake",
        local_llm_model="fake",
        max_iterations=10,
        workspace_root=Path("."),
    )

    registry = get_tool_registry(settings)

    tool = registry.get("glob")

    assert tool.name == "glob"


def test_get_context_assembler_returns_priority_order_assembler():
    assembler = get_context_assembler()
    
    assert isinstance(assembler, PriorityOrderAssembler)