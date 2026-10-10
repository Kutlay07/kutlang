import pytest
from unittest.mock import MagicMock

from harness.agent.agent_response import AgentResponse
from harness.agent.agent_runtime import AgentRuntime
from harness.agent.tool_call import ToolCall
from harness.llm.base_llm import BaseLLM
from harness.observability.audit_emitter import AuditEmitter
from harness.policy.approval_broker import ApprovalBroker
from harness.policy.policy_decision import PolicyDecision
from harness.policy.policy_engine import PolicyEngine
from harness.policy.policy_evaluation import PolicyEvaluation
from harness.policy.risk_level import RiskLevel
from harness.policy.trust_level import TrustLevel
from harness.tools.filesystem.read_file import ReadFileTool
from harness.tools.output_budget import OutputBudget
from harness.tools.tool_registration import ToolRegistration
from harness.tools.tool_registry import ToolRegistry
from harness.security.workspace_path_guard import WorkspacePathGuard


@pytest.mark.asyncio
async def test_agent_runtime_reads_file_with_real_tool(
    tmp_path,
    llm,
    policy_engine, 
    approval_broker,
    audit_emitter,
    context_assembler,
    history_producer,
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
    output_budget = OutputBudget(max_chars=20_000)

    tools = ToolRegistry([
        ToolRegistration(
            tool=ReadFileTool(workspace_boundary, output_budget),
            trust_level=TrustLevel.TRUSTED,
        )
    ])

    runtime = AgentRuntime(
        llm, 
        tools,
        policy_engine, 
        approval_broker,
        audit_emitter,
        context_assembler,
        history_producer,
        )

    result = await runtime.run("Read the file")
    second_conversation = llm.generate.call_args_list[1].args[0]
    tool_result = second_conversation[-1]

    assert result.text == "The file says: Hello from file"
    assert llm.generate.call_count == 2
    assert tool_result.call_id == "call_123"
    assert tool_result.tool_name == "read_file"
    assert tool_result.result == "Hello from file"
    assert tool_result.is_error is False