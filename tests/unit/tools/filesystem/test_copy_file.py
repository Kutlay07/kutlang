import pytest

from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.copy_file import CopyFileTool


def test_copy_file_tool_metadata(workspace_boundary):
    tool = CopyFileTool(workspace_boundary)

    assert tool.name == "copy_file"
    assert tool.description == "Copy a file to a different path"


def test_copy_file_tool_implements_base_tool(workspace_boundary):
    tool = CopyFileTool(workspace_boundary)

    assert isinstance(tool, BaseTool)


def test_copy_file_tool_execute(tmp_path, workspace_boundary):
    source = tmp_path / "original.txt"
    destination = tmp_path / "copy.txt"

    source.write_text("Hello", encoding="utf-8")

    tool = CopyFileTool(workspace_boundary)

    result = tool.execute(
        source=str(source),
        destination=str(destination),
    )

    assert result == f"Successfully copied {source} to {destination}"
    assert source.read_text(encoding="utf-8") == "Hello"
    assert destination.read_text(encoding="utf-8") == "Hello"


def test_copy_file_tool_raises_for_missing_source(tmp_path, workspace_boundary):
    tool = CopyFileTool(workspace_boundary)

    with pytest.raises(FileNotFoundError):
        tool.execute(
            source=str(tmp_path / "missing.txt"),
            destination=str(tmp_path / "copy.txt"),
        )