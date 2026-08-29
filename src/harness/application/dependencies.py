from fastapi import Depends

from harness.agent.agent_runtime import AgentRuntime
from harness.config.settings import Settings
from harness.llm.base_llm import BaseLLM
from harness.llm.local import LocalLLM
from harness.tools.entry_point_tool_discovery import EntryPointToolDiscovery
from harness.tools.tool_registry import ToolRegistry


def get_settings() -> Settings:
    return Settings()


def get_llm(settings: Settings = Depends(get_settings)) -> BaseLLM:
    return LocalLLM(
        base_url=settings.local_llm_base_url,
        model=settings.local_llm_model,
    )


def get_tool_registry() -> ToolRegistry:
    discovery = EntryPointToolDiscovery()
    providers = discovery.discover()

    tools = [
        tool
        for provider in providers
        for tool in provider.get_tools()
    ]

    return ToolRegistry(tools)


def get_agent_runtime(
    llm: BaseLLM = Depends(get_llm),
    registry: ToolRegistry = Depends(get_tool_registry),
    settings: Settings = Depends(get_settings),
) -> AgentRuntime:
    return AgentRuntime(
        llm=llm,
        tools=registry,
        max_iterations=settings.max_iterations,
    )