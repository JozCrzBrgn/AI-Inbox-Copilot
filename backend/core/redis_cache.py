from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", case_sensitive=False, env_prefix="REDIS_"
    )

    host: str
    port: int
    password: str
    db: int = 0

    @field_validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("port must be between 1 and 65535")
        return v

    @field_validator("db")
    def validate_db(cls, v):
        if not (0 <= v <= 15):
            raise ValueError("db must be between 0 and 15")
        return v
