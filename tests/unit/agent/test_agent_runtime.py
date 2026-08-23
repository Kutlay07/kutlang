import pytest
from unittest.mock import MagicMock

from coding_agent.agent.agent_response import AgentResponse
from coding_agent.agent.agent_runtime import AgentRuntime
from coding_agent.llm.base_llm import BaseLLM
from coding_agent.tools.tool_registry import ToolRegistry
from coding_agent.agent.tool_call import ToolCall
from coding_agent.agent.tool_result import ToolResult
from coding_agent.llm.message import Message
from coding_agent.tools.base_tool import BaseTool


def test_runtime_initializes_with_llm_and_tools():
    llm = MagicMock(spec=BaseLLM)
    tools = MagicMock(spec=ToolRegistry)

    runtime = AgentRuntime(llm, tools)

    assert runtime.llm is llm
    assert runtime.tools is tools


def test_runtime_runs_llm():
    llm = MagicMock(spec=BaseLLM)

    tool = MagicMock(spec=BaseTool)
    tool.name = "read_file"

    tools = ToolRegistry([tool])

    response = AgentResponse(text="Hello world")
    llm.generate.return_value = response

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Hello")

    llm.generate.assert_called_once_with(
        [
            Message(
                role="user",
                content="Hello",
            )
        ],
        [tool],
    )

    assert result is response


def test_runtime_executes_tool_calls():
    llm = MagicMock(spec=BaseLLM)
    tools = MagicMock(spec=ToolRegistry)

    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="Done"),
    ]

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Read main.py")

    tools.get.assert_called_once_with("read_file")
    tool.execute.assert_called_once_with(path="main.py")
    assert result.text == "Done"


def test_runtime_sends_tool_result_back_to_llm():
    llm = MagicMock(spec=BaseLLM)
    tools = MagicMock(spec=ToolRegistry)

    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    first_response = AgentResponse(
        tool_calls=[tool_call],
    )

    final_response = AgentResponse(
        text="Here is the file.",
    )

    llm.generate.side_effect = [
        first_response,
        final_response,
    ]

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Read main.py")

    assert result is final_response

    assert llm.generate.call_count == 2

    calls = llm.generate.call_args_list

    assert calls[1].args[0] == [
        Message(
            role="user",
            content="Read main.py",
        ),
        tool_call,
        ToolResult(
            call_id="call_123",
            tool_name="read_file",
            result="file contents",
        ),
    ]


def test_runtime_supports_multiple_tool_iterations():
    llm = MagicMock(spec=BaseLLM)
    tools = MagicMock(spec=ToolRegistry)

    tool = MagicMock()
    tool.execute.side_effect = [
        "first result",
        "second result",
    ]
    tools.get.return_value = tool

    first_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "first.py"},
    )

    second_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "second.py"},
    )

    first_response = AgentResponse(tool_calls=[first_call])
    second_response = AgentResponse(tool_calls=[second_call])
    final_response = AgentResponse(text="Done")

    llm.generate.side_effect = [
        first_response,
        second_response,
        final_response,
    ]

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Do the task")

    assert result is final_response
    assert llm.generate.call_count == 3
    assert tool.execute.call_count == 2


def test_runtime_raises_when_max_iterations_exceeded():
    llm = MagicMock(spec=BaseLLM)
    tools = MagicMock(spec=ToolRegistry)

    tool = MagicMock()
    tool.execute.return_value = "result"
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "test.py"},
    )

    llm.generate.return_value = AgentResponse(
        tool_calls=[tool_call],
    )

    runtime = AgentRuntime(
        llm,
        tools,
        max_iterations=2,
    )

    with pytest.raises(RuntimeError, match="Maximum agent iterations exceeded"):
        runtime.run("Keep going")

    assert llm.generate.call_count == 2


def test_runtime_returns_tool_error_as_tool_result():
    llm = MagicMock(spec=BaseLLM)
    tools = MagicMock(spec=ToolRegistry)

    tool = MagicMock()
    tool.execute.side_effect = FileNotFoundError("File not found")
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "missing.py"},
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="I couldn't find the file."),
    ]

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Read missing.py")

    assert result.text == "I couldn't find the file."
    tool.execute.assert_called_once_with(path="missing.py")

    second_messages = llm.generate.call_args_list[1].args[0]

    tool_result = second_messages[-1]

    assert isinstance(tool_result, ToolResult)
    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "read_file"
    assert tool_result.result == "File not found"
    assert tool_result.is_error is True

def test_tool_result_can_represent_error():
    result = ToolResult(
        call_id="call_123",
        tool_name="read_file",
        result="File not found",
        is_error=True,
    )

    assert result.call_id == "call_123"
    assert result.is_error is True


def test_runtime_handles_unknown_tool():
    llm = MagicMock(spec=BaseLLM)
    tools = MagicMock(spec=ToolRegistry)

    tools.get.side_effect = KeyError("unknown_tool")

    tool_call = ToolCall(
        call_id="call_123",
        name="unknown_tool",
        arguments={},
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="I don't have that tool."),
    ]

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Use unknown_tool")

    assert result.text == "I don't have that tool."

    second_messages = llm.generate.call_args_list[1].args[0]

    tool_result = second_messages[-1]

    assert isinstance(tool_result, ToolResult)
    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "unknown_tool"
    assert "unknown_tool" in tool_result.result
    assert tool_result.is_error is True


def test_runtime_formats_tool_errors_as_errors():
    llm = MagicMock(spec=BaseLLM)
    tools = MagicMock(spec=ToolRegistry)

    tool = MagicMock()
    tool.execute.side_effect = FileNotFoundError("File not found")
    tools.get.return_value = tool

    llm.generate.side_effect = [
        AgentResponse(
            tool_calls=[
                ToolCall(
                    call_id="call_123",
                    name="read_file",
                    arguments={"path": "missing.py"},
                )
            ]
        ),
        AgentResponse(text="Done"),
    ]

    runtime = AgentRuntime(llm, tools)

    runtime.run("Read missing.py")

    second_conversation = llm.generate.call_args_list[1].args[0]

    tool_result = second_conversation[-1]

    assert isinstance(tool_result, ToolResult)
    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "read_file"
    assert tool_result.result == "File not found"
    assert tool_result.is_error is True


def test_runtime_preserves_tool_call_id():
    llm = MagicMock(spec=BaseLLM)
    tools = MagicMock(spec=ToolRegistry)

    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    response = AgentResponse(
        tool_calls=[tool_call],
    )

    runtime = AgentRuntime(llm, tools)

    results = runtime._execute_tool_calls(response)

    assert results == [
        ToolResult(
            call_id="call_123",
            tool_name="read_file",
            result="file contents",
        )
    ]