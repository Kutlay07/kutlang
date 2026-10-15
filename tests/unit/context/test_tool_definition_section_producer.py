from unittest.mock import MagicMock

from harness.context.tool_definition_section_producer import ToolDefinitionSectionProducer
from harness.tools.sync_base_tool import SyncBaseTool


def test_tool_definition_section_producer_returns_none_for_no_tools():
    producer = ToolDefinitionSectionProducer()
    assert producer.produce([]) is None


def test_producer_includes_tool_metadata_and_estimates_large_definition():
    producer = ToolDefinitionSectionProducer()
    tool = MagicMock(spec=SyncBaseTool)
    tool.name = "read_file"
    tool.description = "x" * 1_000
    tool.parameters = {"type": "object", "properties": {}}

    section = producer.produce([tool])

    assert section is not None
    assert section.kind == "tool_definitions"
    assert "read_file" in section.content
    assert tool.description in section.content
    assert '"properties"' in section.content
    assert section.estimated_tokens > 10
