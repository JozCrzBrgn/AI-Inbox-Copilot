from functools import lru_cache

from .ai_agent import AiAgentSettings
from .api_info import ApiInfoSettings
from .cors import CorsSettings
from .security import SecuritySettings
from .slack import SlackSettings


class Settings:
    def __init__(self):
        self.api_info = ApiInfoSettings()
        self.security = SecuritySettings()
        self.ai_agent = AiAgentSettings()
        self.cors = CorsSettings()
        self.slack = SlackSettings()

@lru_cache
def get_settings() -> Settings:
    return Settings()