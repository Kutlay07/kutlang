from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.write_file import WriteFileTool


def test_write_file_tool_metadata():
    tool = WriteFileTool()

    assert tool.name == "write_file"
    assert tool.description == "Write content to a file"


def test_write_file_tool_implements_base_tool():
    tool = WriteFileTool()

    assert isinstance(tool, BaseTool)


def test_write_file_tool_execute(tmp_path):
    file = tmp_path / "test.txt"

    tool = WriteFileTool()

    result = tool.execute(
        path=str(file),
        content="Hello world",
    )

    assert result == f"Successfully wrote to {file}"
    assert file.read_text(encoding="utf-8") == "Hello world"