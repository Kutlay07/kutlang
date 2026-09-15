from dataclasses import dataclass

from harness.policy.trust_level import TrustLevel
from harness.tools.base_tool import BaseTool


@dataclass(frozen=True)
class ToolRegistration:
    tool: BaseTool
    trust_level: TrustLevel = TrustLevel.UNKNOWN