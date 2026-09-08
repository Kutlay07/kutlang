from harness.agent.agent_response import AgentResponse
from harness.agent.tool_result import ToolResult
from harness.llm.base_llm import BaseLLM
from harness.llm.message import Message
from harness.policy.approval_broker import ApprovalBroker
from harness.policy.approval_result import ApprovalResult
from harness.policy.policy_context import PolicyContext
from harness.policy.policy_decision import PolicyDecision
from harness.policy.approval_request import ApprovalRequest
from harness.policy.policy_engine import PolicyEngine
from harness.policy.tool_execution_request import ToolExecutionRequest
from harness.tools.tool_registry import ToolRegistry


class AgentRuntime:
    def __init__(
        self,
        llm: BaseLLM,
        tools: ToolRegistry,
        policy_engine: PolicyEngine,
        approval_broker: ApprovalBroker,
        max_iterations: int = 10,
    ):
        self.llm = llm
        self.tools = tools
        self.max_iterations = max_iterations
        self.policy_engine = policy_engine
        self.approval_broker = approval_broker


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
                arguments=tool_call.arguments,
            )
            
            policy_context = PolicyContext(
                request=tool_execution_request
            )
            
            evaluation = self.policy_engine.evaluate(policy_context)
            
            if evaluation.decision == PolicyDecision.ALLOW:
                result = self._execute_tool_call(tool_call)
                results.append(result)
                
            elif evaluation.decision == PolicyDecision.ASK:
                approval_request = ApprovalRequest(
                    tool_execution_request=tool_execution_request,
                    risk_level=evaluation.risk_level,
                    scope=evaluation.approval_scope,
                )
                approval_result = await self.approval_broker.request_approval(
                    approval_request
                )
                
                if approval_result == ApprovalResult.GRANTED:
                    result = self._execute_tool_call(tool_call)
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


    def _execute_tool_call(
        self,
        tool_call,
    ) -> ToolResult: 
        
        try:
            tool = self.tools.get(tool_call.name)
            result = tool.execute(**tool_call.arguments)
            is_error = False
            
        except Exception as exc:
            result = str(exc)
            is_error = True
            
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