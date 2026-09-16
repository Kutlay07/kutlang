from dataclasses import dataclass

from harness.policy.trust_level import TrustLevel
from harness.tools.sync_base_tool import SyncBaseTool


@dataclass(frozen=True)
class ToolRegistration:
    tool: SyncBaseTool
    trust_level: TrustLevel = TrustLevel.UNKNOWN