import pytest

from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.move_file import MoveFileTool


def test_move_file_tool_metadata():
    tool = MoveFileTool()

    assert tool.name == "move_file"
    assert tool.description == "Move a file to a different path"


def test_move_file_tool_implements_base_tool():
    tool = MoveFileTool()

    assert isinstance(tool, BaseTool)


def test_move_file_tool_execute(tmp_path):
    source = tmp_path / "old.txt"
    destination = tmp_path / "new.txt"

    source.write_text("Hello", encoding="utf-8")

    tool = MoveFileTool()

    result = tool.execute(
        source=str(source),
        destination=str(destination),
    )

    assert result == f"Successfully moved {source} to {destination}"
    assert not source.exists()
    assert destination.read_text(encoding="utf-8") == "Hello"


def test_move_file_tool_raises_for_missing_source(tmp_path):
    tool = MoveFileTool()

    with pytest.raises(FileNotFoundError):
        tool.execute(
            source=str(tmp_path / "missing.txt"),
            destination=str(tmp_path / "new.txt"),
        )