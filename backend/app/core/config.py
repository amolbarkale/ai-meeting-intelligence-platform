from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    WHISPER_CPP_PATH: str
    WHISPER_CPP_MODEL_PATH: str

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()