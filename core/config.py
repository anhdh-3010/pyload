from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


class Config(BaseConfig):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    postgres_host: str
    environment: str = "development"
    app_host: str = "localhost"
    app_port: int = 8000
    base_url: str = "http://localhost:8000"
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    google_client_id: str
    google_client_secret: str
    session_secret_key: str = ""


config: Config = Config()  # type: ignore
