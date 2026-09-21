from pathlib import Path

from harness.application.dependencies import get_tool_registry
from harness.config.settings import Settings


def test_get_tool_registry_includes_glob():
    settings = Settings(
        workspace_root=Path("."),
    )

    registry = get_tool_registry(settings)

    tool = registry.get("glob")

    assert tool.name == "glob"