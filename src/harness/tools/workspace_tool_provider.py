from harness.security.workspace_boundary import WorkspaceBoundary
from harness.tools.tool_provider import ToolProvider


class WorkspaceToolProvider(ToolProvider):
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary