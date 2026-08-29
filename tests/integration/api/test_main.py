from fastapi.testclient import TestClient

from harness.agent.agent_response import AgentResponse
from harness.application.dependencies import get_agent_runtime
from harness.main import app


def test_chat_endpoint():
    class FakeRuntime:
        def run(self, prompt):
            assert prompt == "Hello"
            return AgentResponse(text="Hello back")

    app.dependency_overrides[get_agent_runtime] = lambda: FakeRuntime()

    try:
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={"prompt": "Hello"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "text": "Hello back",
            "tool_calls": None,
        }
    finally:
        app.dependency_overrides.clear()


def test_chat_request_validation():
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={},
    )

    assert response.status_code == 422