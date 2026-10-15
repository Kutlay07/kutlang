from collections.abc import Sequence
import json

from harness.context.context_section import ContextSection, Section
from harness.tools.base_tool import BaseTool
from harness.context.token_estimator import estimate_tokens


class ToolDefinitionSectionProducer:

    def produce(
        self,
        tools: Sequence[BaseTool]
    ) -> ContextSection | None:
        if not tools:
            return None

        tool_dict = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters}
            for tool in tools
        ]

        content = json.dumps(tool_dict, sort_keys=True, ensure_ascii=False)
        estimated_tokens = estimate_tokens(content)

        return Section(
            kind="tool_definitions",
            priority=10,
            content=content,
            estimated_tokens=estimated_tokens,
        )
