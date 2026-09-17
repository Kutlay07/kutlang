from abc import ABC, abstractmethod
from typing import TypeAlias

from harness.agent.agent_response import AgentResponse
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.tools.sync_base_tool import SyncBaseTool

from .message import Message


ConversationItem: TypeAlias = Message | ToolCall | ToolResult


class BaseLLM(ABC):

    @abstractmethod
    def generate(
        self,
        conversation: list[ConversationItem],
        tools: list[SyncBaseTool],
    ) -> AgentResponse:
        ...