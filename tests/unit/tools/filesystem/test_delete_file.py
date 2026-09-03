import pytest

from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.delete_file import DeleteFileTool


def test_delete_file_tool_metadata(workspace_boundary):
    tool = DeleteFileTool(workspace_boundary)

    assert tool.name == "delete_file"
    assert tool.description == "Delete a file"


def test_delete_file_tool_implements_base_tool(workspace_boundary):
    tool = DeleteFileTool(workspace_boundary)

    assert isinstance(tool, BaseTool)


def test_delete_file_tool_execute(tmp_path, workspace_boundary):
    file = tmp_path / "test.txt"
    file.write_text("Hello", encoding="utf-8")

    tool = DeleteFileTool(workspace_boundary)

    result = tool.execute(path=str(file))

    assert result == f"Successfully deleted {file}"
    assert not file.exists()


def test_delete_file_tool_raises_for_missing_file(tmp_path, workspace_boundary):
    tool = DeleteFileTool(workspace_boundary)

    with pytest.raises(FileNotFoundError):
        tool.execute(path=str(tmp_path / "missing.txt"))