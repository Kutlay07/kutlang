from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.directory_exists import (
    DirectoryExistsTool,
)


def test_directory_exists_tool_metadata():
    tool = DirectoryExistsTool()

    assert tool.name == "directory_exists"
    assert tool.description == "Check whether a directory exists"


def test_directory_exists_tool_implements_base_tool():
    tool = DirectoryExistsTool()

    assert isinstance(tool, BaseTool)


def test_directory_exists_tool_returns_true_for_existing_directory(tmp_path):
    directory = tmp_path / "src"
    directory.mkdir()

    tool = DirectoryExistsTool()

    assert tool.execute(path=str(directory)) == "true"


def test_directory_exists_tool_returns_false_for_missing_directory(tmp_path):
    tool = DirectoryExistsTool()

    assert tool.execute(
        path=str(tmp_path / "missing")
    ) == "false"


def test_directory_exists_tool_returns_false_for_file(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("Hello", encoding="utf-8")

    tool = DirectoryExistsTool()

    assert tool.execute(path=str(file)) == "false"