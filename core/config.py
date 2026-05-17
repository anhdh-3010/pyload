from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Config(BaseConfig):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    postgres_host: str
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_download_task_created_topic: str = "download_task.created"
    kafka_download_task_ready_topic: str = "download_task.ready"
    kafka_worker_group_id: str = "worker-service"
    worker_download_dir: str = "./downloads"
    worker_http_timeout_seconds: float = 300.0
    worker_lock_ttl_seconds: int = 300
    worker_retry_delay_seconds: int = 60
    scheduler_poll_interval_seconds: float = 2.0
    scheduler_batch_size: int = 100
    environment: str = "development"
    app_host: str = "localhost"
    app_port: int = 8000
    base_url: str = "http://localhost:8000"
    outbox_poll_interval_seconds: float = 2.0
    outbox_batch_size: int = 100
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    session_secret_key: str = "wz8KcXr6mX9ZQ2fTq3L1YvN7pH5sUeA4B0dJkR8cGmP2xW9uFzTn6QhV1yL3Eo7aS"


config: Config = Config()  # type: ignore
