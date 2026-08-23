from coding_agent.agent.tool_call import ToolCall


def test_tool_call_stores_name_and_arguments():
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    assert tool_call.name == "read_file"
    assert tool_call.arguments == {"path": "main.py"}


def test_tool_call_is_immutable():
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    try:
        tool_call.name = "write_file"
        assert False
    except AttributeError:
        pass