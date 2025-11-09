from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    FFMPEG_PATH: str = "ffmpeg"  # Default to system ffmpeg if not specified
    DEEPGRAM_API_KEY: str
    OPENAI_API_KEY: str
    NEO4J_URI: str | None = None
    NEO4J_USERNAME: str | None = None
    NEO4J_PASSWORD: str | None = None
    NEO4J_DATABASE: str | None = None
    AURA_INSTANCEID: str | None = None
    AURA_INSTANCENAME: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()