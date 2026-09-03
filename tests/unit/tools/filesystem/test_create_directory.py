import pytest

from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.create_directory import CreateDirectoryTool


def test_create_directory_tool_metadata(workspace_boundary):
    tool = CreateDirectoryTool(workspace_boundary)

    assert tool.name == "create_directory"
    assert tool.description == "Create a directory"


def test_create_directory_tool_implements_base_tool(workspace_boundary):
    tool = CreateDirectoryTool(workspace_boundary)

    assert isinstance(tool, BaseTool)


def test_create_directory_tool_execute(tmp_path, workspace_boundary):
    directory = tmp_path / "src" / "utils"

    tool = CreateDirectoryTool(workspace_boundary)

    result = tool.execute(path=str(directory))

    assert result == f"Successfully created directory {directory}"
    assert directory.is_dir()


def test_create_directory_tool_raises_if_directory_exists(tmp_path, workspace_boundary):
    directory = tmp_path / "src"
    directory.mkdir()

    tool = CreateDirectoryTool(workspace_boundary)

    with pytest.raises(FileExistsError):
        tool.execute(path=str(directory))