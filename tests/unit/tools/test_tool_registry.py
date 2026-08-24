from unittest.mock import MagicMock

import pytest

from harness.tools.base_tool import BaseTool
from harness.tools.tool_registry import ToolRegistry
from harness.tools.execution.run_command import RunCommandTool


def test_registry_stores_tools_by_name():
    tool = MagicMock(spec=BaseTool)
    type(tool).name = property(lambda _: "read_file")

    registry = ToolRegistry([tool])

    assert registry.get("read_file") is tool


def test_registry_supports_multiple_tools():
    read_file = MagicMock(spec=BaseTool)
    type(read_file).name = property(lambda _: "read_file")

    write_file = MagicMock(spec=BaseTool)
    type(write_file).name = property(lambda _: "write_file")

    registry = ToolRegistry([read_file, write_file])

    assert registry.get("read_file") is read_file
    assert registry.get("write_file") is write_file


def test_registry_raises_for_unknown_tool():
    registry = ToolRegistry([])

    with pytest.raises(KeyError):
        registry.get("unknown_tool")


def test_registry_exposes_registered_tools():
    tool = MagicMock(spec=BaseTool)
    tool.name = "read_file"

    registry = ToolRegistry([tool])

    assert registry.tools == [tool]


def test_registry_registers_run_command_tool():
    tool = RunCommandTool()
    registry = ToolRegistry([tool])

    assert registry.get("run_command") is tool
    assert tool in registry.tools