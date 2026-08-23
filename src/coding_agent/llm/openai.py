from openai import OpenAI
import json

from coding_agent.agent.agent_response import AgentResponse
from coding_agent.tools.base_tool import BaseTool
from coding_agent.agent.tool_call import ToolCall
from coding_agent.agent.tool_result import ToolResult

from .base_llm import BaseLLM, ConversationItem
from .message import Message


class OpenAILLM(BaseLLM):
    def __init__(self, model: str):
        self.client = OpenAI()
        self.model = model
        
    def _parse_tool_calls(
        self,
        response,
    ) -> tuple[list[ToolCall], str | None]:
        tool_calls = []

        for item in response.output:
            if item.type != "function_call":
                continue

            try:
                arguments = json.loads(item.arguments)
            except json.JSONDecodeError:
                return [], f"Invalid tool arguments for {item.name}"

            tool_calls.append(
                ToolCall(
                    call_id=item.call_id,
                    name=item.name,
                    arguments=arguments,
                )
            )

        return tool_calls, None
    
    def _build_input(self, conversation):
        inputs = []

        for item in conversation:
            if isinstance(item, Message):
                inputs.append(
                    {
                        "role": item.role,
                        "content": item.content,
                    }
                )

            elif isinstance(item, ToolCall):
                inputs.append(
                    {
                        "type": "function_call",
                        "call_id": item.call_id,
                        "name": item.name,
                        "arguments": json.dumps(item.arguments),
                    }
                )

            elif isinstance(item, ToolResult):
                inputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": item.result,
                    }
                )

        return inputs

    def generate(
        self,
        conversation: list[ConversationItem],
        tools: list[BaseTool],
    ) -> AgentResponse:
        response = self.client.responses.create(
            model=self.model,
            input=self._build_input(conversation),
            tools=[
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
                for tool in tools
            ],
        )

        tool_calls, error = self._parse_tool_calls(response)

        return AgentResponse(
            text=error or response.output_text or None,
            tool_calls=tool_calls or None,
        )