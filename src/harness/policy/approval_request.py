from dataclasses import dataclass

from harness.policy.approval_scope import ApprovalScope
from harness.policy.risk_level import RiskLevel
from harness.policy.tool_execution_request import ToolExecutionRequest


@dataclass(frozen=True)
class ApprovalRequest():
    tool_execution_request: ToolExecutionRequest
    risk_level: RiskLevel
    scope: ApprovalScope