from fastapi import FastAPI, Depends

from harness.application.dependencies import get_agent_runtime
from harness.api.schemas.chat_request import ChatRequest
from harness.agent.agent_runtime import AgentRuntime


app = FastAPI(
    title="Kutlang",
    summary="Coding agent harness",
    contact={
        "name": "Kutlay",
    },
    license_info={
        "name": "MIT",
    },
)


@app.post("/chat")
def chat(
    request: ChatRequest,
    runtime: AgentRuntime = Depends(get_agent_runtime),
):
    return runtime.run(request.prompt)