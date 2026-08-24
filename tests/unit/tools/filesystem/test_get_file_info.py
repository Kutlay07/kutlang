import pytest

from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.get_file_info import (
    GetFileInfoTool,
)


def test_get_file_info_tool_metadata():
    tool = GetFileInfoTool()

    assert tool.name == "get_file_info"
    assert tool.description == (
        "Get basic information about a file or directory"
    )


def test_get_file_info_tool_implements_base_tool():
    tool = GetFileInfoTool()

    assert isinstance(tool, BaseTool)


def test_get_file_info_tool_returns_file_info(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("Hello", encoding="utf-8")

    tool = GetFileInfoTool()

    result = tool.execute(path=str(file))

    assert "type: file" in result
    assert "size: 5" in result


def test_get_file_info_tool_returns_directory_info(tmp_path):
    directory = tmp_path / "src"
    directory.mkdir()

    tool = GetFileInfoTool()

    result = tool.execute(path=str(directory))

    assert "type: directory" in result


def test_get_file_info_tool_raises_for_missing_path(tmp_path):
    tool = GetFileInfoTool()

    with pytest.raises(FileNotFoundError):
        tool.execute(
            path=str(tmp_path / "missing")
        )