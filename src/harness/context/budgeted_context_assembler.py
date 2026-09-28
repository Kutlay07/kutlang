from harness.context.context_section import ContextSection
from harness.context.context_telemetry import ContextTelemetry


class BudgetedContextAssembler:
    """Emits sections in priority order, stopping before the first
    section that would exceed the token budget (inclusive boundary)."""
    
    def __init__(
        self, 
        max_tokens: int, 
        telemetry: ContextTelemetry | None = None
        ):
        self.max_tokens = max_tokens
        self.telemetry = telemetry


    def assemble(
        self,
        sections: list[ContextSection]
    ) -> list[ContextSection]:
        ordered = sorted(sections, key=lambda s: s.priority)
        kept = []
        total = 0
        tokens_dropped = 0
        dropped_kinds = []

        for i, section in enumerate(ordered):
            if total + section.estimated_tokens > self.max_tokens:
                for dropped in ordered[i:]:
                    tokens_dropped += dropped.estimated_tokens
                    dropped_kinds.append(dropped.kind)
                break        # stop-on-first-overflow
            kept.append(section)
            total += section.estimated_tokens

        if self.telemetry is not None:
            self.telemetry.record({
                "sections_in": len(ordered),
                "sections_kept": len(kept),
                "tokens_kept": total,
                "tokens_dropped": tokens_dropped,
                "dropped_kinds": dropped_kinds,
            })

        return kept