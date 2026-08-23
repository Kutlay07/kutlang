from coding_agent.tools.base_tool import BaseTool
from coding_agent.tools.filesystem.read_file import ReadFileTool


def test_read_file_tool_metadata():
    tool = ReadFileTool()

    assert tool.name == "read_file"
    assert tool.description == "Read the contents of a file"


def test_read_file_tool_implements_base_tool():
    tool = ReadFileTool()

    assert isinstance(tool, BaseTool)


def test_read_file_tool_execute(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("Hello world", encoding="utf-8")

    tool = ReadFileTool()

    result = tool.execute(path=str(file))

    assert result == "Hello world"


def test_read_file_tool_parameters():
    tool = ReadFileTool()

    assert tool.parameters == {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read.",
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    }