import pytest

from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.context.history_section_producer import HistorySectionProducer
from harness.llm.message import Message


@pytest.fixture
def producer():
    return HistorySectionProducer()

def test_producer_builds_history_section_from_conversation(producer):
    conversation = [
        Message(role="user", content="Read main.py"),
        Message(role="assistant", content="I will read the file"),
    ]

    section = producer.produce(conversation)

    assert section.kind == "history"
    assert "Read main.py" in section.content
    assert "I will read the file" in section.content
    assert section.estimated_tokens > 0
    assert section.priority == 90


def test_producer_returns_none_for_empty_conversation(producer):
    conversation = []

    section = producer.produce(conversation)

    assert section is None


def test_producer_serializes_mixed_conversation(producer):
    conversation = [
        Message(role="user", content="Read main.py"), 
        ToolCall(call_id="call_123", name="read_file", arguments={"path": "main.py"}),
        ToolResult(call_id="call_123", tool_name="read_file", result="file contents", is_error=False)
    ]

    section = producer.produce(conversation)
    
    assert section.content.splitlines() == [
        "user: Read main.py",
        'tool_call: read_file {"path": "main.py"}',
        "tool_result: read_file -> file contents",
        ]


def test_producer_serializes_error_tool_result(producer):
    conversation = [
        ToolResult(call_id="call_123", tool_name="read_file", result="permission denied", is_error=True)
    ]

    section = producer.produce(conversation)

    assert section.content == "tool_result_error: read_file -> permission denied"


def test_producer_token_estimate(producer):
    conversation = [
        Message(role="user", content="Hello from world")
    ]
    
    section = producer.produce(conversation)
    
    assert section.estimated_tokens == max(1, len(section.content) // 4)


def test_producer_handles_cjk_undercount(producer):
    conversation = [
        Message(role="user", content="这是测试" * 50)
    ]
    
    section = producer.produce(conversation)
    
    assert section.estimated_tokens >= 200