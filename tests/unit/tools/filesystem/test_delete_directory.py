import pytest

from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.delete_directory import (
    DeleteDirectoryTool,
)


def test_delete_directory_tool_metadata(workspace_boundary):
    tool = DeleteDirectoryTool(workspace_boundary)

    assert tool.name == "delete_directory"
    assert tool.description == "Delete an empty directory"


def test_delete_directory_tool_implements_base_tool(workspace_boundary):
    tool = DeleteDirectoryTool(workspace_boundary)

    assert isinstance(tool, BaseTool)


def test_delete_directory_tool_execute(tmp_path, workspace_boundary):
    directory = tmp_path / "empty"
    directory.mkdir()

    tool = DeleteDirectoryTool(workspace_boundary)

    result = tool.execute(path=str(directory))

    assert result == f"Successfully deleted directory {directory}"
    assert not directory.exists()


def test_delete_directory_tool_raises_for_missing_directory(tmp_path, workspace_boundary):
    tool = DeleteDirectoryTool(workspace_boundary)

    with pytest.raises(FileNotFoundError):
        tool.execute(path=str(tmp_path / "missing"))


def test_delete_directory_tool_raises_for_non_empty_directory(tmp_path, workspace_boundary):
    directory = tmp_path / "non_empty"
    directory.mkdir()
    (directory / "file.txt").write_text("Hello", encoding="utf-8")

    tool = DeleteDirectoryTool(workspace_boundary)

    with pytest.raises(OSError):
        tool.execute(path=str(directory))