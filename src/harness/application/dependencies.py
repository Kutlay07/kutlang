from fastapi import Depends

from harness.agent.agent_runtime import AgentRuntime
from harness.config.settings import Settings
from harness.llm.base_llm import BaseLLM
from harness.llm.local import LocalLLM
from harness.policy.approval_broker import ApprovalBroker
from harness.policy.approval_handler import ApprovalHandler
from harness.policy.default_approval_broker import DefaultApprovalBroker
from harness.policy.default_approval_handler import DefaultApprovalHandler
from harness.policy.policy_engine import PolicyEngine
from harness.policy.risk_classifier import RiskClassifier
from harness.tools.entry_point_tool_discovery import EntryPointToolDiscovery
from harness.tools.tool_registry import ToolRegistry
from harness.security.workspace_path_guard import WorkspacePathGuard
from harness.tools.filesystem.provider import FilesystemToolProvider
from harness.policy.default_policy_engine import DefaultPolicyEngine
from harness.policy.default_risk_classifier import DefaultRiskClassifier


def get_settings() -> Settings:
    return Settings()


def get_llm(settings: Settings = Depends(get_settings)) -> BaseLLM:
    return LocalLLM(
        base_url=settings.local_llm_base_url,
        model=settings.local_llm_model,
    )


def get_tool_registry(
    settings: Settings = Depends(get_settings),
    ) -> ToolRegistry:
    
    boundary = WorkspacePathGuard(settings.workspace_root)
    
    discovery = EntryPointToolDiscovery()
    provider_classes = discovery.discover()
    
    providers = []
    
    for provider_class in provider_classes:
        if issubclass(provider_class, FilesystemToolProvider):
            providers.append(provider_class(boundary))
        else:
            providers.append(provider_class())
            
    tools = [
        tool
        for provider in providers
        for tool in provider.get_tools()
    ]
    
    return ToolRegistry(tools)


def get_risk_classifier() -> RiskClassifier:
    return DefaultRiskClassifier()


def get_policy_engine(
    risk_classifier: RiskClassifier = Depends(get_risk_classifier),
    ) -> PolicyEngine:
    return DefaultPolicyEngine(risk_classifier)


def get_approval_handler() -> ApprovalHandler:
    return DefaultApprovalHandler()


def get_approval_broker(
    handler: ApprovalHandler = Depends(get_approval_handler),
    ) -> ApprovalBroker:
    return DefaultApprovalBroker(handler)


def get_agent_runtime(
    llm: BaseLLM = Depends(get_llm),
    registry: ToolRegistry = Depends(get_tool_registry),
    policy_engine: PolicyEngine = Depends(get_policy_engine),
    approval_broker: ApprovalBroker = Depends(get_approval_broker),
    settings: Settings = Depends(get_settings),
) -> AgentRuntime:
    return AgentRuntime(
        llm=llm,
        tools=registry,
        policy_engine=policy_engine,
        approval_broker=approval_broker,
        max_iterations=settings.max_iterations,
    )