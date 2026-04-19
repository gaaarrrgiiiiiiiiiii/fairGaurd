from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FairGuard"
    API_V1_STR: str = "/v1"
    DATABASE_URL: str = "sqlite:///./fairguard.db" # local DB for now
    SECRET_KEY: str = "secret"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
