from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiInfoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="API_",
        extra="ignore",
    )

    name: str
    description: str
    version: str
    contact_name: str
    contact_email: str
    contact_url: str
    license: str
    license_url: str
