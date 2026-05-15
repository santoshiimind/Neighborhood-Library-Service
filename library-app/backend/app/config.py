from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://library_user:library_pass@localhost:5432/library_db"
    loan_period_days: int = 14
    fine_per_day: float = 0.50

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
