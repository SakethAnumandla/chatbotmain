"""
Configuration Management
Centralized configuration using Pydantic Settings for type safety and validation
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")
    openai_base_url: str = Field(default="https://api.openai.com/v1", description="OpenAI API base URL")
    
    # Platform API Configuration
    platform_api_base_url: str = Field(..., description="Base URL for platform API")
    platform_api_key: str = Field(..., description="API key for platform authentication")
    platform_api_timeout: int = Field(default=30, description="API request timeout in seconds")
    
    # Session Configuration
    session_ttl: int = Field(default=3600, description="Session TTL in seconds")
    
    # Application Runtime Configuration
    app_env: str = Field(
        default="development",
        description="Application environment"
    )
    app_debug: bool = Field(
        default=True,
        description="Application debug mode"
    )
    app_host: str = Field(
        default="0.0.0.0",
        description="Application host"
    )
    app_port: int = Field(
        default=5000,
        description="Application port"
    )
    app_secret_key: str = Field(
        ...,
        description="Application secret key"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/chatbot.log", description="Log file path")
    
    # CORS Configuration
    cors_origins: str = Field(default="*", description="Comma-separated CORS origins")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=20, description="Max requests per minute")
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.app_env.lower() == "production"


# Global settings instance
settings = Settings()
