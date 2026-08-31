from dataclasses import dataclass

from harness.policy.tool_execution_request import ToolExecutionRequest


@dataclass(frozen=True)
class PolicyContext:
    request: ToolExecutionRequest