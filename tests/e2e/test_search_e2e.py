from fastapi.testclient import TestClient

from harness.agent.agent_response import AgentResponse
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.llm.base_llm import BaseLLM
from harness.main import app
from harness.application.dependencies import get_llm, get_settings
from harness.config.settings import Settings


class FakeLLM(BaseLLM):
    def __init__(self, tool_name: str, arguments: dict):
        self.tool_name = tool_name
        self.arguments = arguments
        self.tool_result = None
        
    def generate(self, conversation, tools) -> AgentResponse:
        tool_result = next(
            (
                item
                for item in conversation
                if isinstance(item, ToolResult)
            ),
            None,
        )
        
        if tool_result is not None:
            self.tool_result = tool_result
            
            return AgentResponse(
                text="Task completed successfully.",
                tool_calls=None,
            )
            
        return AgentResponse(
            text=None,
            tool_calls=[
                ToolCall(
                    call_id="e2e-call-1",
                    name=self.tool_name,
                    arguments=self.arguments,
                )
            ],
        )


def test_chat_completes_grep_end_to_end(tmp_path):
    target_file = tmp_path / "app.py"
    target_file.write_text(
        'print("hello")\n'
        'print("needle")\n',
        encoding="utf-8",
    )

    settings = Settings(
        local_llm_base_url="http://fake",
        local_llm_model="fake",
        max_iterations=10,
        workspace_root=tmp_path,
    )

    fake_llm = FakeLLM("grep", {"query": "needle"})

    app.dependency_overrides[get_llm] = lambda: fake_llm
    app.dependency_overrides[get_settings] = lambda: settings
    
    try:
        client = TestClient(app)
        response = client.post("/chat", json={"prompt": "find needle"})
        
        assert response.status_code == 200
        assert response.json()["text"] == "Task completed successfully."
        assert fake_llm.tool_result is not None
        assert fake_llm.tool_result.tool_name == "grep"
        assert fake_llm.tool_result.is_error is False
        assert "needle" in fake_llm.tool_result.result

    finally:
        app.dependency_overrides.clear()