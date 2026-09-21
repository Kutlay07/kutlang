import pytest

from harness.security.workspace_boundary import WorkspaceBoundaryViolation
from harness.tools.output_budget import OutputBudget
from harness.tools.search.grep import GrepTool


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