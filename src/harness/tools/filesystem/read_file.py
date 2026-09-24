from ..sync_base_tool import SyncBaseTool

from harness.security.workspace_boundary import WorkspaceBoundary


class ReadFileTool(SyncBaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
        
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file, optionally starting at a specific line and limiting the number of lines returned"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read.",
                },
                "offset": {
                    "type": "integer",
                    "description": "Starting line number to read. Line numbers are 1-based. Defaults to the first line.",
                    "minimum": 1,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of lines to read. Defaults to reading until the end of the file.",
                    "minimum": 1,
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(
        self,
        path: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> str:
        validated_path = self.workspace_boundary.validate(path)

        if offset is not None and offset < 1:
            raise ValueError("offset must be >= 1")

        if limit is not None and limit < 1:
            raise ValueError("limit must be >= 1")

        lines = validated_path.read_text(
            encoding="utf-8"
        ).splitlines(keepends=True)

        start = 0 if offset is None else offset - 1

        if limit is None:
            selected_lines = lines[start:]
        else:
            selected_lines = lines[start:start + limit]

        return "".join(selected_lines)