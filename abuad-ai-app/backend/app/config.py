from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ABUAD AI Assistant API"
    app_version: str = "4.0.0"
    database_url: str = "sqlite:///./abuad.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    frontend_origin: str = "http://localhost:5173"
    admin_key: str = "change-me"
    documents_dir: str = "../documents"
    rag_top_k: int = 5
    max_history_messages: int = 12
    max_upload_mb: int = 15

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
