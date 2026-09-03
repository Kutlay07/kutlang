from harness.security.workspace_boundary import WorkspaceBoundary

from ..base_tool import BaseTool


class GetFileInfoTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
        
    @property
    def name(self) -> str:
        return "get_file_info"

    @property
    def description(self) -> str:
        return "Get basic information about a file or directory"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file or directory.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        validated_path = self.workspace_boundary.validate(path)

        if not validated_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        if validated_path.is_file():
            return (
                f"type: file\n"
                f"size: {validated_path.stat().st_size}"
            )

        if validated_path.is_dir():
            return (
                f"type: directory\n"
                f"size: {validated_path.stat().st_size}"
            )

        return "type: other"