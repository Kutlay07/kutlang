from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.edit_file import EditFileTool


def test_edit_file_tool_metadata(workspace_boundary):
    tool = EditFileTool(workspace_boundary)

    assert tool.name == "edit_file"
    assert tool.description == "Replace text in a file"


def test_edit_file_tool_implements_base_tool(workspace_boundary):
    tool = EditFileTool(workspace_boundary)

    assert isinstance(tool, BaseTool)


def test_edit_file_tool_execute(tmp_path,workspace_boundary):
    file = tmp_path / "test.txt"
    file.write_text(
        "Hello world",
        encoding="utf-8",
    )

    tool = EditFileTool(workspace_boundary)

    result = tool.execute(
        path=str(file),
        old_text="world",
        new_text="Python",
    )

    assert result == f"Successfully edited {file}"
    assert file.read_text(encoding="utf-8") == "Hello Python"


def test_edit_file_tool_raises_when_text_not_found(tmp_path,workspace_boundary):
    file = tmp_path / "test.txt"
    file.write_text(
        "Hello world",
        encoding="utf-8",
    )

    tool = EditFileTool(workspace_boundary)

    try:
        tool.execute(
            path=str(file),
            old_text="missing",
            new_text="Python",
        )
    except ValueError as exc:
        assert str(exc) == "Text to replace was not found in the file"
    else:
        raise AssertionError("Expected ValueError")