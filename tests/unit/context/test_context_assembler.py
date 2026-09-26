from dataclasses import dataclass

from harness.context.context_assembler import ContextAssembler
from harness.context.priority_order_assembler import PriorityOrderAssembler


@dataclass
class FakeSection:
    kind: str
    content: str
    priority: int
    estimated_tokens: int

def test_assembler_orders_section_by_priority():
    assembler = PriorityOrderAssembler()

    section1 = FakeSection(
        kind="kind123",
        content="low",
        priority=10,
        estimated_tokens=500,
    )
    section2 = FakeSection(
        kind="kind123",
        content="mid",
        priority=20,
        estimated_tokens=500,
    )
    section3 = FakeSection(
        kind="kind123",
        content="high",
        priority=30,
        estimated_tokens=500,
    )

    result = assembler.assemble([section1, section2, section3])

    assert [s.content for s in result] == ["low", "mid", "high"]


def test_assembler_preserves_input_order_for_equal_priorities():
    assembler = PriorityOrderAssembler()

    section1 = FakeSection(
        kind="kind123",
        content="something",
        priority=10,
        estimated_tokens=500,
    )
    section2 = FakeSection(
        kind="kind123",
        content="anything",
        priority=10,
        estimated_tokens=500,
    )

    result = assembler.assemble([section1, section2])

    assert [s.content for s in result] == ["something", "anything"]