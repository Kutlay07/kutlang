import pytest
from unittest.mock import MagicMock, patch

from coding_agent.llm.base_llm import BaseLLM
from coding_agent.llm.message import Message
from coding_agent.llm.local import LocalLLM
from coding_agent.agent.agent_response import AgentResponse


pytestmark = pytest.mark.slow


def test_local_llm_initializes():
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()

    with patch(
        "transformers.AutoTokenizer.from_pretrained",
        return_value=mock_tokenizer,
    ) as tokenizer:
        with patch(
            "transformers.AutoModelForCausalLM.from_pretrained",
            return_value=mock_model,
        ) as model:
            llm = LocalLLM("test-model")

            tokenizer.assert_called_once_with("test-model")

            model.assert_called_once_with(
                "test-model",
                device_map="auto",
            )

            assert llm.tokenizer is mock_tokenizer
            assert llm.model is mock_model


def test_local_llm_implements_base_llm():
    with patch(
        "transformers.AutoTokenizer.from_pretrained",
        return_value=MagicMock(),
    ), patch(
        "transformers.AutoModelForCausalLM.from_pretrained",
        return_value=MagicMock(),
    ):
        llm = LocalLLM("test-model")

        assert isinstance(llm, BaseLLM)


def test_local_llm_generate():
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()

    mock_inputs = MagicMock()
    mock_tokenizer.apply_chat_template.return_value = mock_inputs

    mock_outputs = [[1, 2, 3, 4]]
    mock_model.generate.return_value = mock_outputs

    mock_tokenizer.decode.return_value = "Hello world"

    with patch(
        "transformers.AutoTokenizer.from_pretrained",
        return_value=mock_tokenizer,
    ):
        with patch(
            "transformers.AutoModelForCausalLM.from_pretrained",
            return_value=mock_model,
        ):
            llm = LocalLLM("test-model")

            result = llm.generate(
                [
                        Message(
                            role="user",
                            content="Hello world",
                        )
                    ],
                    [],
                )

            mock_tokenizer.apply_chat_template.assert_called_once_with(
                [
                    {
                        "role": "user",
                        "content": "Hello world",
                    }
                ],
                return_tensors="pt",
                add_generation_prompt=True,
            )

            mock_model.generate.assert_called_once_with(
                mock_inputs
            )

            mock_tokenizer.decode.assert_called_once_with(
                mock_outputs[0],
                skip_special_tokens=True,
            )

            assert isinstance(result, AgentResponse)
            assert result.text == "Hello world"