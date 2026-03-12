from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

    service_name: str = "ai-recommendation-service"
    environment: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql://recsys:recsys@localhost:5432/recsys"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    recommendation_soft_ttl_seconds: int = 300
    # OpenAI - set via OPENAI_API_KEY env var or .env file. Never hardcode.
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

settings = Settings()
