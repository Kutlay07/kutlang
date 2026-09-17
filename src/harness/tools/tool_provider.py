from abc import ABC, abstractmethod

from harness.tools.base_tool import BaseTool



class ToolProvider(ABC):
    
    @abstractmethod
    def get_tools(self) -> list[BaseTool]:
        ...