from abc import ABC, abstractmethod

from harness.tools.sync_base_tool import SyncBaseTool



class ToolProvider(ABC):
    
    @abstractmethod
    def get_tools(self) -> list[SyncBaseTool]:
        ...