from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AiAgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False
    )

    openai_api_key: str
    openai_model: str
    openai_temperature: float
    openai_max_tokens: int
    openai_timeout: int

    @field_validator('openai_api_key')
    def validate_api_key(cls, v):
        """Validate basic OpenAI API key format"""
        api_key = v.get_secret_value() if isinstance(v, SecretStr) else v
        
        if not api_key:
            raise ValueError('OpenAI API key cannot be empty')
        
        if not api_key.startswith('sk-'):
            raise ValueError('OpenAI API key should start with "sk-"')
        
        if len(api_key) < 20:  # Typical minimum length
            raise ValueError('OpenAI API key seems too short')
        
        return v
    
    @field_validator('openai_model')
    def validate_model(cls, v):
        """Verify that the model is one of the supported ones"""
        allowed_models = [
            'gpt-4', 'gpt-4-turbo', 'gpt-4o',
            'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'
        ]
        
        if v not in allowed_models:
            raise ValueError(f'Model must be one of: {", ".join(allowed_models)}')
        
        return v
    
    @field_validator('openai_temperature')
    def validate_temperature(cls, v):
        """Verify that the temperature is within a valid range (0-2)"""
        if v < 0 or v > 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v
    
    @field_validator('openai_max_tokens')
    def validate_max_tokens(cls, v):
        """Validate that max_tokens is positive and does not exceed 500"""
        if v <= 0:
            raise ValueError('max_tokens must be positive')
        if v>500:
            raise ValueError('The maximum number of tokens must be 500')
        return v