from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "DeepSeek Code Sentinel"
    API_V1_STR: str = "/api/v1"

    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1"

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), case_sensitive=True)

settings = Settings()
