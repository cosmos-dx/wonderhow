from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model_fast: str = "gpt-4o-mini"
    openai_model_strong: str = "gpt-4o"

    tavily_api_key: str = ""
    newsapi_key: str = ""

    database_url: str = "postgresql+asyncpg://wonderhow:wonderhow@localhost:5432/wonderhow"
    redis_url: str = "redis://localhost:6379/0"
    chroma_host: str = "localhost"
    chroma_port: int = 8100

    tick_interval_seconds: float = 15.0
    max_cascade_depth: int = 3

    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
