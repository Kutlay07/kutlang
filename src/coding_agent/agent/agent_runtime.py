from coding_agent.agent.agent_response import AgentResponse
from coding_agent.agent.tool_result import ToolResult
from coding_agent.llm.base_llm import BaseLLM
from coding_agent.llm.message import Message
from coding_agent.tools.tool_registry import ToolRegistry


class AgentRuntime:
    def __init__(
        self,
        llm: BaseLLM,
        tools: ToolRegistry,
        max_iterations: int = 10,
    ):
        self.llm = llm
        self.tools = tools
        self.max_iterations = max_iterations

    def run(self, prompt: str) -> AgentResponse:
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

            results = self._execute_tool_calls(response)

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

    def _execute_tool_calls(
        self,
        response: AgentResponse,
    ) -> list[ToolResult]:
        results = []

        for tool_call in response.tool_calls or []:
            try:
                tool = self.tools.get(tool_call.name)
                result = tool.execute(**tool_call.arguments)

                is_error = False

            except Exception as exc:
                result = str(exc)
                is_error = True

            results.append(
                ToolResult(
                    call_id=tool_call.call_id,
                    tool_name=tool_call.name,
                    result=result,
                    is_error=is_error,
                )
            )

        return results