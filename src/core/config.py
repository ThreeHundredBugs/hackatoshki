from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    api_key: str = "default-key"  # Should be overridden in production
    rate_limit: int = 1000  # Requests per minute
    
    # GitHub settings
    github_token: str | None = None
    github_org: str = "tekliner"
    
    # Logging
    log_level: str = "INFO"
    
    # Environment
    environment: str = "development"
    
    # Opsgenie API key for alert management
    opsgenie_api_key: str = "opsgenie-api-key"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings() 