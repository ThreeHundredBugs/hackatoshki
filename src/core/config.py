from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    api_key: str = "default-key"  # Should be overridden in production
    rate_limit: int = 1000  # Requests per minute
    
    # Logging
    log_level: str = "INFO"
    
    # Environment
    environment: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings() 