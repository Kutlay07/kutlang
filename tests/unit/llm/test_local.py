import pytest
from unittest.mock import MagicMock, patch

from harness.llm.base_llm import BaseLLM
from harness.llm.message import Message
from harness.llm.local import LocalLLM
from harness.agent.agent_response import AgentResponse
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.tools.base_tool import BaseTool



def test_local_llm_initializes():
    with patch("harness.llm.local.OpenAI") as openai:
        llm = LocalLLM(
            base_url="http://test/v1",
            model="test-model",
        )
        
        openai.assert_called_once_with(
            base_url="http://test/v1",
            api_key="not-needed",
        )
        
        assert llm.base_url == "http://test/v1"
        assert llm.model == "test-model"


def test_local_llm_implements_base_llm():
    with patch("harness.llm.local.OpenAI"):
        llm = LocalLLM(
            base_url="http://test/v1",
            model="test-model",
        )
        
        assert isinstance(llm, BaseLLM)


def test_local_llm_generate():
    mock_client = MagicMock()
    mock_response = MagicMock()
    
    mock_response.choices[0].message.content = "Hello world"
    
    mock_client.chat.completions.create.return_value = mock_response
    
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
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


def test_build_input():
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
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


def test_tool_result_build_input():
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
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


def test_format_tools():
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


def test_parse_tool_calls():
    llm = LocalLLM(
        base_url="http://test/v1",
        model="test-model",
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