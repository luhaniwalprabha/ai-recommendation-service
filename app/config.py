from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "ai-recommendation-service"
    environment: str = "local"
    log_level: str = "INFO"


settings = Settings()
