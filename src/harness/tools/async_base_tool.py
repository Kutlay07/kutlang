from abc import abstractmethod

from harness.tools.base_tool import BaseTool


class AsyncBaseTool(BaseTool):

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        ...