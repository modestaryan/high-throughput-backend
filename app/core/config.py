from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/high_throughput_db"
    JWT_SECRET: str = "supersecretjwtkeyforhighthroughputbackend2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    IDEMPOTENCY_EXPIRE_SECONDS: int = 86400

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()