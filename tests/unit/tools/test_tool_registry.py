from unittest.mock import MagicMock

import pytest

from harness.tools.sync_base_tool import SyncBaseTool
from harness.tools.tool_registry import ToolRegistry
from harness.tools.execution.run_command import RunCommandTool
from harness.policy.trust_level import TrustLevel
from harness.tools.tool_registration import ToolRegistration


def test_registry_stores_tools_by_name():
    tool = MagicMock(spec=SyncBaseTool)
    type(tool).name = property(lambda _: "read_file")

    registry = ToolRegistry([
    ToolRegistration(
        tool=tool,
        trust_level=TrustLevel.TRUSTED,
        )
    ])

    assert registry.get("read_file") is tool


def test_registry_supports_multiple_tools():
    read_file = MagicMock(spec=SyncBaseTool)
    type(read_file).name = property(lambda _: "read_file")

    write_file = MagicMock(spec=SyncBaseTool)
    type(write_file).name = property(lambda _: "write_file")

    registry1 = ToolRegistry([
    ToolRegistration(
        tool=read_file,
        trust_level=TrustLevel.TRUSTED,
        )
    ])
    
    registry2 = ToolRegistry([
        ToolRegistration(
            tool=write_file,
            trust_level=TrustLevel.TRUSTED,
        )
    ])

    assert registry1.get("read_file") is read_file
    assert registry2.get("write_file") is write_file


def test_registry_raises_for_unknown_tool():
    registry = ToolRegistry([])

    with pytest.raises(KeyError):
        registry.get("unknown_tool")


def test_registry_exposes_registered_tools():
    tool = MagicMock(spec=SyncBaseTool)
    tool.name = "read_file"

    registry = ToolRegistry([
        ToolRegistration(
            tool=tool,
            trust_level=TrustLevel.TRUSTED,
            )
        ])

    assert registry.tools == [tool]


def test_registry_registers_run_command_tool():
    tool = RunCommandTool()
    registry = ToolRegistry([
        ToolRegistration(
            tool=tool,
            trust_level=TrustLevel.TRUSTED,
        )
    ])

    assert registry.get("run_command") is tool
    assert tool in registry.tools


def test_registry_returns_registration():
    tool = MagicMock(spec=SyncBaseTool)
    type(tool).name = property(lambda _: "read_file")
    
    registration = ToolRegistration(
        tool=tool,
        trust_level=TrustLevel.TRUSTED,
    )
    
    registry = ToolRegistry([registration])
    
    result = registry.get_registration("read_file")
    
    assert registry.get_registration("read_file") is registration
    assert result.tool is tool
    assert result.trust_level == TrustLevel.TRUSTED