from dataclasses import dataclass

from harness.context.budgeted_context_assembler import BudgetedContextAssembler


@dataclass
class FakeSection:
    kind: str
    content: str
    priority: int
    estimated_tokens: int


def test_assembler_returns_all_sections_when_within_budget():
    assembler = BudgetedContextAssembler(max_tokens=800)

    sections = [
        FakeSection(kind="system", content="low", priority=10, estimated_tokens=300),
        FakeSection(kind="task", content="mid", priority=20, estimated_tokens=300),
        FakeSection(kind="tool_result", content="high", priority=30, estimated_tokens=200),
    ]

    result = assembler.assemble(sections)

    assert [s.content for s in result] == ["low", "mid", "high"]


def test_assembler_stops_at_first_section_exceeding_budget():
    assembler = BudgetedContextAssembler(max_tokens=800)

    sections = [
        FakeSection(kind="system", content="first", priority=10, estimated_tokens=500),
        FakeSection(kind="task", content="second", priority=20, estimated_tokens=400),
    ]

    result = assembler.assemble(sections)

    assert [s.content for s in result] == ["first"]


def test_assembler_includes_sections_when_cumulative_tokens_equal_budget():
    assembler = BudgetedContextAssembler(max_tokens=800)

    sections = [
        FakeSection(kind="system", content="first", priority=10, estimated_tokens=500),
        FakeSection(kind="task", content="second", priority=20, estimated_tokens=300),
    ]

    result = assembler.assemble(sections)

    assert [s.content for s in result] == ["first", "second"]


def test_assembler_returns_empty_list_when_single_section_exceeds_budget():
    assembler = BudgetedContextAssembler(max_tokens=100)

    sections = [
        FakeSection(kind="system", content="huge", priority=10, estimated_tokens=500)
    ]

    result = assembler.assemble(sections)

    assert result == []