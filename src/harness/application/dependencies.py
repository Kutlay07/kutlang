import logging
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
from harness.security.secret_file_visibility import SecretFileVisibility
from harness.tools.entry_point_tool_discovery import EntryPointToolDiscovery
from harness.tools.output_budget import OutputBudget
from harness.tools.search.provider import SearchToolProvider
from harness.tools.tool_registry import ToolRegistry
from harness.security.workspace_path_guard import WorkspacePathGuard
from harness.tools.filesystem.provider import FilesystemToolProvider
from harness.policy.default_policy_engine import DefaultPolicyEngine
from harness.policy.default_risk_classifier import DefaultRiskClassifier
from harness.policy.trust_level import TrustLevel
from harness.tools.tool_registration import ToolRegistration
from harness.tools.execution.provider import ExecutionToolProvider
from harness.observability.audit_emitter import AuditEmitter
from harness.observability.logging_audit_emitter import LoggingAuditEmitter
from harness.observability.redaction.default_entropy_detector import DefaultEntropyDetector
from harness.observability.redaction.default_secret_redactor import DefaultSecretRedactor
from harness.tools.workspace_tool_provider import WorkspaceToolProvider


SEARCH_OUTPUT_BUDGET_CHARS = 10_000

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
    search_visibility = SecretFileVisibility()
    output_budget = OutputBudget(max_chars=SEARCH_OUTPUT_BUDGET_CHARS)

    discovery = EntryPointToolDiscovery()
    provider_classes = discovery.discover()

    trusted_providers = {
        FilesystemToolProvider,
        ExecutionToolProvider,
        SearchToolProvider,
    }

    providers = []

    for provider_class in provider_classes:
        if provider_class is SearchToolProvider:
            providers.append(
                provider_class(
                    boundary, 
                    search_visibility,
                    output_budget,
                    )
            )
        elif issubclass(provider_class, WorkspaceToolProvider):
            providers.append(provider_class(boundary))
        else:
            providers.append(provider_class())
            
    registrations = []

    for provider in providers:
        if provider.__class__ in trusted_providers:
            trust_level = TrustLevel.TRUSTED
        else:
            trust_level = TrustLevel.UNKNOWN
            
        for tool in provider.get_tools():
            registrations.append(
                ToolRegistration(
                    tool=tool,
                    trust_level=trust_level,
                )
            )

    return ToolRegistry(registrations)


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


def get_entropy_detector() -> DefaultEntropyDetector:
    return DefaultEntropyDetector()


def get_secret_redactor(
    entropy_detector: DefaultEntropyDetector = Depends(get_entropy_detector),
    ) -> DefaultSecretRedactor:
    return DefaultSecretRedactor(entropy_detector)


def get_logger() -> logging.Logger:
    return logging.getLogger("harness.audit")


def get_audit_emitter(
    logger: logging.Logger = Depends(get_logger),
    secret_redactor: DefaultSecretRedactor = Depends(get_secret_redactor),
    ) -> LoggingAuditEmitter:
    return LoggingAuditEmitter(
        logger=logger,
        secret_redactor=secret_redactor,
    )


def get_agent_runtime(
    llm: BaseLLM = Depends(get_llm),
    registry: ToolRegistry = Depends(get_tool_registry),
    policy_engine: PolicyEngine = Depends(get_policy_engine),
    approval_broker: ApprovalBroker = Depends(get_approval_broker),
    settings: Settings = Depends(get_settings),
    audit_emitter: AuditEmitter = Depends(get_audit_emitter),
) -> AgentRuntime:
    return AgentRuntime(
        llm=llm,
        tools=registry,
        policy_engine=policy_engine,
        approval_broker=approval_broker,
        audit_emitter=audit_emitter,
        max_iterations=settings.max_iterations,
    )