from fastapi.testclient import TestClient

from harness.agent.agent_response import AgentResponse
from harness.agent.tool_call import ToolCall
from harness.agent.tool_result import ToolResult
from harness.application.dependencies import get_llm
from harness.llm.base_llm import BaseLLM
from harness.main import app


class FakeLLM(BaseLLM):
    def __init__(self):
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
                    name="get_current_directory",
                    arguments={},
                )
            ],
        )


def test_chat_completes_end_to_end():
    fake_llm = FakeLLM()
    app.dependency_overrides[get_llm] = lambda: fake_llm

    try:
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={"prompt": "Hello"},
        )

        assert response.status_code == 200
        assert response.json()["text"] == "Task completed successfully."
        assert fake_llm.tool_result is not None
        assert fake_llm.tool_result.tool_name == "get_current_directory"
        assert fake_llm.tool_result.is_error is False
        assert fake_llm.tool_result.result

    finally:
        app.dependency_overrides.clear()