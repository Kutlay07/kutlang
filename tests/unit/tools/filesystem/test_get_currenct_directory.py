from pathlib import Path

from harness.tools.sync_base_tool import SyncBaseTool
from harness.tools.filesystem.get_current_directory import (
    GetCurrentDirectoryTool,
)


def test_get_current_directory_tool_metadata():
    tool = GetCurrentDirectoryTool()

    assert tool.name == "get_current_directory"
    assert tool.description == "Get the current working directory"


def test_get_current_directory_tool_implements_base_tool():
    tool = GetCurrentDirectoryTool()

    assert isinstance(tool, SyncBaseTool)


def test_get_current_directory_tool_execute():
    tool = GetCurrentDirectoryTool()

    assert tool.execute() == str(Path.cwd())