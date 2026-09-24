from harness.tools.search.search_tool_provider_base import SearchToolProviderBase
from harness.tools.base_tool import BaseTool
from harness.tools.search.glob import GlobTool
from harness.tools.search.grep import GrepTool



class SearchToolProvider(SearchToolProviderBase):
    def get_tools(self) -> list[BaseTool]:
        
        return [
            GlobTool(
                self.workspace_boundary,
                self.search_visibility,
                self.output_budget,
                ),
            GrepTool(
                self.workspace_boundary,
                self.search_visibility,
                self.output_budget,
                ),
        ]