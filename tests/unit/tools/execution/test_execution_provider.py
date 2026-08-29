from harness.tools.execution.provider import ExecutionToolProvider


def test_execution_provider_returns_tools():
    provider = ExecutionToolProvider()
    
    tools = provider.get_tools()
    
    assert len(tools) == 4


def test_execution_provider_returns_expected_tools():
    provider = ExecutionToolProvider()
    
    tools = provider.get_tools()
    
    assert {tool.name for tool in tools} == {
        "get_process_output",
        "kill_process",
        "run_background_command",
        "run_command",
        }


def test_execution_provider_shares_process_manager():
    provider = ExecutionToolProvider()
    
    tools = provider.get_tools()
    
    get_output = next(
        tool for tool in tools
        if tool.name == "get_process_output"
    )
    kill = next(
        tool for tool in tools
        if tool.name == "kill_process"
    )
    background = next(
        tool for tool in tools
        if tool.name == "run_background_command"
    )
    
    assert get_output.process_manager is kill.process_manager
    assert kill.process_manager is background.process_manager