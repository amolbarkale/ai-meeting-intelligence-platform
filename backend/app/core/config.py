from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    FFMPEG_PATH: str = "ffmpeg"  # Default to system ffmpeg if not specified
    DEEPGRAM_API_KEY: str
    OPENAI_API_KEY: str
    CHROMA_DB_PATH: str

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()