from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.file_exists import FileExistsTool


def test_file_exists_tool_metadata(workspace_boundary):
    tool = FileExistsTool(workspace_boundary)

    assert tool.name == "file_exists"
    assert tool.description == "Check whether a file exists"


def test_file_exists_tool_implements_base_tool(workspace_boundary):
    tool = FileExistsTool(workspace_boundary)

    assert isinstance(tool, BaseTool)


def test_file_exists_tool_returns_true_for_existing_file(tmp_path,workspace_boundary):
    file = tmp_path / "test.txt"
    file.write_text("Hello", encoding="utf-8")

    tool = FileExistsTool(workspace_boundary)

    assert tool.execute(path=str(file)) == "true"


def test_file_exists_tool_returns_false_for_missing_file(tmp_path,workspace_boundary):
    tool = FileExistsTool(workspace_boundary)

    assert tool.execute(
        path=str(tmp_path / "missing.txt")
    ) == "false"


def test_file_exists_tool_returns_false_for_directory(tmp_path,workspace_boundary):
    directory = tmp_path / "src"
    directory.mkdir()

    tool = FileExistsTool(workspace_boundary)

    assert tool.execute(path=str(directory)) == "false"