import pytest
from unittest.mock import MagicMock, patch

from coding_agent.agent.agent_response import AgentResponse
from coding_agent.llm.local import LocalLLM
from coding_agent.llm.message import Message


pytestmark = pytest.mark.slow


def test_local_llm_implements_current_generate_contract():
    with patch(
        "transformers.AutoTokenizer.from_pretrained",
    ) as tokenizer, patch(
        "transformers.AutoModelForCausalLM.from_pretrained",
    ) as model:

        tokenizer_instance = tokenizer.return_value
        model_instance = model.return_value

        tokenizer_instance.apply_chat_template.return_value = MagicMock()
        model_instance.generate.return_value = [[1, 2, 3]]
        tokenizer_instance.decode.return_value = "Hello"

        llm = LocalLLM("test-model")

        result = llm.generate(
    [
        Message(
            role="user",
            content="Hello",
        )
    ],
    [],
    )

        assert isinstance(result, AgentResponse)
        assert result.text == "Hello"