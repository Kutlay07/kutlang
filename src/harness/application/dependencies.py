from fastapi import Depends

from ..agent.agent_runtime import AgentRuntime
from ..llm.base_llm import BaseLLM
from ..llm.openai import OpenAILLM
from ..tools.tool_registry import ToolRegistry
from config import settings



def get_llm() -> BaseLLM:
    return OpenAILLM()



def get_tool_registry() -> ToolRegistry:
    return ToolRegistry(
        
    )



def get_agent_runtime(
    llm: BaseLLM = Depends(get_llm),
    registry: ToolRegistry = Depends(get_tool_registry),
    max_iterations: int = settings.MAX_ITERATIONS,
) -> AgentRuntime:
    return AgentRuntime(llm, registry, max_iterations)