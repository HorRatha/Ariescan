from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ariescan API"
    database_url: str = "sqlite:///./ariescan.db"
    request_timeout_seconds: float = 15.0
    max_test_cases_per_run: int = 100
    max_response_bytes: int = 1_000_000
    allow_private_targets: bool = True
    allow_destructive_tests: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
