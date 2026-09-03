from harness.tools.entry_point_tool_discovery import (
    EntryPointToolDiscovery)
from harness.tools.tool_provider import ToolProvider


def test_entry_point_discovery_finds_providers():
    discovery = EntryPointToolDiscovery()
    
    providers = discovery.discover()
    
    assert len(providers) == 2


def test_entry_point_discovery_finds_expected_providers():
    discovery = EntryPointToolDiscovery()
    
    providers = discovery.discover()
    
    assert {provider.__name__ for provider in providers} == {
        "FilesystemToolProvider",
        "ExecutionToolProvider",
    }


def test_entry_point_discovery_returns_tool_providers():
    discovery = EntryPointToolDiscovery()
    
    providers = discovery.discover()
    
    assert all(issubclass(provider, ToolProvider) for provider in providers)