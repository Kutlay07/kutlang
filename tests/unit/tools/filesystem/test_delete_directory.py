import pytest

from coding_agent.tools.base_tool import BaseTool
from coding_agent.tools.filesystem.delete_directory import (
    DeleteDirectoryTool,
)


def test_delete_directory_tool_metadata():
    tool = DeleteDirectoryTool()

    assert tool.name == "delete_directory"
    assert tool.description == "Delete an empty directory"


def test_delete_directory_tool_implements_base_tool():
    tool = DeleteDirectoryTool()

    assert isinstance(tool, BaseTool)


def test_delete_directory_tool_execute(tmp_path):
    directory = tmp_path / "empty"
    directory.mkdir()

    tool = DeleteDirectoryTool()

    result = tool.execute(path=str(directory))

    assert result == f"Successfully deleted directory {directory}"
    assert not directory.exists()


def test_delete_directory_tool_raises_for_missing_directory(tmp_path):
    tool = DeleteDirectoryTool()

    with pytest.raises(FileNotFoundError):
        tool.execute(path=str(tmp_path / "missing"))


def test_delete_directory_tool_raises_for_non_empty_directory(tmp_path):
    directory = tmp_path / "non_empty"
    directory.mkdir()
    (directory / "file.txt").write_text("Hello", encoding="utf-8")

    tool = DeleteDirectoryTool()

    with pytest.raises(OSError):
        tool.execute(path=str(directory))