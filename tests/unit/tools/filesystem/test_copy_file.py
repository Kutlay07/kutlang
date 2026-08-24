import pytest

from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.copy_file import CopyFileTool


def test_copy_file_tool_metadata():
    tool = CopyFileTool()

    assert tool.name == "copy_file"
    assert tool.description == "Copy a file to a different path"


def test_copy_file_tool_implements_base_tool():
    tool = CopyFileTool()

    assert isinstance(tool, BaseTool)


def test_copy_file_tool_execute(tmp_path):
    source = tmp_path / "original.txt"
    destination = tmp_path / "copy.txt"

    source.write_text("Hello", encoding="utf-8")

    tool = CopyFileTool()

    result = tool.execute(
        source=str(source),
        destination=str(destination),
    )

    assert result == f"Successfully copied {source} to {destination}"
    assert source.read_text(encoding="utf-8") == "Hello"
    assert destination.read_text(encoding="utf-8") == "Hello"


def test_copy_file_tool_raises_for_missing_source(tmp_path):
    tool = CopyFileTool()

    with pytest.raises(FileNotFoundError):
        tool.execute(
            source=str(tmp_path / "missing.txt"),
            destination=str(tmp_path / "copy.txt"),
        )