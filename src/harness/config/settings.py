from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    local_llm_base_url: str
    local_llm_model: str