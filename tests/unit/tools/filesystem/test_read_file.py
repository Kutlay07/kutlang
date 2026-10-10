import pytest

from harness.tools.output_budget import OutputBudget
from harness.tools.sync_base_tool import SyncBaseTool
from harness.tools.filesystem.read_file import ReadFileTool


def test_read_file_tool_metadata(workspace_boundary, output_budget):
    tool = ReadFileTool(workspace_boundary, output_budget)

    assert tool.name == "read_file"
    assert tool.description == "Read the contents of a file, optionally starting at a specific line and limiting the number of lines returned"


def test_read_file_tool_implements_base_tool(workspace_boundary, output_budget):
    tool = ReadFileTool(workspace_boundary, output_budget)

    assert isinstance(tool, SyncBaseTool)


def test_read_file_tool_execute(tmp_path, workspace_boundary, output_budget):
    file = tmp_path / "test.txt"
    file.write_text("Hello world", encoding="utf-8")

    tool = ReadFileTool(workspace_boundary, output_budget)

    result = tool.execute(path=str(file))

    assert result == "Hello world"


def test_read_file_tool_parameters(workspace_boundary, output_budget):
    tool = ReadFileTool(workspace_boundary, output_budget)

    assert tool.parameters == {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read.",
            },
            "offset": {
                "type": "integer",
                "description": "Starting line number to read. Line numbers are 1-based. Defaults to the first line.",
                "minimum": 1,
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of lines to read. Defaults to reading until the end of the file.",
                "minimum": 1,
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    }


def test_read_file_supports_offset_and_limit(
    tmp_path,
    workspace_boundary,
    output_budget,
    ):
    file = tmp_path / "test.txt"
    file.write_text(
        "line 1\n"
        "line 2\n"
        "line 3\n"
        "line 4\n"
        "line 5\n",
        newline="\n",
        encoding="utf-8"
    )
    
    tool = ReadFileTool(workspace_boundary, output_budget)

    result = tool.execute(
        path="test.txt",
        offset=2,
        limit=2,
    )

    assert result == "line 2\nline 3\n"


def test_read_file_rejects_invalid_offset(
    tmp_path,
    workspace_boundary,
    output_budget,
):
    file = tmp_path / "test.txt"
    file.touch()

    tool = ReadFileTool(workspace_boundary, output_budget)

    with pytest.raises(ValueError):
        tool.execute(path="test.txt", offset=0)


def test_read_file_rejects_invalid_limit(
    tmp_path,
    workspace_boundary,
    output_budget,
):
    file = tmp_path / "test.txt"
    file.touch()

    tool = ReadFileTool(workspace_boundary, output_budget)

    with pytest.raises(ValueError):
        tool.execute(path="test.txt", limit=0)


def test_read_file_returns_empty_when_offset_is_past_end(
    tmp_path,
    workspace_boundary,
    output_budget,
):
    file = tmp_path / "test.txt"
    file.write_text(
        "line 1\n"
        "line 2\n"
        "line 3\n",
        encoding="utf-8"
    )

    tool = ReadFileTool(workspace_boundary, output_budget)

    result = tool.execute(
        path="test.txt",
        offset=10,
    )

    assert result == ""


def test_read_file_returns_remaining_lines_when_limit_exceeds_file(
    tmp_path,
    workspace_boundary,
    output_budget,
):
    file = tmp_path / "test.txt"
    file.write_text(
        "line 1\n"
        "line 2\n"
        "line 3\n",
        newline="\n",
        encoding="utf-8",
    )

    tool = ReadFileTool(workspace_boundary, output_budget)

    result = tool.execute(
        path="test.txt",
        offset=2,
        limit=100,
    )

    assert result == "line 2\nline 3\n"


def test_read_file_truncates_oversized_single_line_with_notice(tmp_path, workspace_boundary):
    file = tmp_path / "test.txt"
    file.write_text("x" * 30, encoding="utf-8")

    output_budget = OutputBudget(max_chars=20)

    tool = ReadFileTool(workspace_boundary, output_budget)

    result = tool.execute(path="test.txt")

    assert len(result) == 20
    assert result == "x" * 8 + "\n[truncated]"


def test_read_file_truncation_notice(tmp_path, workspace_boundary):
    file = tmp_path / "test.txt"
    file.write_text(
        "line12\n"
        "loongloonglooongtextloongloonglooongtext",
        newline="\n",
        encoding="utf-8"
    )

    output_budget = OutputBudget(max_chars=46)

    tool = ReadFileTool(workspace_boundary, output_budget)

    result = tool.execute(path="test.txt")

    expected_notice = "[truncated]"

    assert result.startswith("line12\n")
    assert result.endswith("\n" + expected_notice)
    assert len(result) <= 46


def test_read_file_preserves_original_line_endings_and_blank_lines(
    tmp_path, workspace_boundary, output_budget
):
    file = tmp_path / "test.txt"
    file.write_bytes(
        b"a\r\n\r\nb\r\n"
    )

    tool = ReadFileTool(workspace_boundary, output_budget)

    result = tool.execute(path="test.txt")

    assert result == "a\r\n\r\nb\r\n"


def test_read_file_preserves_unicode_line_separator(
    tmp_path, workspace_boundary, output_budget
):
    file = tmp_path / "test.txt"
    content = "alpha\u2028beta"
    file.write_bytes(content.encode("utf-8"))

    tool = ReadFileTool(workspace_boundary, output_budget)

    result = tool.execute(path="test.txt")

    assert result == content
