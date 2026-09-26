from harness.context.context_section import ContextSection


class ContextAssembler:
    def assemble(
        self,
        sections: list[ContextSection]
    ) -> list[ContextSection]:
        ...