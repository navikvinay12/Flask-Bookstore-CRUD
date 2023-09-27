from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')
    DATABASE_URL: str
    JWT_KEY: str
    ALGORITHM: str
    ADMIN_KEY: str
    USER_PORT: int
    EMAIL_USER: str
    EMAIL_PASS: str
    BOOK_PORT: int

setting = Settings()
