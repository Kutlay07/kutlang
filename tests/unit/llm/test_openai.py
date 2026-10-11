from unittest.mock import MagicMock, patch, ANY

import pytest

from harness.llm.base_llm import BaseLLM
from harness.llm.message import Message
from harness.llm.openai import OpenAILLM
from harness.agent.agent_response import AgentResponse
from harness.tools.output_budget import OutputBudget
from harness.tools.sync_base_tool import BaseTool
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult

@pytest.fixture
def output_budget():
    return OutputBudget(max_chars=20_000)

def test_openai_llm_initializes(output_budget):
    with patch("harness.llm.openai.OpenAI") as openai:
        llm = OpenAILLM("gpt-5", output_budget=output_budget)

        openai.assert_called_once_with()
        assert llm.client is openai.return_value
        assert llm.model == "gpt-5"


def test_openai_llm_implements_base_llm(output_budget):
    with patch("harness.llm.openai.OpenAI"):
        llm = OpenAILLM("gpt-5", output_budget=output_budget)

        assert isinstance(llm, BaseLLM)


def test_openai_llm_generate(output_budget):
    with patch("harness.llm.openai.OpenAI") as openai:
        client = openai.return_value

        response = MagicMock()
        response.output_text = "Hello world"

        client.responses.create.return_value = response

        llm = OpenAILLM("gpt-5", output_budget=output_budget)

        messages = [
            Message(role="user", content="Hello"),
        ]
        
        tool = MagicMock(spec=BaseTool)

        tool.name = "read_file"
        tool.description = "Read the contents of a file"
        tool.parameters = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                },
            },
            "required": ["path"],
        }

        result = llm.generate(messages, [tool])

        client.responses.create.assert_called_once_with(
            model="gpt-5",
            input=[
                {
                    "role": "user",
                    "content": "Hello",
                },
            ],
            tools=[
                {
                    "type": "function",
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                            },
                        },
                        "required": ["path"],
                    },
                }
            ],
        )

        assert isinstance(result, AgentResponse)
        assert result.text == "Hello world"
        assert result.tool_calls is None


def test_openai_llm_parses_tool_calls(output_budget):
    with patch("harness.llm.openai.OpenAI") as openai:
        client = openai.return_value

        function_call = MagicMock()
        function_call.type = "function_call"
        function_call.call_id = "call_123"
        function_call.name = "read_file"
        function_call.arguments = '{"path": "main.py"}'

        response = MagicMock()
        response.output = [function_call]
        response.output_text = ""

        client.responses.create.return_value = response

        llm = OpenAILLM("gpt-5", output_budget=output_budget)

        messages = [
            Message(
                role="user",
                content="Read main.py",
            )
        ]

        tool = MagicMock(spec=BaseTool)
        tool.name = "read_file"
        tool.description = "Read the contents of a file"
        tool.parameters = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                },
            },
            "required": ["path"],
        }
        

        result = llm.generate(messages, [tool])

        assert result.tool_calls == [
            ToolCall(
                call_id="call_123",
                name="read_file",
                arguments={"path": "main.py"},
            )
        ]

        assert result.text is None


def test_openai_llm_builds_tool_call_and_result_input(output_budget):
    with patch("harness.llm.openai.OpenAI") as openai:
        client = openai.return_value

        response = MagicMock()
        response.output = []
        response.output_text = "Done"

        client.responses.create.return_value = response

        llm = OpenAILLM("gpt-5", output_budget=output_budget)

        conversation = [
            Message(
                role="user",
                content="Read main.py",
            ),
            ToolCall(
                call_id="call_123",
                name="read_file",
                arguments={"path": "main.py"},
            ),
            ToolResult(
                call_id="call_123",
                tool_name="read_file",
                result="file contents",
            ),
        ]

        tool = MagicMock(spec=BaseTool)
        tool.name = "read_file"
        tool.description = "Read the contents of a file"
        tool.parameters = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                },
            },
            "required": ["path"],
        }

        result = llm.generate(
            conversation,
            [tool],
        )

        client.responses.create.assert_called_once_with(
            model="gpt-5",
            input=[
                {
                    "role": "user",
                    "content": "Read main.py",
                },
                {
                    "type": "function_call",
                    "call_id": "call_123",
                    "name": "read_file",
                    "arguments": '{"path": "main.py"}',
                },
                {
                    "type": "function_call_output",
                    "call_id": "call_123",
                    "output": "file contents",
                },
            ],
            tools=ANY,
        )

        assert result.text == "Done"


def test_openai_llm_handles_malformed_tool_arguments(output_budget):
    with patch("harness.llm.openai.OpenAI") as openai:
        client = openai.return_value

        function_call = MagicMock()
        function_call.type = "function_call"
        function_call.call_id = "call_123"
        function_call.name = "read_file"
        function_call.arguments = '{"path": "main.py"'

        response = MagicMock()
        response.output = [function_call]
        response.output_text = ""

        client.responses.create.return_value = response

        llm = OpenAILLM("gpt-5", output_budget=output_budget)

        result = llm.generate(
            [
                Message(
                    role="user",
                    content="Read main.py",
                )
            ],
            [],
        )

        assert result.text is not None
        assert "Invalid tool arguments" in result.text


def test_openai_llm_truncates_oversized_tool_result_at_serialization():
    output_budget = OutputBudget(max_chars=20)

    with patch("harness.llm.openai.OpenAI"):
        llm = OpenAILLM("gpt-5", output_budget=output_budget)

        tool_result = ToolResult(
            call_id="call_123",
            tool_name="read_file",
            result="x" * 30,
            is_error=False
        )

        content = llm._build_input([tool_result])

        assert content[-1]["output"] == "x" * 8 + "\n[truncated]"
        assert tool_result.result == "x" * 30
        assert content[-1]["call_id"] == "call_123"


def test_openai_llm_does_not_truncate_regular_messages():
    output_budget = OutputBudget(max_chars=20)

    with patch("harness.llm.openai.OpenAI"):
        openai_llm = OpenAILLM("gpt-5", output_budget=output_budget)

        message = Message(
            role="user",
            content="x" * 30,
        )

        result = openai_llm._build_input([message])

        assert result[0]["content"] == "x" * 30
