from functools import lru_cache

from .api_info import ApiInfoSettings
from .security import SecuritySettings


class Settings:
    def __init__(self):
        self.api_info = ApiInfoSettings()
        self.security = SecuritySettings()

@lru_cache
def get_settings() -> Settings:
    return Settings()