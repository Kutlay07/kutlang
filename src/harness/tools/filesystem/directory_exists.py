from harness.security.workspace_boundary import WorkspaceBoundary

from ..base_tool import BaseTool


class DirectoryExistsTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
    
    @property
    def name(self) -> str:
        return "directory_exists"

    @property
    def description(self) -> str:
        return "Check whether a directory exists"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to check.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        validated_path = self.workspace_boundary.validate(path)
        return str(validated_path.is_dir()).lower()