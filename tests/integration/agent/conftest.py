from unittest.mock import MagicMock

import pytest

from harness.llm.base_llm import BaseLLM
from harness.observability.audit_emitter import AuditEmitter
from harness.policy.approval_broker import ApprovalBroker
from harness.policy.policy_engine import PolicyEngine


@pytest.fixture
def llm():
    return MagicMock(spec=BaseLLM)

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
        self.result = None

    def assemble(self, sections):
        self.calls.append(sections)
        return self.result if self.result is not None else sections

@pytest.fixture
def context_assembler():
    return FakeAssembler()

class FakeHistoryProducer:
    def __init__(self, section=None):
        self.calls = []
        self.section = section

    def produce(self, conversation):
        self.calls.append(conversation)
        return self.section

@pytest.fixture
def history_producer():
    return FakeHistoryProducer()