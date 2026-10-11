import pytest
from unittest.mock import MagicMock, patch

from harness.llm.base_llm import BaseLLM
from harness.llm.message import Message
from harness.llm.local import LocalLLM
from harness.agent.agent_response import AgentResponse
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.tools.output_budget import OutputBudget
from harness.tools.sync_base_tool import BaseTool



@pytest.fixture
def output_budget():
    return OutputBudget(max_chars=20_000)

def test_local_llm_initializes(output_budget):
    with patch("harness.llm.local.OpenAI") as openai:
        llm = LocalLLM(
            base_url="http://test/v1",
            model="test-model",
            output_budget=output_budget,
        )
        
        openai.assert_called_once_with(
            base_url="http://test/v1",
            api_key="not-needed",
        )
        
        assert llm.base_url == "http://test/v1"
        assert llm.model == "test-model"


def test_local_llm_implements_base_llm(output_budget):
    with patch("harness.llm.local.OpenAI"):
        llm = LocalLLM(
            base_url="http://test/v1",
            model="test-model",
            output_budget=output_budget,
        )
        
        assert isinstance(llm, BaseLLM)


def test_local_llm_generate(output_budget):
    mock_client = MagicMock()
    mock_response = MagicMock()
    
    mock_response.choices[0].message.content = "Hello world"
    
    mock_client.chat.completions.create.return_value = mock_response
    
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
        output_budget=output_budget,
    )
    
    llm.client = mock_client
    
    result = llm.generate(
        [
            Message(
                role="user",
                content="Hello world",
            )
        ],
        [],
    )
    
    mock_client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[
            {
                "role": "user",
                "content": "Hello world",
            }
        ],
        tools=[],
    )
    
    assert isinstance(result, AgentResponse)
    assert result.text == "Hello world"


def test_build_input(output_budget):
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
        output_budget=output_budget,
    )
    
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "test.py"},
    )
    
    built = llm._build_input([tool_call])
    
    assert len(built) == 1

    message = built[0]

    assert message["role"] == "assistant"
    assert message["tool_calls"][0]["id"] == "call_123"
    assert message["tool_calls"][0]["type"] == "function"
    assert message["tool_calls"][0]["function"]["name"] == "read_file"
    assert message["tool_calls"][0]["function"]["arguments"] == '{"path": "test.py"}'


def test_tool_result_build_input(output_budget):
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
        output_budget=output_budget,
    )
        
    tool_result = ToolResult(
        call_id="call_123",
        tool_name="read_file",
        result="file contents",
        is_error=False,
    )
    
    built = llm._build_input([tool_result])
    
    assert len(built) == 1
    
    message = built[0]
    
    assert message["role"] == "tool"
    assert message["tool_call_id"] == "call_123"
    assert message["content"] == "file contents"


def test_format_tools(output_budget):
    class FakeTool(BaseTool):
        @property
        def name(self):
            return "read_file"

        @property
        def description(self):
            return "Read a file"

        @property
        def parameters(self):
            return {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                }
            }

        def execute(self, **kwargs):
            return "..."
        
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
        output_budget=output_budget,
    )
    formatted = llm._format_tools([FakeTool()])
    
    assert len(formatted) == 1

    tool = formatted[0]

    assert tool["type"] == "function"
    assert tool["function"]["name"] == "read_file"
    assert tool["function"]["description"] == "Read a file"
    assert tool["function"]["parameters"] == {
        "type": "object",
        "properties": {
            "path": {"type": "string"}
        }
    }


def test_parse_tool_calls(output_budget):
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
        output_budget=output_budget,
    )

    function = MagicMock()
    function.name = "read_file"
    function.arguments = '{"path": "test.py"}'

    tool_call = MagicMock()
    tool_call.id = "call_123"
    tool_call.function = function
    
    response = MagicMock()
    response.choices[0].message.tool_calls = [tool_call]

    
    tool_calls, error = llm._parse_tool_calls(response)

    assert len(tool_calls) == 1

    tool_call = tool_calls[0]

    assert isinstance(tool_call, ToolCall)
    assert tool_call.call_id == "call_123"
    assert tool_call.name == "read_file"
    assert tool_call.arguments == {"path": "test.py"}

    assert error is None


def test_build_input_groups_multiple_tool_calls(output_budget):
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
        output_budget=output_budget,
    )

    tool_calls = [
        ToolCall(
            call_id="call_1",
            name="read_file",
            arguments={"path": "a.py"},
        ),
        ToolCall(
            call_id="call_2",
            name="read_file",
            arguments={"path": "b.py"},
        ),
    ]

    built = llm._build_input(tool_calls)

    assert len(built) == 1

    message = built[0]

    assert message["role"] == "assistant"
    assert len(message["tool_calls"]) == 2

    assert message["tool_calls"][0]["id"] == "call_1"
    assert message["tool_calls"][1]["id"] == "call_2"


@pytest.mark.parametrize("arguments", [None, 123, {}, []])
def test_parse_tool_calls_rejects_non_string_arguments(arguments, output_budget):
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
        output_budget=output_budget,
    )

    function = MagicMock()
    function.name = "read_file"
    function.arguments = arguments

    tool_call = MagicMock()
    tool_call.id = "call_123"
    tool_call.function = function

    response = MagicMock()
    response.choices[0].message.tool_calls = [tool_call]

    tool_calls, error = llm._parse_tool_calls(response)

    assert tool_calls == []
    assert error == "Invalid tool arguments for read_file"


def test_local_llm_truncates_oversized_tool_result_at_serialization():
    budget = OutputBudget(max_chars=20)

    local_llm = LocalLLM("https://test/v1", "test-model", output_budget=budget)

    tool_result = ToolResult(
        call_id="call_123",
        tool_name="read_file",
        result="x" * 30,
        is_error=False
    )

    content = local_llm._build_input([tool_result])

    assert content[-1]["content"] == "x" * 8 + "\n[truncated]"
    assert tool_result.result == "x" * 30
    assert content[-1]["tool_call_id"] == "call_123"


def test_local_llm_does_not_truncate_regular_messages():
    budget = OutputBudget(max_chars=20)

    local_llm = LocalLLM("https://test/v1", "test-model", output_budget=budget)

    message = Message(
        role="user",
        content="x" * 30,
    )

    result = local_llm._build_input([message])

    assert result[0]["content"] == "x" * 30
