import pytest
import asyncio
from unittest.mock import MagicMock

from harness.agent.agent_response import AgentResponse
from harness.agent.agent_runtime import AgentRuntime
from harness.llm.base_llm import BaseLLM
from harness.policy.approval_broker import ApprovalBroker
from harness.policy.approval_result import ApprovalResult
from harness.policy.approval_scope import ApprovalScope
from harness.policy.policy_decision import PolicyDecision
from harness.policy.policy_engine import PolicyEngine
from harness.policy.policy_evaluation import PolicyEvaluation
from harness.policy.risk_level import RiskLevel
from harness.tools.tool_registry import ToolRegistry
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.llm.message import Message
from harness.tools.base_tool import BaseTool
from harness.tools.execution.run_command import RunCommandTool
from harness.tools.execution.process_manager import ProcessManager
from harness.tools.execution.run_background_command import (
    RunBackgroundCommandTool,
)
from harness.tools.execution.get_process_output import (
    GetProcessOutputTool,
)
from harness.tools.execution.kill_process import KillProcessTool


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
def runtime(llm, tools, policy_engine, approval_broker):
    return AgentRuntime(
        llm,
        tools,
        policy_engine,
        approval_broker,
    )


def test_runtime_initializes_with_llm_and_tools(runtime, llm, tools):
    assert runtime.llm is llm
    assert runtime.tools is tools


@pytest.mark.asyncio
async def test_runtime_runs_llm(runtime, llm, tools):
    tool = MagicMock(spec=BaseTool)
    tool.name = "read_file"
    
    tools.tools = [tool]

    response = AgentResponse(text="Hello world")
    llm.generate.return_value = response

    result = await runtime.run("Hello")

    llm.generate.assert_called_once_with(
        [
            Message(
                role="user",
                content="Hello",
            )
        ],
        [tool],
    )
    
    assert result is response


@pytest.mark.asyncio
async def test_runtime_executes_tool_calls(
    llm,
    tools,
    policy_engine, 
    approval_broker,
    runtime
    ):

    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool

    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        risk_level=RiskLevel.LOW,
    )
    
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="Done"),
    ]

    result = await runtime.run("Read main.py")

    tools.get.assert_called_once_with("read_file")
    tool.execute.assert_called_once_with(path="main.py")
    assert result.text == "Done"


@pytest.mark.asyncio
async def test_runtime_sends_too_result_back_to_llm(
    runtime, 
    llm, 
    tools, 
    policy_engine
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        risk_level=RiskLevel.LOW,
    )

    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    first_response = AgentResponse(
        tool_calls=[tool_call],
    )

    final_response = AgentResponse(
        text="Here is the file.",
    )

    llm.generate.side_effect = [
        first_response,
        final_response,
    ]

    result = await runtime.run("Read main.py")

    assert result is final_response

    assert llm.generate.call_count == 2

    calls = llm.generate.call_args_list

    assert calls[1].args[0] == [
        Message(
            role="user",
            content="Read main.py",
        ),
        tool_call,
        ToolResult(
            call_id="call_123",
            tool_name="read_file",
            result="file contents",
        ),
    ]


@pytest.mark.asyncio
async def test_runtime_supports_multiple_tool_iterations(
    runtime,
    llm, 
    tools,
    policy_engine,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
    decision=PolicyDecision.ALLOW,
    risk_level=RiskLevel.LOW,
    )
    
    tool = MagicMock()
    tool.execute.side_effect = [
        "first result",
        "second result",
    ]
    tools.get.return_value = tool

    first_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "first.py"},
    )

    second_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "second.py"},
    )

    first_response = AgentResponse(tool_calls=[first_call])
    second_response = AgentResponse(tool_calls=[second_call])
    final_response = AgentResponse(text="Done")

    llm.generate.side_effect = [
        first_response,
        second_response,
        final_response,
    ]

    result = await runtime.run("Do the task")

    assert result is final_response
    assert llm.generate.call_count == 3
    assert tool.execute.call_count == 2


@pytest.mark.asyncio
async def test_runtime_raises_when_max_iterations_exceeded(
    llm, 
    tools,
    policy_engine,
    approval_broker,
    ):

    tool = MagicMock()
    tool.execute.return_value = "result"
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "test.py"},
    )

    llm.generate.return_value = AgentResponse(
        tool_calls=[tool_call],
    )

    runtime = AgentRuntime(
        llm,
        tools,
        policy_engine,
        approval_broker,
        max_iterations=2,
    )

    with pytest.raises(RuntimeError, match="Maximum agent iterations exceeded"):
        await runtime.run("Keep going")

    assert llm.generate.call_count == 2


@pytest.mark.asyncio
async def test_runtime_returns_tool_error_as_tool_result(
    runtime, 
    llm,
    tools,
    policy_engine,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        risk_level=RiskLevel.LOW,
)

    tool = MagicMock()
    tool.execute.side_effect = FileNotFoundError("File not found")
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "missing.py"},
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="I couldn't find the file."),
    ]

    result = await runtime.run("Read missing.py")

    assert result.text == "I couldn't find the file."
    tool.execute.assert_called_once_with(path="missing.py")

    second_messages = llm.generate.call_args_list[1].args[0]

    tool_result = second_messages[-1]

    assert isinstance(tool_result, ToolResult)
    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "read_file"
    assert tool_result.result == "File not found"
    assert tool_result.is_error is True



def test_tool_result_can_represent_error():
    result = ToolResult(
        call_id="call_123",
        tool_name="read_file",
        result="File not found",
        is_error=True,
    )

    assert result.call_id == "call_123"
    assert result.is_error is True


@pytest.mark.asyncio
async def test_runtime_handles_unknown_tool(
    runtime, 
    llm, 
    tools,
    policy_engine
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        risk_level=RiskLevel.LOW,
        )
    
    tools.get.side_effect = KeyError("unknown_tool")

    tool_call = ToolCall(
        call_id="call_123",
        name="unknown_tool",
        arguments={},
    )

    llm.generate.side_effect = [
        AgentResponse(tool_calls=[tool_call]),
        AgentResponse(text="I don't have that tool."),
    ]

    result = await runtime.run("Use unknown_tool")

    assert result.text == "I don't have that tool."

    second_messages = llm.generate.call_args_list[1].args[0]

    tool_result = second_messages[-1]

    assert isinstance(tool_result, ToolResult)
    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "unknown_tool"
    assert "unknown_tool" in tool_result.result
    assert tool_result.is_error is True


@pytest.mark.asyncio
async def test_runtime_formats_tool_errors_as_errors(
    runtime,
    llm, 
    tools,
    policy_engine,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        risk_level=RiskLevel.LOW,
    )
    
    tool = MagicMock()
    tool.execute.side_effect = FileNotFoundError("File not found")
    tools.get.return_value = tool

    llm.generate.side_effect = [
        AgentResponse(
            tool_calls=[
                ToolCall(
                    call_id="call_123",
                    name="read_file",
                    arguments={"path": "missing.py"},
                )
            ]
        ),
        AgentResponse(text="Done"),
    ]

    await runtime.run("Read missing.py")

    second_conversation = llm.generate.call_args_list[1].args[0]

    tool_result = second_conversation[-1]

    assert isinstance(tool_result, ToolResult)
    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "read_file"
    assert tool_result.result == "File not found"
    assert tool_result.is_error is True


@pytest.mark.asyncio
async def test_runtime_preserves_tool_call_id(
    runtime, 
    llm, 
    tools,
    policy_engine,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        risk_level=RiskLevel.LOW,
    )
    
    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )

    response = AgentResponse(
        tool_calls=[tool_call],
    )

    results = await runtime._execute_tool_calls(response)

    assert results == [
        ToolResult(
            call_id="call_123",
            tool_name="read_file",
            result="file contents",
        )
    ]


@pytest.mark.asyncio
async def test_runtime_preserves_assistant_text_with_tool_calls(
    runtime, 
    llm, 
    tools,
    policy_engine,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        risk_level=RiskLevel.LOW,
    )
    
    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool
    
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )
    
    llm.generate.side_effect = [
        AgentResponse(
            text="I will read the file first.",
            tool_calls=[tool_call],
        ),
        AgentResponse(text="Here is the file."),
    ]
    
    await runtime.run("Read main.py")
    
    second_conversation = llm.generate.call_args_list[1].args[0]
    
    assert second_conversation[0] == Message(
        role="user",
        content="Read main.py",
    )
    
    assert second_conversation[1] == Message(
        role="assistant",
        content="I will read the file first.",
    )
    
    assert second_conversation[2] == tool_call
    
    assert second_conversation[3].tool_name == "read_file"
    assert second_conversation[3].result == "file contents"


def test_execution_tools_can_be_registered_together():
    manager = ProcessManager()
    
    tools = [
        RunCommandTool(),
        RunBackgroundCommandTool(manager),
        GetProcessOutputTool(manager),
        KillProcessTool(manager),
    ]
    
    registry = ToolRegistry(tools)
    
    assert registry.get("run_command") is tools[0]
    assert registry.get("run_background_command") is tools[1]
    assert registry.get("get_process_output") is tools[2]
    assert registry.get("kill_process") is tools[3]


@pytest.mark.asyncio
async def test_runtime_does_not_execute_tool_when_approval_is_rejected(
    llm,
    tools,
    policy_engine,
    approval_broker,
    runtime,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ASK,
        risk_level=RiskLevel.HIGH,
        approval_scope=ApprovalScope.SINGLE_CALL
    )
    
    approval_broker.request_approval.return_value = ApprovalResult.REJECTED
    
    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool
    
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )
    
    runtime = AgentRuntime(
        llm,
        tools,
        policy_engine,
        approval_broker,
    )
    
    results = await runtime._execute_tool_calls(
        AgentResponse(tool_calls=[tool_call])
    )
    
    assert len(results) == 1
    assert results[0].call_id == "call_123"
    assert results[0].tool_name == "read_file"
    assert results[0].result == "Tool execution rejected by user."
    assert results[0].is_error is True
    tool.execute.assert_not_called()
    approval_broker.request_approval.assert_awaited_once()


@pytest.mark.asyncio
async def test_runtime_executes_tool_when_approval_is_granted(
    llm,
    tools,
    policy_engine,
    approval_broker,
    runtime,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ASK,
        risk_level=RiskLevel.HIGH,
        approval_scope=ApprovalScope.SINGLE_CALL
    )
    
    approval_broker.request_approval.return_value = ApprovalResult.GRANTED
    
    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool
    
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )
    
    runtime = AgentRuntime(
        llm,
        tools,
        policy_engine,
        approval_broker,
    )
    
    results = await runtime._execute_tool_calls(
        AgentResponse(tool_calls=[tool_call])
    )
    
    assert len(results) == 1
    assert results[0].call_id == "call_123"
    assert results[0].tool_name == "read_file"
    assert results[0].is_error is False
    tool.execute.assert_called_once()
    approval_broker.request_approval.assert_awaited_once()


@pytest.mark.asyncio
async def test_runtime_does_not_execute_tool_when_approval_expires(
    llm,
    tools,
    policy_engine,
    approval_broker,
    runtime,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ASK,
        risk_level=RiskLevel.HIGH,
        approval_scope=ApprovalScope.SINGLE_CALL
    )
    
    approval_broker.request_approval.return_value = ApprovalResult.EXPIRED
    
    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool
    
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )
    
    runtime = AgentRuntime(
        llm,
        tools,
        policy_engine,
        approval_broker,
    )
    
    results = await runtime._execute_tool_calls(
        AgentResponse(tool_calls=[tool_call])
    )
    
    assert len(results) == 1
    assert results[0].call_id == "call_123"
    assert results[0].tool_name == "read_file"
    assert results[0].result == "Tool execution approval expired."
    assert results[0].is_error is True
    tool.execute.assert_not_called()
    approval_broker.request_approval.assert_awaited_once()


@pytest.mark.asyncio
async def test_runtime_does_not_execute_tool_when_approval_is_canceled(
    llm,
    tools,
    policy_engine,
    approval_broker,
    runtime,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ASK,
        risk_level=RiskLevel.HIGH,
        approval_scope=ApprovalScope.SINGLE_CALL
    )
    
    approval_broker.request_approval.return_value = ApprovalResult.CANCELED
    
    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool
    
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )
    
    runtime = AgentRuntime(
        llm,
        tools,
        policy_engine,
        approval_broker,
    )
    
    results = await runtime._execute_tool_calls(
        AgentResponse(tool_calls=[tool_call])
    )
    
    assert len(results) == 1
    assert results[0].call_id == "call_123"
    assert results[0].tool_name == "read_file"
    assert results[0].result == "Tool execution approval cancelled by user."
    assert results[0].is_error is True
    tool.execute.assert_not_called()
    approval_broker.request_approval.assert_awaited_once()


@pytest.mark.asyncio
async def test_runtime_denies_tool_execution_when_policy_denies(
    llm,
    tools,
    policy_engine,
    approval_broker,
    runtime,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.DENY,
        risk_level=RiskLevel.HIGH,
        approval_scope=None,
    )
    
    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool
    
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )
    
    runtime = AgentRuntime(
        llm,
        tools,
        policy_engine,
        approval_broker,
    )
    
    results = await runtime._execute_tool_calls(
        AgentResponse(tool_calls=[tool_call])
    )
    
    assert len(results) == 1
    assert results[0].call_id == "call_123"
    assert results[0].tool_name == "read_file"
    assert results[0].result == "Tool execution denied by policy."
    assert results[0].is_error is True
    tool.execute.assert_not_called()
    approval_broker.request_approval.assert_not_awaited()


@pytest.mark.asyncio
async def test_runtime_does_not_execute_tool_while_approval_is_pending(
    llm,
    tools,
    policy_engine,
    approval_broker,
    runtime,
    ):
    
    approval_event = asyncio.Event()
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ASK,
        risk_level=RiskLevel.HIGH,
        approval_scope=ApprovalScope.SINGLE_CALL,
    )
    
    async def request_approval(approval_request):
        await approval_event.wait()
        return ApprovalResult.GRANTED
    
    approval_broker.request_approval.side_effect = request_approval
    
    tool = MagicMock()
    tool.execute.return_value = "file contents"
    tools.get.return_value = tool
    
    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"},
    )
    
    
    task = asyncio.create_task(
        runtime._execute_tool_calls(
            AgentResponse(tool_calls=[tool_call])
        )
    )
    await asyncio.sleep(0)
    tool.execute.assert_not_called()
    
    approval_event.set()
    
    results = await task
    
    assert len(results) == 1
    assert results[0].call_id == "call_123"
    assert results[0].tool_name == "read_file"
    assert results[0].is_error is False

    tool.execute.assert_called_once()
    approval_broker.request_approval.assert_awaited_once()