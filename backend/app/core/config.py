"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.

    All values are loaded from environment variables.
    Defaults are provided for development convenience only.
    """

    # --- App ---
    app_name: str = "AI Business Copilot"
    app_version: str = "0.1.0"
    environment: str = "development"
    allowed_origins: str = "http://localhost:3000"

    # --- Supabase ---
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    database_url: str = ""

    # --- LLM ---
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-flash"
    gemini_api_key: str = ""

    # --- Upload ---
    upload_max_size_mb: int = 50

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
