from pydantic_settings import BaseSettings, SettingsConfigDict


class SlackSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    slack_webhook_url: str
