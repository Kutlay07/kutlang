from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    local_llm_base_url: str
    local_llm_model: str
    max_iterations: int
    workspace_root: Path
    max_context_tokens: int = 8000
    
    model_config = SettingsConfigDict(env_file='.env')