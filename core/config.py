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
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    session_secret_key: str = "wz8KcXr6mX9ZQ2fTq3L1YvN7pH5sUeA4B0dJkR8cGmP2xW9uFzTn6QhV1yL3Eo7aS"


config: Config = Config()  # type: ignore
