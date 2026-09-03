from importlib.metadata import entry_points

from harness.tools.tool_discovery import ToolDiscovery
from harness.tools.tool_provider import ToolProvider


class EntryPointToolDiscovery(ToolDiscovery):

    def discover(self) -> list[type[ToolProvider]]:
        providers = []

        for ep in entry_points(group="harness.tools"):
            provider_class = ep.load()
            providers.append(provider_class)

        return providers