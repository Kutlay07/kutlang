from abc import ABC, abstractmethod
from typing import TypeAlias

from harness.agent.agent_response import AgentResponse
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.tools.base_tool import BaseTool

from .message import Message


ConversationItem: TypeAlias = Message | ToolCall | ToolResult


class BaseLLM(ABC):

    @abstractmethod
    def generate(
        self,
        conversation: list[ConversationItem],
        tools: list[BaseTool],
    ) -> AgentResponse:
        ...