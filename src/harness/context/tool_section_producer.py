from collections.abc import Sequence
from typing import Protocol

from harness.context.context_section import ContextSection
from harness.tools.base_tool import BaseTool


class ToolSectionProducer(Protocol):
    def produce(
        self,
        tools: Sequence[BaseTool],
    ) -> ContextSection | None:
        ...
