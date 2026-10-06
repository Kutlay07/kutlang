from collections.abc import Sequence
from typing import Protocol

from harness.context.context_section import ContextSection
from harness.llm.base_llm import ConversationItem


class ConversationSectionProducer(Protocol):
    def produce(
        self, 
        conversation: Sequence[ConversationItem]
    ) -> ContextSection | None:
        ...