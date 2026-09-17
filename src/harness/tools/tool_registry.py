from .sync_base_tool import SyncBaseTool
from .tool_registration import ToolRegistration


class ToolRegistry:
    def __init__(
        self, 
        registrations: list[ToolRegistration]):
        self._tools = {
            registration.tool.name: registration
            for registration in registrations}

    def get(self, name: str) -> SyncBaseTool:
        return self._tools[name].tool

    def get_registration(self, name: str) -> ToolRegistration:
        return self._tools[name]

    @property
    def tools(self) -> list[SyncBaseTool]:
        return [
            registration.tool
            for registration in self._tools.values()
        ]