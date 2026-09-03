from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.read_file import ReadFileTool


def test_read_file_tool_metadata(workspace_boundary):
    tool = ReadFileTool(workspace_boundary)

    assert tool.name == "read_file"
    assert tool.description == "Read the contents of a file"


def test_read_file_tool_implements_base_tool(workspace_boundary):
    tool = ReadFileTool(workspace_boundary)

    assert isinstance(tool, BaseTool)


def test_read_file_tool_execute(tmp_path, workspace_boundary):
    file = tmp_path / "test.txt"
    file.write_text("Hello world", encoding="utf-8")

    tool = ReadFileTool(workspace_boundary)

    result = tool.execute(path=str(file))

    assert result == "Hello world"


def test_read_file_tool_parameters(workspace_boundary):
    tool = ReadFileTool(workspace_boundary)

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