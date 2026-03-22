from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",
        extra="ignore",
        case_sensitive=False
    )

    host: str
    port: int
    name: str
    user: str
    password: str

    @field_validator('port')
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError('port must be between 1 and 65535')
        return v