import pytest
from unittest.mock import MagicMock

from harness.agent.agent_response import AgentResponse
from harness.agent.agent_runtime import AgentRuntime
from harness.agent.tool_call import ToolCall
from harness.llm.base_llm import BaseLLM
from harness.policy.approval_broker import ApprovalBroker
from harness.policy.policy_decision import PolicyDecision
from harness.policy.policy_engine import PolicyEngine
from harness.policy.policy_evaluation import PolicyEvaluation
from harness.policy.risk_level import RiskLevel
from harness.tools.filesystem.read_file import ReadFileTool
from harness.tools.tool_registry import ToolRegistry
from harness.security.workspace_path_guard import WorkspacePathGuard

@pytest.fixture
def llm():
    return MagicMock(spec=BaseLLM)
@pytest.fixture
def policy_engine():
    return MagicMock(spec=PolicyEngine)

@pytest.fixture
def approval_broker():
    return MagicMock(spec=ApprovalBroker)


@pytest.mark.asyncio
async def test_agent_runtime_reads_file_with_real_tool(
    tmp_path,
    llm,
    policy_engine, 
    approval_broker,
    ):
    
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        risk_level=RiskLevel.LOW,
    )
    
    file = tmp_path / "test.txt"
    file.write_text("Hello from file", encoding="utf-8")

    llm.generate.side_effect = [
        AgentResponse(
            tool_calls=[
                ToolCall(
                    call_id="call_123",
                    name="read_file",
                    arguments={"path": str(file)},
                )
            ]
        ),
        AgentResponse(text="The file says: Hello from file"),
    ]

    workspace_boundary = WorkspacePathGuard(tmp_path)
    tools = ToolRegistry([ReadFileTool(workspace_boundary)])
    runtime = AgentRuntime(
        llm, 
        tools,
        policy_engine, 
        approval_broker,
        )

    result = await runtime.run("Read the file")

    assert result.text == "The file says: Hello from file"
    assert llm.generate.call_count == 2