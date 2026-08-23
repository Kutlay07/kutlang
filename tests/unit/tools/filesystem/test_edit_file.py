from coding_agent.tools.base_tool import BaseTool
from coding_agent.tools.filesystem.edit_file import EditFileTool


def test_edit_file_tool_metadata():
    tool = EditFileTool()

    assert tool.name == "edit_file"
    assert tool.description == "Replace text in a file"


def test_edit_file_tool_implements_base_tool():
    tool = EditFileTool()

    assert isinstance(tool, BaseTool)


def test_edit_file_tool_execute(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text(
        "Hello world",
        encoding="utf-8",
    )

    tool = EditFileTool()

    result = tool.execute(
        path=str(file),
        old_text="world",
        new_text="Python",
    )

    assert result == f"Successfully edited {file}"
    assert file.read_text(encoding="utf-8") == "Hello Python"


def test_edit_file_tool_raises_when_text_not_found(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text(
        "Hello world",
        encoding="utf-8",
    )

    tool = EditFileTool()

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