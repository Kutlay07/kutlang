from harness.security.workspace_boundary import WorkspaceBoundary

from ..base_tool import BaseTool


class ListDirectoryTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
    
    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "List the contents of a directory"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to list.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        validated_path = self.workspace_boundary.validate(path)

        entries = sorted(
            entry.name
            for entry in validated_path.iterdir()
        )

        return "\n".join(entries)