from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "ai-recommendation-service"
    environment: str = "local"
    log_level: str = "INFO"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    recommendation_soft_ttl_seconds: int = 300


settings = Settings()
