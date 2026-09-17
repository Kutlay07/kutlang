from abc import abstractmethod

from harness.tools.base_tool import BaseTool


class SyncBaseTool(BaseTool):

    @abstractmethod
    def execute(self, **kwargs) -> str:
        ...