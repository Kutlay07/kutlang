from harness.security.search_visibility import SearchVisibility
from harness.security.workspace_boundary import WorkspaceBoundary
from harness.tools.output_budget import OutputBudget
from harness.tools.workspace_tool_provider import WorkspaceToolProvider


class SearchToolProviderBase(WorkspaceToolProvider):
    def __init__(
        self,
        workspace_boundary: WorkspaceBoundary,
        search_visibility: SearchVisibility,
        output_budget: OutputBudget,
    ):
        super().__init__(workspace_boundary)
        self.search_visibility = search_visibility
        self.output_budget = output_budget