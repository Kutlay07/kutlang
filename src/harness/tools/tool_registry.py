from .base_tool import BaseTool


class ToolRegistry:
    def __init__(self, tools: list[BaseTool]):
        self._tools = {tool.name: tool for tool in tools}

    def get(self, name: str) -> BaseTool:
        return self._tools[name]
    
    @property
    def tools(self) -> list[BaseTool]:
        return list(self._tools.values())