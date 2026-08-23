from coding_agent.tools.base_tool import BaseTool
from coding_agent.tools.filesystem.file_exists import FileExistsTool


def test_file_exists_tool_metadata():
    tool = FileExistsTool()

    assert tool.name == "file_exists"
    assert tool.description == "Check whether a file exists"


def test_file_exists_tool_implements_base_tool():
    tool = FileExistsTool()

    assert isinstance(tool, BaseTool)


def test_file_exists_tool_returns_true_for_existing_file(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("Hello", encoding="utf-8")

    tool = FileExistsTool()

    assert tool.execute(path=str(file)) == "true"


def test_file_exists_tool_returns_false_for_missing_file(tmp_path):
    tool = FileExistsTool()

    assert tool.execute(
        path=str(tmp_path / "missing.txt")
    ) == "false"


def test_file_exists_tool_returns_false_for_directory(tmp_path):
    directory = tmp_path / "src"
    directory.mkdir()

    tool = FileExistsTool()

    assert tool.execute(path=str(directory)) == "false"