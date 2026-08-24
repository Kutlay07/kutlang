from unittest.mock import MagicMock, patch, ANY

from harness.llm.base_llm import BaseLLM
from harness.llm.message import Message
from harness.llm.openai import OpenAILLM
from harness.agent.agent_response import AgentResponse
from harness.tools.base_tool import BaseTool
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult


def test_openai_llm_initializes():
    with patch("harness.llm.openai.OpenAI") as openai:
        llm = OpenAILLM("gpt-5")

        openai.assert_called_once_with()
        assert llm.client is openai.return_value
        assert llm.model == "gpt-5"


def test_openai_llm_implements_base_llm():
    with patch("harness.llm.openai.OpenAI"):
        llm = OpenAILLM("gpt-5")

        assert isinstance(llm, BaseLLM)


def test_openai_llm_generate():
    with patch("harness.llm.openai.OpenAI") as openai:
        client = openai.return_value

        response = MagicMock()
        response.output_text = "Hello world"

        client.responses.create.return_value = response

        llm = OpenAILLM("gpt-5")

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


def test_openai_llm_parses_tool_calls():
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

        llm = OpenAILLM("gpt-5")

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


def test_openai_llm_builds_tool_call_and_result_input():
    with patch("harness.llm.openai.OpenAI") as openai:
        client = openai.return_value

        response = MagicMock()
        response.output = []
        response.output_text = "Done"

        client.responses.create.return_value = response

        llm = OpenAILLM("gpt-5")

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


def test_openai_llm_handles_malformed_tool_arguments():
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

        llm = OpenAILLM("gpt-5")

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