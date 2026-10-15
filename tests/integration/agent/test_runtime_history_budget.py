from unittest.mock import MagicMock

import pytest

from harness.agent.agent_response import AgentResponse
from harness.agent.agent_runtime import AgentRuntime
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.context.budgeted_context_assembler import BudgetedContextAssembler
from harness.context.history_section_producer import HistorySectionProducer
from harness.policy.policy_decision import PolicyDecision
from harness.policy.policy_evaluation import PolicyEvaluation
from harness.policy.risk_level import RiskLevel
from harness.tools.output_budget import OutputBudget
from harness.tools.sync_base_tool import SyncBaseTool



@pytest.mark.asyncio
async def test_runtime_keeps_oversized_tool_result_after_history_budgeting(
    llm, tools, policy_engine, approval_broker, audit_emitter, tool_section_producer,
):
    policy_engine.evaluate.return_value = PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        risk_level=RiskLevel.LOW,
    )

    context_assembler = BudgetedContextAssembler(max_tokens=8_000)

    output_budget = OutputBudget(max_chars=20_000)
    conversation_section_producer = HistorySectionProducer(output_budget=output_budget)

    tool = MagicMock(spec=SyncBaseTool)
    tool.execute.return_value = "x" * 40_000
    tools.get.return_value = tool

    tool_call = ToolCall(
        call_id="call_123",
        name="read_file",
        arguments={"path": "main.py"})

    llm.generate.side_effect = [AgentResponse(tool_calls=[tool_call]), AgentResponse(text="Done")]

    runtime = AgentRuntime(
        llm,
        tools,
        policy_engine,
        approval_broker,
        audit_emitter,
        context_assembler,
        conversation_section_producer,
        tool_section_producer,
    )

    await runtime.run("Read the file")

    assert llm.generate.call_count == 2

    second_conversation = llm.generate.call_args_list[1].args[0]
    assert second_conversation[1] == tool_call

    result = second_conversation[2]
    assert isinstance(result, ToolResult)
    assert result.call_id == "call_123"
    assert result.result == "x" * 40_000
    assert result.is_error is False
