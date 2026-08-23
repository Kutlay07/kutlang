from unittest.mock import MagicMock

from coding_agent.agent.agent_response import AgentResponse
from coding_agent.agent.agent_runtime import AgentRuntime
from coding_agent.agent.tool_call import ToolCall
from coding_agent.llm.base_llm import BaseLLM
from coding_agent.tools.filesystem.read_file import ReadFileTool
from coding_agent.tools.tool_registry import ToolRegistry
from coding_agent.tools.filesystem.write_file import WriteFileTool
from coding_agent.tools.filesystem.copy_file import CopyFileTool


def test_runtime_executes_real_read_file_tool(tmp_path):
    file = tmp_path / "main.py"
    file.write_text("print('hello')", encoding="utf-8")

    llm = MagicMock(spec=BaseLLM)

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": str(file)},
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="The file contains print('hello')."),
    ]

    tools = ToolRegistry([
        ReadFileTool(),
    ])

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Read main.py")

    assert result.text == "The file contains print('hello')."

    assert llm.generate.call_count == 2

    second_conversation = llm.generate.call_args_list[1].args[0]

    assert second_conversation[-1].result == "print('hello')"


def test_runtime_handles_real_read_file_error(tmp_path):
    missing_file = tmp_path / "missing.py"

    llm = MagicMock(spec=BaseLLM)

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": str(missing_file)},
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="I couldn't read the file."),
    ]

    tools = ToolRegistry([
        ReadFileTool(),
    ])

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Read missing.py")

    assert result.text == "I couldn't read the file."

    second_conversation = llm.generate.call_args_list[1].args[0]
    tool_result = second_conversation[-1]

    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "read_file"
    assert tool_result.is_error is True
    assert "No such file" in tool_result.result or "does not exist" in tool_result.result


def test_runtime_executes_multiple_real_tools(tmp_path):
    first_file = tmp_path / "first.py"
    second_file = tmp_path / "second.py"

    first_file.write_text("first", encoding="utf-8")
    second_file.write_text("second", encoding="utf-8")

    llm = MagicMock(spec=BaseLLM)

    first_call = ToolCall(
        call_id="call_1",
        name="read_file",
        arguments={"path": str(first_file)},
    )

    second_call = ToolCall(
        call_id="call_2",
        name="read_file",
        arguments={"path": str(second_file)},
    )

    llm.generate.side_effect = [
        AgentResponse(
            tool_calls=[first_call, second_call],
        ),
        AgentResponse(text="Both files read."),
    ]

    tools = ToolRegistry([
        ReadFileTool(),
    ])

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Read both files")

    assert result.text == "Both files read."

    second_conversation = llm.generate.call_args_list[1].args[0]

    results = second_conversation[-2:]

    assert results[0].call_id == "call_1"
    assert results[0].result == "first"

    assert results[1].call_id == "call_2"
    assert results[1].result == "second"


def test_runtime_executes_real_write_file_tool(tmp_path):
    file = tmp_path / "created.py"

    llm = MagicMock(spec=BaseLLM)

    tool_call = ToolCall(
        call_id="call_123",
        name="write_file",
        arguments={
            "path": str(file),
            "content": "print('hello')",
        },
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="File created."),
    ]

    tools = ToolRegistry([
        WriteFileTool(),
    ])

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Create the file")

    assert result.text == "File created."
    assert file.read_text(encoding="utf-8") == "print('hello')"

    second_conversation = llm.generate.call_args_list[1].args[0]
    tool_result = second_conversation[-1]

    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "write_file"
    assert tool_result.result == f"Successfully wrote to {file}"
    assert tool_result.is_error is False


def test_runtime_handles_real_write_file_error(tmp_path):
    directory = tmp_path / "directory"
    directory.mkdir()

    llm = MagicMock(spec=BaseLLM)

    tool_call = ToolCall(
        call_id="call_123",
        name="write_file",
        arguments={
            "path": str(directory),
            "content": "Hello",
        },
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="I couldn't write the file."),
    ]

    tools = ToolRegistry([
        WriteFileTool(),
    ])

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Write the file")

    assert result.text == "I couldn't write the file."

    second_conversation = llm.generate.call_args_list[1].args[0]
    tool_result = second_conversation[-1]

    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "write_file"
    assert tool_result.is_error is True


def test_runtime_executes_real_copy_file_tool(tmp_path):
    source = tmp_path / "original.py"
    destination = tmp_path / "copy.py"

    source.write_text("print('hello')", encoding="utf-8")

    llm = MagicMock(spec=BaseLLM)

    tool_call = ToolCall(
        call_id="call_123",
        name="copy_file",
        arguments={
            "source": str(source),
            "destination": str(destination),
        },
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="File copied."),
    ]

    tools = ToolRegistry([
        CopyFileTool(),
    ])

    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Copy original.py to copy.py")

    assert result.text == "File copied."

    assert source.read_text(encoding="utf-8") == "print('hello')"
    assert destination.read_text(encoding="utf-8") == "print('hello')"

    second_conversation = llm.generate.call_args_list[1].args[0]
    tool_result = second_conversation[-1]

    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "copy_file"
    assert tool_result.is_error is False
    assert tool_result.result == (
        f"Successfully copied {source} to {destination}"
    )