from openai import OpenAI
import json

from .base_llm import BaseLLM
from harness.agent.agent_response import AgentResponse
from harness.tools.base_tool import BaseTool
from .message import Message
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult


class LocalLLM(BaseLLM):
    def __init__(
        self, 
        base_url: str,
        model: str,
        ):
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="not-needed",
            )


    def _build_input(self, conversation):
        messages = []
        tool_calls = []

        def flush_tool_calls():
            if tool_calls:
                messages.append({
                    "role": "assistant",
                    "tool_calls": tool_calls.copy(),
                })
                tool_calls.clear()

        for item in conversation:
            if isinstance(item, Message):
                flush_tool_calls()

                messages.append({
                    "role": item.role,
                    "content": item.content,
                })

            elif isinstance(item, ToolCall):
                tool_calls.append({
                    "id": item.call_id,
                    "type": "function",
                    "function": {
                        "name": item.name,
                        "arguments": json.dumps(item.arguments),
                    },
                })

            elif isinstance(item, ToolResult):
                flush_tool_calls()

                messages.append({
                    "role": "tool",
                    "tool_call_id": item.call_id,
                    "content": item.result,
                })

        flush_tool_calls()

        return messages


    def _format_tools(self, tools):
        formatted_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in tools
        ]
        
        return formatted_tools


    def _parse_tool_calls(self, response):
        tool_calls = []

        for item in response.choices[0].message.tool_calls or []:
            try:
                if not isinstance(item.function.arguments, str):
                    raise TypeError

                arguments = json.loads(item.function.arguments)
            except (json.JSONDecodeError, TypeError):
                return [], f"Invalid tool arguments for {item.function.name}"

            tool_calls.append(
                ToolCall(
                    call_id=item.id,
                    name=item.function.name,
                    arguments=arguments,
                )
            )

        return tool_calls, None


    def generate(
        self,
        conversation,
        tools: list[BaseTool],
    ) -> AgentResponse:
        chat = self._build_input(conversation)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=chat,
            tools=self._format_tools(tools),
        )
        
        tool_calls, error = self._parse_tool_calls(response)
        
        return AgentResponse(
            text=error or response.choices[0].message.content or None,
            tool_calls=tool_calls or None
        )