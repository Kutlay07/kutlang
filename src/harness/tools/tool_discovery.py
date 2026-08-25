from abc import ABC, abstractmethod

from harness.tools.tool_provider import ToolProvider



class ToolDiscovery(ABC):
    
    @abstractmethod
    def discover(self) -> list[ToolProvider]:
        ...