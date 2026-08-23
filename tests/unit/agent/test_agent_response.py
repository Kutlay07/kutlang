from coding_agent.agent.agent_response import AgentResponse
from coding_agent.agent.tool_call import ToolCall


def test_agent_response_can_contain_text():
    response = AgentResponse(text="Hello world")

    assert response.text == "Hello world"
    assert response.tool_calls is None


def test_agent_response_can_contain_tool_calls():
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    response = AgentResponse(tool_calls=[tool_call])

    assert response.text is None
    assert response.tool_calls == [tool_call]


def test_agent_response_can_contain_text_and_tool_calls():
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    response = AgentResponse(
        text="I need to inspect the file.",
        tool_calls=[tool_call],
    )

    assert response.text == "I need to inspect the file."
    assert response.tool_calls == [tool_call]