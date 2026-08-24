import pytest

from harness.tools.base_tool import BaseTool


def test_base_tool_is_abstract():
    with pytest.raises(TypeError):
        BaseTool()


def test_tool_subclass_must_implement_all_members():
    class IncompleteTool(BaseTool):
        pass

    with pytest.raises(TypeError):
        IncompleteTool()


def test_tool_subclass_can_implement_all_members():
    class TestTool(BaseTool):
        @property
        def name(self) -> str:
            return "test_tool"

        @property
        def description(self) -> str:
            return "A test tool."
        
        @property
        def parameters(self) -> dict:
            return {
                "type": "object",
                "properties": {},
            }

        def execute(self, **kwargs) -> str:
            return "result"

    tool = TestTool()

    assert tool.name == "test_tool"
    assert tool.description == "A test tool."
    assert tool.execute() == "result"


def test_tool_subclass_must_implement_parameters():
    class IncompleteTool(BaseTool):
        @property
        def name(self) -> str:
            return "test"

        @property
        def description(self) -> str:
            return "test"

        def execute(self, **kwargs) -> str:
            return "test"

    with pytest.raises(TypeError):
        IncompleteTool()