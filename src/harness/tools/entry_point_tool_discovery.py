from importlib.metadata import entry_points

from harness.tools.tool_discovery import ToolDiscovery
from harness.tools.tool_provider import ToolProvider


class EntryPointToolDiscovery(ToolDiscovery):
    
    def discover(self, ) -> list[ToolProvider]:
        providers = []
        
        for ep in entry_points(group="harness.tools"):
            provider_class = ep.load()
            provider = provider_class()
            providers.append(provider)
        
        return providers