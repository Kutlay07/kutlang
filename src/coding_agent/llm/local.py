from transformers import AutoModelForCausalLM, AutoTokenizer

from .base_llm import BaseLLM
from .message import Message
from coding_agent.agent.agent_response import AgentResponse
from coding_agent.tools.base_tool import BaseTool


class LocalLLM(BaseLLM):
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
        )

    def generate(
        self,
        conversation,
        tools: list[BaseTool],
    ) -> AgentResponse:
        chat = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in conversation
        ]

        inputs = self.tokenizer.apply_chat_template(
            chat,
            return_tensors="pt",
            add_generation_prompt=True,
        )

        outputs = self.model.generate(inputs)

        text = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        )

        return AgentResponse(text=text)