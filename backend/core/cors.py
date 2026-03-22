from typing import List, Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class CorsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False
    )

    cors_allow_origins: Union[str, List[str]]
    cors_allow_methods: Union[str, List[str]]
    cors_allow_headers: Union[str, List[str]]

    @property
    def origins_list(self) -> List[str]:
        """Convert to list for use with CORS"""
        if isinstance(self.cors_allow_origins, str):
            if self.cors_allow_origins == "*":
                return ["*"]
            return [item.strip() for item in self.cors_allow_origins.split(",") if item.strip()]
        return self.cors_allow_origins or ["*"]
    
    @property
    def methods_list(self) -> List[str]:
        """Convert methods to a list"""
        if isinstance(self.cors_allow_methods, str):
            if self.cors_allow_methods == "*":
                return ["*"]
            return [item.strip() for item in self.cors_allow_methods.split(",") if item.strip()]
        return self.cors_allow_methods or ["*"]
    
    @property
    def headers_list(self) -> List[str]:
        """Convert headers to a list"""
        if isinstance(self.cors_allow_headers, str):
            if self.cors_allow_headers == "*":
                return ["*"]
            return [item.strip() for item in self.cors_allow_headers.split(",") if item.strip()]
        return self.cors_allow_headers or ["*"]