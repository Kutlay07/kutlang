from unittest.mock import MagicMock

from coding_agent.agent.agent_response import AgentResponse
from coding_agent.agent.agent_runtime import AgentRuntime
from coding_agent.agent.tool_call import ToolCall
from coding_agent.llm.base_llm import BaseLLM
from coding_agent.tools.filesystem.read_file import ReadFileTool
from coding_agent.tools.tool_registry import ToolRegistry


def test_agent_runtime_reads_file_with_real_tool(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("Hello from file", encoding="utf-8")

    llm = MagicMock(spec=BaseLLM)

    llm.generate.side_effect = [
        AgentResponse(
            tool_calls=[
                ToolCall(
                    call_id="call_123",
                    name="read_file",
                    arguments={"path": str(file)},
                )
            ]
        ),
        AgentResponse(text="The file says: Hello from file"),
    ]

    tools = ToolRegistry([ReadFileTool()])
    runtime = AgentRuntime(llm, tools)

    result = runtime.run("Read the file")

    assert result.text == "The file says: Hello from file"
    assert llm.generate.call_count == 2