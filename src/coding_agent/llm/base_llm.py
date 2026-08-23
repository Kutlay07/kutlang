from abc import ABC, abstractmethod
from typing import TypeAlias

from coding_agent.agent.agent_response import AgentResponse
from coding_agent.agent.tool_call import ToolCall
from coding_agent.agent.tool_result import ToolResult
from coding_agent.tools.base_tool import BaseTool

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