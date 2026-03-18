from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    database_url: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/order_system'
    app_env: str = 'dev'

    jwt_secret: str = 'change-me-in-prod'
    jwt_algorithm: str = 'HS256'
    jwt_access_ttl_seconds: int = 3600
    jwt_refresh_ttl_seconds: int = 1209600

    redis_url: str = 'redis://localhost:6379/0'
    celery_broker_url: str = 'redis://localhost:6379/1'
    celery_result_backend: str = 'redis://localhost:6379/2'


settings = Settings()
