from typing import Protocol

from harness.policy.risk_level import RiskLevel
from harness.policy.tool_execution_request import ToolExecutionRequest


class RiskClassifier(Protocol):
    def classify(self, request: ToolExecutionRequest) -> RiskLevel:
        ...