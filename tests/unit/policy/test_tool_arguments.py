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


def test_tool_arguments_isolated_from_source_mapping_mutation():
    args = {"path": "main.py"}
    tool_args = ToolArguments(arguments=args)

    args["path"] = "evil.py"

    assert tool_args.arguments["path"] == "main.py"


def test_mapping_is_immutable():
    args = {"path": "main.py"}
    tool_args = ToolArguments(arguments=args)
    with pytest.raises(TypeError):
        tool_args.arguments["path"] = "evil.py"


def test_nested_object_is_immutable():
    args = {
    "config": {
        "paths": ["a.py"]
        }
    }
    tool_args = ToolArguments(arguments=args)
    
    args["config"]["paths"].append("evil.py")
    
    assert tool_args.arguments["config"]["paths"] == ("a.py",)
    
    with pytest.raises(TypeError):
        tool_args.arguments["config"]["paths"] = ("bok.py",)


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ]
)
def test_rejects_non_finite_floats(value):
    with pytest.raises(TypeError):
        ToolArguments(arguments={"value": value})


def test_list_contains_itself():
    args = []
    args.append(args)
    
    with pytest.raises(TypeError):
        ToolArguments(arguments={"value": args})


def test_mapping_contains_itself():
    args = {}
    args["self"] = args
    
    with pytest.raises(TypeError):
        ToolArguments(arguments={"value": args})


def test_indirect_cycle():
    a = []
    b = {"items": a}
    a.append(b)
    
    with pytest.raises(TypeError):
        ToolArguments(arguments={"value": a})