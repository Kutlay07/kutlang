from harness.tools.base_tool import BaseTool
from harness.tools.filesystem.provider import FilesystemToolProvider


def test_filesystem_provider_returns_tools(workspace_boundary):
    provider = FilesystemToolProvider(workspace_boundary)
    
    tools = provider.get_tools()
    
    assert len(tools) == 14


def test_filesystem_provider_returns_expected_tools(workspace_boundary):
    provider = FilesystemToolProvider(workspace_boundary)
    
    tools = provider.get_tools()
    
    assert {tool.name for tool in tools} == {
            "append_file",
            "copy_file",
            "create_directory",
            "delete_directory",
            "delete_file",
            "directory_exists",
            "edit_file",
            "file_exists",
            "get_current_directory",
            "get_file_info",
            "list_directory",
            "move_file",
            "read_file",
            "write_file",
        }



def test_filesystem_provider_returns_base_tools(workspace_boundary):
    provider = FilesystemToolProvider(workspace_boundary)
    
    tools = provider.get_tools()
    
    assert all(isinstance(tool, BaseTool) for tool in tools)