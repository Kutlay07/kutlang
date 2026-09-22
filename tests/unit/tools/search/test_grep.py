import pytest

from harness.security.workspace_boundary import WorkspaceBoundaryViolation
from harness.tools.output_budget import OutputBudget
from harness.tools.search.grep import GrepTool


def test_grep_tool_parameters(
    workspace_boundary,
    search_visibility,
    output_budget,
):
    tool = GrepTool(
        workspace_boundary,
        search_visibility, 
        output_budget,
        )

    assert tool.parameters == {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The text string or regex pattern to search for inside the files (e.g., 'def execute', 'TODO').",
            },
            "pattern": {
                "type": "string",
                "description": "File pattern to restrict the search, relative to the workspace root. Defaults to '**/*' to search all files.",
            },
            "before": {
                "type": "integer",
                "description": "The number of lines of context to include BEFORE each match.",
                "minimum": 0,
            },
            "after": {
                "type": "integer",
                "description": "The number of lines of context to include AFTER each match.",
                "minimum": 0,
            },
            "max_results": {
                "type": "integer",
                "description": "The number of matches the tool will return.",
                "minimum": 0,
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    }


def test_grep_tool_finds_text_matches(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    file1 = tmp_path / "first.py"
    file2 = tmp_path / "second.py"
    file3 = tmp_path / "third.txt"

    file1.write_text("hello world", encoding="utf-8")
    file2.write_text("hello world", encoding="utf-8")
    file3.write_text("nothing", encoding="utf-8")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    result = tool.execute(query="hello", pattern="*.py")

    assert str(file1.relative_to(tmp_path)) in result
    assert str(file2.relative_to(tmp_path)) in result
    assert str(file3.relative_to(tmp_path)) not in result


def test_grep_tool_supports_regex(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    file = tmp_path / "test.py"
    file.write_text(
        "hello world\n"
        "hello again\n"
        "hello there\n",
        encoding="utf-8",
    )

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    result = tool.execute(query="hello (world|again)")

    assert "hello world" in result
    assert "hello again" in result
    assert "hello there" not in result


def test_grep_tool_returns_workspace_relative_paths(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    file = tmp_path / "test.py"
    file.write_text("hello world", encoding="utf-8")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )
    
    result = tool.execute(query="hello")
    
    assert "test.py:1:hello world" in result
    assert str(tmp_path) not in result


def test_grep_tool_raises_on_invalid_regex(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    file = tmp_path / "test.py"
    file.write_text("hello world", encoding="utf-8")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    with pytest.raises(RuntimeError):
        tool.execute(query="[invalid)")


def test_grep_tool_treats_dash_prefixed_query_as_search_pattern(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    file = tmp_path / "test.py"
    file.write_text("-hello", encoding="utf-8")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    result = tool.execute(query="-hello")

    assert str(file.relative_to(tmp_path)) in result


def test_grep_tool_hides_sensitive_files(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    file1 = tmp_path / ".env"
    file1.write_text("hello", encoding="utf-8")

    file2 = tmp_path / "normal.py"
    file2.write_text("hello", encoding="utf-8")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    result = tool.execute(query="hello")

    assert str(file1.relative_to(tmp_path)) not in result
    assert str(file2.relative_to(tmp_path)) in result


def test_grep_tool_rejects_pattern_outside_workspace(
    workspace_boundary,
    search_visibility,
    output_budget,
):
    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    with pytest.raises(WorkspaceBoundaryViolation):
        tool.execute(query="hello", pattern="../*.py")


def test_grep_tool_rejects_absolute_pattern(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    pattern = str(tmp_path / "*.py")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    with pytest.raises(WorkspaceBoundaryViolation):
        tool.execute(query="hello", pattern=pattern)


def test_grep_tool_returns_empty_result_when_no_match(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    file = tmp_path / "test.py"
    file.write_text("hello world", encoding="utf-8")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    result = tool.execute(query="goodbye")

    assert result == ""


def test_grep_tool_enforces_output_budget(
    tmp_path,
    workspace_boundary,
    search_visibility,
):
    file_names = [f"module_{index:02d}.py" for index in range(20)]
    for name in file_names:
        (tmp_path / name).write_text("hello", encoding="utf-8")
    
    budget = OutputBudget(max_chars=100)
    tool = GrepTool(
        workspace_boundary,
        search_visibility, 
        output_budget=budget,
        )

    result = tool.execute(query="hello", pattern="*.py")

    lines = result.splitlines()

    notice = lines[-1]
    assert notice.startswith("[truncated:")
    assert f"/{len(file_names)} lines" in notice
    assert "refine search" in notice

    shown_files = lines[:-1]
    assert shown_files
    assert all(any(line.startswith(name) for name in file_names) for line in shown_files)

    assert len(result) <= budget.max_chars


def test_grep_tool_ignores_binary_files(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    normal_file = tmp_path / "normal.py"
    binary_file = tmp_path / "binary"
    normal_file.write_text("hello", encoding="utf-8")
    binary_file.write_bytes(b"\x00\x01\x02hello\xff\xfe")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
    )

    result = tool.execute(query="hello")

    assert str(normal_file.relative_to(tmp_path)) in result
    assert str(binary_file.relative_to(tmp_path)) not in result


def test_grep_tool_supports_utf16_files(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    normal_file = tmp_path / "normal.py"
    utf16_file = tmp_path / "utf16.txt"

    normal_file.write_text("hello", encoding="utf-8")
    utf16_file.write_bytes("hello".encode("utf-16"))

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
    )

    result = tool.execute(query="hello")

    assert "normal.py:1:hello" in result
    assert "utf16.txt:1:hello" in result


def test_grep_tool_returns_match_context(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    file = tmp_path / "test.py"

    file.write_text(
        "before\n"
        "TARGET\n"
        "after\n",
        encoding="utf-8",
    )

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
    )

    result = tool.execute(
        query="TARGET",
        before=1,
        after=1,
    )

    assert "test.py:1:before" in result
    assert "test.py:2:TARGET" in result
    assert "test.py:3:after" in result


def test_grep_tool_rejects_negative_before(
    workspace_boundary,
    search_visibility,
    output_budget,
):
    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget
    )
    
    with pytest.raises(ValueError):
        tool.execute(query="hello", before=-1)


def test_grep_tool_rejects_negative_after(
    workspace_boundary,
    search_visibility,
    output_budget,
):
    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
    )
    
    with pytest.raises(ValueError):
        tool.execute(query="hello", after=-1)


def test_grep_tool_rejects_negative_max_results(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    file = tmp_path / "test.py"
    file.write_text("hello\n", encoding="utf-8")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
    )

    with pytest.raises(ValueError):
        tool.execute(query="hello", max_results=-1)


def test_grep_tool_limits_number_of_matches(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):    
    file = tmp_path / "test.py"

    file.write_text(
        "hello\n"
        "nothing\n"
        "hello\n"
        "nothing\n"
        "hello\n",
        encoding="utf-8",
    )

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
    )

    result = tool.execute(
        query="hello",
        max_results=2,
    )

    assert "test.py:1:hello" in result
    assert "test.py:3:hello" in result
    assert "test.py:5:hello" not in result


def test_grep_tool_limits_matches_without_truncating_context(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    file = tmp_path / "test.py"

    file.write_text(
        "hello\n"
        "before second\n"
        "hello\n"
        "after second\n"
        "hello\n"
        "after third\n",
        encoding="utf-8",
    )

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
    )

    result = tool.execute(
        query="hello",
        before=1,
        after=1,
        max_results=2,
    )

    assert "test.py:1:hello" in result
    assert "test.py:2:before second" in result
    assert "test.py:3:hello" in result
    assert "test.py:4:after second" in result

    assert "test.py:5:hello" not in result
    assert "test.py:6:after third" not in result


def test_grep_tool_returns_empty_result_when_max_results_is_zero(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    file = tmp_path / "test.py"
    file.write_text("hello\nhello\n", encoding="utf-8")

    tool = GrepTool(
        workspace_boundary,
        search_visibility,
        output_budget,
    )

    result = tool.execute(
        query="hello",
        max_results=0,
    )

    assert result == ""