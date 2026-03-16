from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SEC_",
        extra="ignore",
        case_sensitive=False
    )

    jwt_secret: str
    algorithm: str
    auth_username: str
    auth_password: str

    @field_validator('jwt_secret')
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError('jwt_secret must be at least 32 characters long.')
        return v

    @field_validator('algorithm')
    def validate_algorithm(cls, v):
        allowed = ['HS256', 'HS384', 'HS512']
        if v not in allowed:
            raise ValueError(f'algorithm must be one of{allowed}')
        return v