from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Babelix"
    database_url: str = "postgresql+psycopg://babelix:babelix@localhost:5432/babelix"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="BABELIX_")


settings = Settings()
