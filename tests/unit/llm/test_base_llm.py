import pytest

from coding_agent.llm.base_llm import BaseLLM
from coding_agent.llm.message import Message


def test_llm_is_abstract():
    with pytest.raises(TypeError):
        BaseLLM()


def test_llm_subclass_must_implement_generate():
    class IncompleteLLM(BaseLLM):
        pass

    with pytest.raises(TypeError):
        IncompleteLLM()


def test_llm_subclass_can_implement_generate():
    class FakeLLM(BaseLLM):
        def generate(self, messages: list[Message]) -> str:
            return "fake response"

    llm = FakeLLM()

    result = llm.generate(
        [Message(role="user", content="Hello")]
    )

    assert result == "fake response"