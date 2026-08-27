import pytest
from unittest.mock import MagicMock, patch

from harness.llm.base_llm import BaseLLM
from harness.llm.message import Message
from harness.llm.local import LocalLLM
from harness.agent.agent_response import AgentResponse



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