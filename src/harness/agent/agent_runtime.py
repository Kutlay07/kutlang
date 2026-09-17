from datetime import datetime, timezone
import logging

from harness.agent.agent_response import AgentResponse
from harness.agent.tool_result import ToolResult
from harness.llm.base_llm import BaseLLM
from harness.llm.message import Message
from harness.observability.approval_audit_data import ApprovalAuditData
from harness.observability.approval_requested_audit_data import (
    ApprovalRequestedAuditData,
)
from harness.observability.audit_approval_result import AuditApprovalResult
from harness.observability.audit_approval_scope import AuditApprovalScope
from harness.observability.audit_emitter import AuditEmitter
from harness.observability.audit_event import AuditEvent
from harness.observability.audit_event_type import AuditEventType
from harness.observability.audit_outcome import AuditOutcome
from harness.observability.audit_policy_risk_level import AuditPolicyRiskLevel
from harness.observability.policy_audit_data import PolicyAuditData
from harness.observability.tool_completion_audit_data import (
    ToolCompletionAuditData,
)
from harness.observability.tool_failure_audit_data import ToolFailureAuditData
from harness.observability.tool_invocation_audit_data import (
    ToolInvocationAuditData,
)
from harness.policy.approval_broker import ApprovalBroker
from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_result import ApprovalResult
from harness.policy.policy_context import PolicyContext
from harness.policy.policy_decision import PolicyDecision
from harness.policy.policy_engine import PolicyEngine
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest
from harness.tools.tool_registry import ToolRegistry
from harness.tools.async_base_tool import AsyncBaseTool
from harness.tools.sync_base_tool import SyncBaseTool


logger = logging.getLogger(__name__)


class AgentRuntime:
    def __init__(
        self,
        llm: BaseLLM,
        tools: ToolRegistry,
        policy_engine: PolicyEngine,
        approval_broker: ApprovalBroker,
        audit_emitter: AuditEmitter,
        max_iterations: int = 10,
    ):
        self.llm = llm
        self.tools = tools
        self.max_iterations = max_iterations
        self.policy_engine = policy_engine
        self.approval_broker = approval_broker
        self.audit_emitter = audit_emitter


    async def run(self, prompt: str) -> AgentResponse:
        conversation = [
            Message(
                role="user",
                content=prompt,
            )
        ]
        
        for _ in range(self.max_iterations):
            response = self.llm.generate(
                conversation.copy(),
                self.tools.tools,
            )
            
            if not response.tool_calls:
                return response
            
            results = await self._execute_tool_calls(response)
            
            if response.text:
                conversation.append(
                    Message(
                        role="assistant",
                        content=response.text,
                    )
                )
                
            conversation.extend(response.tool_calls)
            conversation.extend(results)
            
        raise RuntimeError("Maximum agent iterations exceeded")


    async def _execute_tool_calls(
        self,
        response: AgentResponse,
    ) -> list[ToolResult]:
        results = []
        
        for tool_call in response.tool_calls or []:
            tool_execution_request = ToolExecutionRequest(
                tool_name=tool_call.name,
                arguments=ToolArguments(tool_call.arguments),
            )
            
            try:
                registration = self.tools.get_registration(tool_call.name)
            except KeyError:
                result = self._create_tool_failure_result(
                    tool_call,
                    reason=f"Unknown tool: {tool_call.name}",
                )
                results.append(result)
                continue
            
            policy_context = PolicyContext(
                request=tool_execution_request,
                trust_level=registration.trust_level,
            )
            
            try:
                evaluation = self.policy_engine.evaluate(policy_context)
            except Exception as exc:
                result = self._create_tool_failure_result(
                    tool_call,
                    reason=f"Policy evaluation failed: {exc}",
                )
                results.append(result)
                continue
            
            try:
                self._emit_policy_evaluation_audit(
                    tool_call,
                    evaluation,
                )
            except Exception:
                logger.exception("Failed to emit audit event")
                
            if evaluation.decision == PolicyDecision.ALLOW:
                result = await self._execute_tool_call(tool_call)
                results.append(result)
                
            elif evaluation.decision == PolicyDecision.ASK:
                approval_request = ApprovalRequest(
                    tool_execution_request=tool_execution_request,
                    risk_level=evaluation.risk_level,
                    scope=evaluation.approval_scope,
                )
                
                try:
                    self._emit_approval_requested_audit(
                        tool_call,
                        approval_request,
                    )
                except Exception:
                    logger.exception("Failed to emit audit event")
                    
                approval_result = (
                    await self.approval_broker.request_approval(
                        approval_request
                    )
                )
                
                try:
                    self._emit_approval_completed_audit(
                        tool_call,
                        approval_result,
                        approval_request,
                    )
                except Exception:
                    logger.exception("Failed to emit audit event")
                    
                if approval_result == ApprovalResult.GRANTED:
                    result = await self._execute_tool_call(tool_call)
                    results.append(result)
                    
                elif approval_result == ApprovalResult.REJECTED:
                    result = self._create_tool_failure_result(
                        tool_call,
                        reason="Tool execution rejected by user.",
                    )
                    results.append(result)
                    
                elif approval_result == ApprovalResult.EXPIRED:
                    result = self._create_tool_failure_result(
                        tool_call,
                        reason="Tool execution approval expired.",
                    )
                    results.append(result)
                    
                elif approval_result == ApprovalResult.CANCELED:
                    result = self._create_tool_failure_result(
                        tool_call,
                        reason="Tool execution approval cancelled by user.",
                    )
                    results.append(result)
                    
            elif evaluation.decision == PolicyDecision.DENY:
                result = self._create_tool_failure_result(
                    tool_call,
                    reason="Tool execution denied by policy.",
                )
                results.append(result)
                
        return results


    async def _execute_tool_call(
        self,
        tool_call,
    ) -> ToolResult:
        try:
            audit_event = AuditEvent(
                event_type=AuditEventType.TOOL_INVOKED,
                timestamp=datetime.now(timezone.utc),
                tool_call_id=tool_call.call_id,
                tool_name=tool_call.name,
                outcome=AuditOutcome.PENDING,
                payload=ToolInvocationAuditData(
                    arguments=tool_call.arguments,
                ),
            )
            
            self.audit_emitter.emit(audit_event)
            
        except Exception:
            logger.exception("Failed to emit audit event")
            
        try:
            tool = self.tools.get(tool_call.name)

            if isinstance(tool, AsyncBaseTool):
                result = await tool.execute(**tool_call.arguments)
            elif isinstance(tool, SyncBaseTool):
                result = tool.execute(**tool_call.arguments)
            else:
                raise TypeError(
                    f"Tool '{tool_call.name}' does not implement a supported tool contract."
                )

            is_error = False
            
            try:
                audit_event = AuditEvent(
                    event_type=AuditEventType.TOOL_COMPLETED,
                    timestamp=datetime.now(timezone.utc),
                    tool_call_id=tool_call.call_id,
                    tool_name=tool_call.name,
                    outcome=AuditOutcome.SUCCESS,
                    payload=ToolCompletionAuditData(
                        result=result,
                    ),
                )
                
                self.audit_emitter.emit(audit_event)
                
            except Exception:
                logger.exception("Failed to emit audit event")
                
        except Exception as exc:
            result = str(exc)
            is_error = True
            
            try:
                audit_event = AuditEvent(
                    event_type=AuditEventType.TOOL_FAILED,
                    timestamp=datetime.now(timezone.utc),
                    tool_call_id=tool_call.call_id,
                    tool_name=tool_call.name,
                    outcome=AuditOutcome.FAILURE,
                    payload=ToolFailureAuditData(
                        arguments=tool_call.arguments,
                        error=str(exc),
                    ),
                )
                
                self.audit_emitter.emit(audit_event)
                
            except Exception:
                logger.exception("Failed to emit audit event")
                
        return ToolResult(
            call_id=tool_call.call_id,
            tool_name=tool_call.name,
            result=result,
            is_error=is_error,
        )


    def _create_tool_failure_result(
        self,
        tool_call,
        reason,
    ) -> ToolResult:
        return ToolResult(
            call_id=tool_call.call_id,
            tool_name=tool_call.name,
            result=reason,
            is_error=True,
        )


    def _emit_policy_evaluation_audit(
        self,
        tool_call,
        evaluation,
    ):
        policy_audit_data = PolicyAuditData(
            decision=evaluation.decision,
            risk_level=evaluation.risk_level,
        )
        
        audit_event = AuditEvent(
            event_type=AuditEventType.POLICY_EVALUATED,
            timestamp=datetime.now(timezone.utc),
            tool_call_id=tool_call.call_id,
            tool_name=tool_call.name,
            outcome=AuditOutcome.SUCCESS,
            payload=policy_audit_data,
        )
        
        self.audit_emitter.emit(audit_event)


    def _emit_approval_requested_audit(
        self,
        tool_call,
        approval_request,
    ):
        approval_audit_data = ApprovalRequestedAuditData(
            risk_level=AuditPolicyRiskLevel(
                approval_request.risk_level.value
            ),
            scope=AuditApprovalScope(
                approval_request.scope.value
            ),
        )
        
        audit_event = AuditEvent(
            event_type=AuditEventType.APPROVAL_REQUESTED,
            timestamp=datetime.now(timezone.utc),
            tool_call_id=tool_call.call_id,
            tool_name=tool_call.name,
            outcome=AuditOutcome.PENDING,
            payload=approval_audit_data,
        )
        
        self.audit_emitter.emit(audit_event)


    def _emit_approval_completed_audit(
        self,
        tool_call,
        approval_result,
        approval_request,
    ):
        audit_approval_result = AuditApprovalResult(
            approval_result.value
        )
        
        if audit_approval_result == AuditApprovalResult.GRANTED:
            audit_outcome = AuditOutcome.APPROVED
        elif audit_approval_result == AuditApprovalResult.REJECTED:
            audit_outcome = AuditOutcome.DENIED
        elif audit_approval_result in (
            AuditApprovalResult.EXPIRED,
            AuditApprovalResult.CANCELED,
        ):
            audit_outcome = AuditOutcome.FAILURE
            
        approval_audit_data = ApprovalAuditData(
            risk_level=AuditPolicyRiskLevel(
                approval_request.risk_level.value
            ),
            scope=AuditApprovalScope(
                approval_request.scope.value
            ),
            result=audit_approval_result,
        )
        
        audit_event = AuditEvent(
            event_type=AuditEventType.APPROVAL_COMPLETED,
            timestamp=datetime.now(timezone.utc),
            tool_call_id=tool_call.call_id,
            tool_name=tool_call.name,
            outcome=audit_outcome,
            payload=approval_audit_data,
        )
        
        self.audit_emitter.emit(audit_event)