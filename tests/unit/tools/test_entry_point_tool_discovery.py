from harness.tools.entry_point_tool_discovery import (
    EntryPointToolDiscovery)
from harness.tools.tool_provider import ToolProvider


def test_entry_point_discovery_returns_tool_providers():
    discovery = EntryPointToolDiscovery()
    
    providers = discovery.discover()
    
    assert all(issubclass(provider, ToolProvider) for provider in providers)


def test_search_provider_is_discovered():
    discovery = EntryPointToolDiscovery()

    providers = discovery.discover()

    assert any(
        provider.__name__ == "SearchToolProvider"
        for provider in providers
    )