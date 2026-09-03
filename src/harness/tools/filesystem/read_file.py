from ..base_tool import BaseTool

from harness.security.workspace_boundary import WorkspaceBoundary


class ReadFileTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
        
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        validated_path = self.workspace_boundary.validate(path)
        return validated_path.read_text(encoding="utf-8")