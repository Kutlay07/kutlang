import pytest

from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.read_file_range import (
    ReadFileRangeTool,
)


def test_read_file_range_tool_metadata(workspace_boundary):
    tool = ReadFileRangeTool(workspace_boundary)

    assert tool.name == "read_file_range"
    assert tool.description == (
        "Read a specific range of lines from a file"
    )


def test_read_file_range_tool_implements_base_tool(workspace_boundary):
    tool = ReadFileRangeTool(workspace_boundary)

    assert isinstance(tool, BaseTool)


def test_read_file_range_tool_execute(tmp_path,workspace_boundary):
    file = tmp_path / "test.py"

    file.write_text(
        "line 1\n"
        "line 2\n"
        "line 3\n"
        "line 4\n",
        encoding="utf-8",
    )

    tool = ReadFileRangeTool(workspace_boundary)

    result = tool.execute(
        path=str(file),
        start_line=2,
        end_line=3,
    )

    assert result == "line 2\nline 3"


def test_read_file_range_tool_raises_for_invalid_start_line(tmp_path,workspace_boundary):
    file = tmp_path / "test.py"
    file.write_text("line 1", encoding="utf-8")

    tool = ReadFileRangeTool(workspace_boundary)

    with pytest.raises(ValueError):
        tool.execute(
            path=str(file),
            start_line=0,
            end_line=1,
        )


def test_read_file_range_tool_raises_for_invalid_range(tmp_path,workspace_boundary):
    file = tmp_path / "test.py"
    file.write_text("line 1", encoding="utf-8")

    tool = ReadFileRangeTool(workspace_boundary)

    with pytest.raises(ValueError):
        tool.execute(
            path=str(file),
            start_line=3,
            end_line=1,
        )