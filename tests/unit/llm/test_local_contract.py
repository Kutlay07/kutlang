from unittest.mock import MagicMock, patch

from harness.agent.agent_response import AgentResponse
from harness.llm.base_llm import BaseLLM
from harness.llm.local import LocalLLM
from harness.llm.message import Message


def test_local_llm_implements_current_generate_contract():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("harness.llm.local.OpenAI", return_value=mock_client):
        llm = LocalLLM(
            base_url="http://test/v1",
            model="test-model",
        )

        result = llm.generate(
            [
                Message(
                    role="user",
                    content="Hello",
                )
            ],
            [],
        )

    assert isinstance(llm, BaseLLM)
    assert isinstance(result, AgentResponse)
    assert result.text == "Hello"