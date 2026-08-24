from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.list_directory import ListDirectoryTool


def test_list_directory_tool_metadata():
    tool = ListDirectoryTool()

    assert tool.name == "list_directory"
    assert tool.description == "List the contents of a directory"


def test_list_directory_tool_implements_base_tool():
    tool = ListDirectoryTool()

    assert isinstance(tool, BaseTool)


def test_list_directory_tool_execute(tmp_path):
    (tmp_path / "b.py").write_text("", encoding="utf-8")
    (tmp_path / "a.py").write_text("", encoding="utf-8")
    (tmp_path / "src").mkdir()

    tool = ListDirectoryTool()

    result = tool.execute(path=str(tmp_path))

    assert result == "a.py\nb.py\nsrc"


def test_list_directory_tool_raises_for_missing_directory(tmp_path):
    tool = ListDirectoryTool()

    missing = tmp_path / "missing"

    try:
        tool.execute(path=str(missing))
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")