import pytest

from harness.policy.tool_arguments import ToolArguments


def test_tool_arguments_accepts_json_compatible_values():
    arguments = ToolArguments(
        arguments={
            "path": ".env",
            "line": 42,
            "enabled": True,
            "ratio": 0.5,
            "value": None,
            "items": ["a", 1, True],
            "metadata": {"key": "value"},
        }
    )
    
    assert arguments.arguments["path"] == ".env"


@pytest.mark.parametrize(
    "value",
    [
        object(),
        {"path": object()},
        {"items": [object()]},
    ],
)
def test_tool_arguments_rejects_non_json_values(value):
    with pytest.raises(TypeError):
        ToolArguments(arguments={"value": value})