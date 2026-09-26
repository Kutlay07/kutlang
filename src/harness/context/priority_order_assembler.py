from harness.context.context_assembler import ContextAssembler
from harness.context.context_section import ContextSection


class PriorityOrderAssembler(ContextAssembler):
    """Trivial default: emits sections ordered by priority (ascending)."""

    def assemble(
        self,
        sections: list[ContextSection]
    ) -> list[ContextSection]:
        return sorted(sections, key=lambda s: s.priority)