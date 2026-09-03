from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.append_file import AppendFileTool


def test_append_file_tool_metadata(workspace_boundary):
    tool = AppendFileTool(workspace_boundary)

    assert tool.name == "append_file"
    assert tool.description == "Append content to the end of a file"


def test_append_file_tool_implements_base_tool(workspace_boundary):
    tool = AppendFileTool(workspace_boundary)

    assert isinstance(tool, BaseTool)


def test_append_file_tool_execute(tmp_path, workspace_boundary):
    file = tmp_path / "test.txt"
    file.write_text("Hello", encoding="utf-8")

    tool = AppendFileTool(workspace_boundary)

    result = tool.execute(
        path=str(file),
        content=" world",
    )

    assert result == f"Successfully appended content to {file}"
    assert file.read_text(encoding="utf-8") == "Hello world"


def test_append_file_tool_creates_missing_file(tmp_path, workspace_boundary):
    file = tmp_path / "new.txt"

    tool = AppendFileTool(workspace_boundary)

    tool.execute(
        path=str(file),
        content="Hello",
    )

    assert file.read_text(encoding="utf-8") == "Hello"