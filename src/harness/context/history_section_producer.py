import json
import unicodedata
from collections.abc import Sequence

from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.context.context_section import ContextSection, Section
from harness.llm.base_llm import ConversationItem
from harness.llm.message import Message


class HistorySectionProducer:
    def produce(
        self, 
        conversation: Sequence[ConversationItem]
    ) -> ContextSection | None:
        if not conversation:
            return None

        content = "\n".join(
            self._serialize_item(item)
            for item in conversation)

        estimated_tokens = self._estimate_tokens(content)

        return Section(
            kind="history",
            priority=90,
            content=content,
            estimated_tokens=estimated_tokens,
        )


    def _serialize_item(self, item: ConversationItem) -> str:
        if isinstance(item, Message):
            return f"{item.role}: {item.content}"

        if isinstance(item, ToolCall):
            return "tool_call: " + item.name + " " + json.dumps(item.arguments, sort_keys=True)

        if isinstance(item, ToolResult):
            if item.is_error:
                return f"tool_result_error: {item.tool_name} -> {item.result}"
            else:
                return f"tool_result: {item.tool_name} -> {item.result}"

        raise TypeError("Unsupported conversation item type")


    def _estimate_tokens(self, content: str) -> int:
        wide = sum(unicodedata.east_asian_width(ch) in ("W", "F") for ch in content)
    
        narrow = len(content) - wide
        return max(1, narrow // 4 + wide)