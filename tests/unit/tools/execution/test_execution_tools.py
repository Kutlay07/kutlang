from harness.tools.execution.get_process_output import GetProcessOutputTool
from harness.tools.execution.kill_process import KillProcessTool
from harness.tools.execution.process_manager import ProcessManager
from harness.tools.execution.process_terminator import ProcessTerminator
from harness.tools.execution.run_background_command import (
    RunBackgroundCommandTool,
)
from harness.tools.execution.run_command import RunCommandTool


def test_execution_tools_share_process_manager():
    manager = ProcessManager()

    run_background = RunBackgroundCommandTool(manager, ProcessTerminator())
    get_output = GetProcessOutputTool(manager)
    kill = KillProcessTool(manager, ProcessTerminator())

    assert run_background.process_manager is manager
    assert get_output.process_manager is manager
    assert kill.process_manager is manager


def test_execution_tools_have_unique_names():
    manager = ProcessManager()

    tools = [
        RunCommandTool(ProcessTerminator()),
        RunBackgroundCommandTool(manager, ProcessTerminator()),
        GetProcessOutputTool(manager),
        KillProcessTool(manager, ProcessTerminator()),
    ]

    names = [tool.name for tool in tools]

    assert len(names) == len(set(names))