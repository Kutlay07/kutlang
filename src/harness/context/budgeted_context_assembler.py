from harness.context.context_section import ContextSection


class BudgetedContextAssembler:
    """Emits sections in priority order, stopping before the first
    section that would exceed the token budget (inclusive boundary)."""
    
    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens


    def assemble(
        self,
        sections: list[ContextSection]
    ) -> list[ContextSection]:
        ordered = sorted(sections, key=lambda s: s.priority)
        kept = []
        total = 0
        
        for section in ordered:
            if total + section.estimated_tokens > self.max_tokens:
                break              # stop-on-first-overflow
            kept.append(section)
            total += section.estimated_tokens

        return kept