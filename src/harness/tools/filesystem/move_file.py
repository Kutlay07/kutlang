from harness.security.workspace_boundary import WorkspaceBoundary

from ..base_tool import BaseTool


class MoveFileTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
    
    @property
    def name(self) -> str:
        return "move_file"

    @property
    def description(self) -> str:
        return "Move a file to a different path"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Path to the file to move.",
                },
                "destination": {
                    "type": "string",
                    "description": "Destination path for the file.",
                },
            },
            "required": ["source", "destination"],
            "additionalProperties": False,
        }

    def execute(self, source: str, destination: str) -> str:
        validated_source = self.workspace_boundary.validate(source)
        validated_destination = self.workspace_boundary.validate(destination)

        if not validated_source.is_file():
            raise FileNotFoundError(f"File not found: {source}")

        validated_source.rename(validated_destination)

        return f"Successfully moved {source} to {destination}"