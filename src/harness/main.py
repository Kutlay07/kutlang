from fastapi import FastAPI
from contextlib import asynccontextmanager

from harness.agent.agent_runtime import AgentRuntime
from harness.llm.local import LocalLLM
from harness.tools.base_tool import BaseTool
from harness.tools.tool_registry import ToolRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass



app = FastAPI(
    title="Kutlang",
    summary="Coding agent harness",
    contact={
        "name": "Kutlay",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
)