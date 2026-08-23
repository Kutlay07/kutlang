from transformers import AutoModelForCausalLM, AutoTokenizer

from .base_llm import BaseLLM
from .message import Message


class LocalLLM(BaseLLM):
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
        )

    def generate(self, messages: list[Message]) -> str:
        chat = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        inputs = self.tokenizer.apply_chat_template(
            chat,
            return_tensors="pt",
            add_generation_prompt=True,
        )

        outputs = self.model.generate(inputs)

        return self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        )