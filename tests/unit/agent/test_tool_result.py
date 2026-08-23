from coding_agent.agent.tool_result import ToolResult


def test_tool_result_stores_tool_name_and_result():
    result = ToolResult(
        call_id="call_123",
        tool_name="read_file",
        result="file contents",
    )

    assert result.tool_name == "read_file"
    assert result.result == "file contents"


def test_tool_result_is_immutable():
    result = ToolResult(
        call_id="call_123",
        tool_name="read_file",
        result="file contents",
    )

    try:
        result.result = "changed"
        assert False
    except AttributeError:
        pass