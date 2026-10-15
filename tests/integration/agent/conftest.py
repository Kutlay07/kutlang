from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from harness.context.tool_section_producer import ToolSectionProducer
from harness.llm.base_llm import BaseLLM
from harness.observability.audit_emitter import AuditEmitter
from harness.policy.approval_broker import ApprovalBroker
from harness.policy.policy_engine import PolicyEngine
from harness.tools.tool_registry import ToolRegistry


@pytest.fixture
def llm():
    return MagicMock(spec=BaseLLM)

@pytest.fixture
def tools():
    return MagicMock(spec=ToolRegistry)

@pytest.fixture
def policy_engine():
    return MagicMock(spec=PolicyEngine)

@pytest.fixture
def approval_broker():
    return MagicMock(spec=ApprovalBroker)

@pytest.fixture
def audit_emitter():
    return MagicMock(spec=AuditEmitter)

class FakeAssembler:
    def __init__(self):
        self.calls = []
        self.responses = []
        self.result = None

    def assemble(self, sections):
        self.calls.append(sections)
        if self.responses:
            first = self.responses.pop(0)
            return first
        return self.result if self.result is not None else sections

@pytest.fixture
def context_assembler():
    return FakeAssembler()

@dataclass
class FakeSection:
    kind: str
    content: str
    priority: int
    estimated_tokens: int

class FakeHistoryProducer:
    def __init__(self, section=FakeSection(
        kind="history",
        content="content",
        priority=90,
        estimated_tokens=1,
        )
    ):
        self.calls = []
        self.section = section

    def produce(self, conversation):
        self.calls.append(list(conversation))
        return self.section

@pytest.fixture
def history_producer():
    return FakeHistoryProducer()

@pytest.fixture
def tool_section_producer():
    producer = MagicMock(spec=ToolSectionProducer)
    producer.produce.return_value = None
    return producer
