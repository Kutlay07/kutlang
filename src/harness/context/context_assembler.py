from typing import Protocol

from harness.context.context_section import ContextSection


class ContextAssembler(Protocol):
    def assemble(
        self,
        sections: list[ContextSection]
    ) -> list[ContextSection]:
        ...