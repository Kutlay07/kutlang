import pytest

from coding_agent.tools.base_tool import BaseTool
from coding_agent.tools.filesystem.append_file import AppendFileTool


def test_append_file_tool_metadata():
    tool = AppendFileTool()

    assert tool.name == "append_file"
    assert tool.description == "Append content to the end of a file"


def test_append_file_tool_implements_base_tool():
    tool = AppendFileTool()

    assert isinstance(tool, BaseTool)


def test_append_file_tool_execute(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("Hello", encoding="utf-8")

    tool = AppendFileTool()

    result = tool.execute(
        path=str(file),
        content=" world",
    )

    assert result == f"Successfully appended content to {file}"
    assert file.read_text(encoding="utf-8") == "Hello world"


def test_append_file_tool_creates_missing_file(tmp_path):
    file = tmp_path / "new.txt"

    tool = AppendFileTool()

    tool.execute(
        path=str(file),
        content="Hello",
    )

    assert file.read_text(encoding="utf-8") == "Hello"