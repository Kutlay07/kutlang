from harness.tools.base_tool import BaseTool
from harness.security.workspace_boundary import WorkspaceBoundary
from harness.tools.filesystem.append_file import AppendFileTool
from harness.tools.filesystem.copy_file import CopyFileTool
from harness.tools.filesystem.create_directory import CreateDirectoryTool
from harness.tools.filesystem.delete_directory import DeleteDirectoryTool
from harness.tools.filesystem.delete_file import DeleteFileTool
from harness.tools.filesystem.directory_exists import DirectoryExistsTool
from harness.tools.filesystem.edit_file import EditFileTool
from harness.tools.filesystem.file_exists import FileExistsTool
from harness.tools.filesystem.get_current_directory import GetCurrentDirectoryTool
from harness.tools.filesystem.get_file_info import GetFileInfoTool
from harness.tools.filesystem.list_directory import ListDirectoryTool
from harness.tools.filesystem.move_file import MoveFileTool
from harness.tools.filesystem.read_file import ReadFileTool
from harness.tools.filesystem.write_file import WriteFileTool
from harness.tools.tool_provider import ToolProvider


class FilesystemToolProvider(ToolProvider):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
    
    def get_tools(self) -> list[BaseTool]:
        return [
            AppendFileTool(self.workspace_boundary),
            CopyFileTool(self.workspace_boundary),
            CreateDirectoryTool(self.workspace_boundary),
            DeleteDirectoryTool(self.workspace_boundary),
            DeleteFileTool(self.workspace_boundary),
            DirectoryExistsTool(self.workspace_boundary),
            EditFileTool(self.workspace_boundary),
            FileExistsTool(self.workspace_boundary),
            GetCurrentDirectoryTool(),
            GetFileInfoTool(self.workspace_boundary),
            ListDirectoryTool(self.workspace_boundary),
            MoveFileTool(self.workspace_boundary),
            ReadFileTool(self.workspace_boundary),
            WriteFileTool(self.workspace_boundary),
        ]