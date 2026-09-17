from harness.tools.execution.process_terminator import ProcessTerminator
from harness.tools.base_tool import BaseTool
from harness.tools.execution.get_process_output import GetProcessOutputTool
from harness.tools.execution.kill_process import KillProcessTool
from harness.tools.execution.process_manager import ProcessManager
from harness.tools.execution.run_background_command import RunBackgroundCommandTool
from harness.tools.execution.run_command import RunCommandTool
from harness.tools.tool_provider import ToolProvider


class ExecutionToolProvider(ToolProvider):
    
    def get_tools(self) -> list[BaseTool]:
        process_manager = ProcessManager()
        process_terminator = ProcessTerminator()
        
        return [
            GetProcessOutputTool(process_manager),
            KillProcessTool(process_manager, process_terminator),
            RunBackgroundCommandTool(process_manager, process_terminator),
            RunCommandTool(process_terminator),
        ]