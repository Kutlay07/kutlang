import pytest

from harness.security.workspace_boundary import WorkspaceBoundaryViolation
from harness.tools.output_budget import OutputBudget
from harness.tools.search.glob import GlobTool
from harness.tools.sync_base_tool import SyncBaseTool


def test_glob_tool_metadata(
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    tool = GlobTool(
        workspace_boundary, 
        search_visibility,
        output_budget,)

    assert tool.name == "glob"
    assert tool.description == ("Fast file pattern matching relative to the workspace root.")


def test_glob_tool_implements_base_tool(
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    tool = GlobTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )
    
    assert isinstance(tool, SyncBaseTool)


def test_glob_tool_parameters(
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    tool = GlobTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    assert tool.parameters == {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Pattern to search for, such as '**/*.py' or 'src/*.ts'.",
            },
        },
        "required": ["pattern"],
        "additionalProperties": False,
    }


def test_glob_tool_executes(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    file1 = tmp_path / "test.py"
    file2 = tmp_path / "test2.py"
    file3 = tmp_path / "test.txt"

    file1.write_text("Hello world", encoding="utf-8")
    file2.write_text("Hello world", encoding="utf-8")
    file3.write_text("Hello world", encoding="utf-8")

    tool = GlobTool(
        workspace_boundary, 
        search_visibility,
        output_budget,
        )

    result = tool.execute(pattern="*.py")

    assert str(file1.relative_to(tmp_path)) in result
    assert str(file2.relative_to(tmp_path)) in result
    assert str(file3.relative_to(tmp_path)) not in result


def test_glob_tool_recursive(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    file1 = tmp_path / "root.py"
    folder = tmp_path / "sub"
    file2 = folder / "nested.py"

    file1.write_text("Hello world", encoding="utf-8")
    folder.mkdir()
    file2.write_text("Hello world", encoding="utf-8")

    tool = GlobTool(
        workspace_boundary, 
        search_visibility,
        output_budget,
        )

    result = tool.execute(pattern="**/*.py")
    
    assert str(file1.relative_to(tmp_path)) in result
    assert str(file2.relative_to(tmp_path)) in result


def test_glob_tool_no_matches(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    file = tmp_path / "test.py"

    tool = GlobTool(
        workspace_boundary, 
        search_visibility,
        output_budget,
        )

    result = tool.execute(pattern="*.txt")

    assert result == ""


def test_glob_tool_finds_directories(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    folder = tmp_path / "src"
    file = tmp_path / "main.py"
    folder.mkdir()
    file.write_text("hi", encoding="utf-8")
    
    tool = GlobTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )
    
    result = tool.execute(pattern="*")
    
    assert str(folder.relative_to(tmp_path)) in result
    assert str(file.relative_to(tmp_path)) in result


def test_glob_tool_returns_relative_paths_as_string(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    file1 = tmp_path / "test.py"
    file2 = tmp_path / "sub" / "nested.py"
    
    file1.write_text("hello", encoding="utf-8")
    file2.parent.mkdir()
    file2.write_text("hello", encoding="utf-8")

    tool = GlobTool(
        workspace_boundary, 
        search_visibility,
        output_budget,
        )

    result = tool.execute(pattern="**/*.py")

    assert isinstance(result, str)
    assert str(file1.relative_to(tmp_path)) in result
    assert str(file2.relative_to(tmp_path)) in result
    assert str(tmp_path) not in result


def test_glob_tool_rejects_path_traversal(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    tool = GlobTool(
        workspace_boundary, 
        search_visibility,
        output_budget,
        )

    with pytest.raises(WorkspaceBoundaryViolation):
        tool.execute(pattern="../*.py")


def test_glob_tool_rejects_pattern_outside_workspace(
    tmp_path,
    workspace_boundary,
    search_visibility,
    output_budget,
):
    tool = GlobTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    with pytest.raises(WorkspaceBoundaryViolation):
        tool.execute(pattern="../*.py")


def test_glob_tool_rejects_absolute_pattern(
    tmp_path, 
    workspace_boundary,
    search_visibility,
    output_budget,
    ):
    tool = GlobTool(
        workspace_boundary,
        search_visibility,
        output_budget,
        )
    
    with pytest.raises(WorkspaceBoundaryViolation):
        tool.execute(pattern=str(tmp_path / "*.py"))


def test_glob_tool_enforces_output_budget(
    tmp_path,
    workspace_boundary,
    search_visibility,
    ):
    file_names = [f"module_{index:02d}.py" for index in range(20)]
    for name in file_names:
        (tmp_path / name).write_text("hello", encoding="utf-8")

    budget = OutputBudget(max_chars=80)
    tool = GlobTool(
        workspace_boundary,
        search_visibility, 
        output_budget=budget,
        )

    result = tool.execute(pattern="*.py")

    lines = result.splitlines()

    notice = lines[-1]
    assert notice.startswith("[truncated:")
    assert f"/{len(file_names)} lines" in notice
    assert "refine search" in notice

    shown_files = lines[:-1]
    assert shown_files
    assert all(line in file_names for line in shown_files)

    assert len(result) <= budget.max_chars