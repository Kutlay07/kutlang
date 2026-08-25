from harness.tools.base_tool import BaseTool
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
    
    def get_tools(self) -> list[BaseTool]:
        return [
            AppendFileTool(),
            CopyFileTool(),
            CreateDirectoryTool(),
            DeleteDirectoryTool(),
            DeleteFileTool(),
            DirectoryExistsTool(),
            EditFileTool(),
            FileExistsTool(),
            GetCurrentDirectoryTool(),
            GetFileInfoTool(),
            ListDirectoryTool(),
            MoveFileTool(),
            ReadFileTool(),
            WriteFileTool(),
        ]