from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    sqlite_path: str = Field(validation_alias='sqlite_path') 
    python_log_level: str = Field(default="INFO", validation_alias='PYTHON_LOG_LEVEL')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = Settings()