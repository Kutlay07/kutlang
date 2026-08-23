from pathlib import Path

from coding_agent.tools.base_tool import BaseTool
from coding_agent.tools.filesystem.get_current_directory import (
    GetCurrentDirectoryTool,
)


def test_get_current_directory_tool_metadata():
    tool = GetCurrentDirectoryTool()

    assert tool.name == "get_current_directory"
    assert tool.description == "Get the current working directory"


def test_get_current_directory_tool_implements_base_tool():
    tool = GetCurrentDirectoryTool()

    assert isinstance(tool, BaseTool)


def test_get_current_directory_tool_execute():
    tool = GetCurrentDirectoryTool()

    assert tool.execute() == str(Path.cwd())