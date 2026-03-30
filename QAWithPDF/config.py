from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    app_name: str = "DocQuest API"
    app_env: str = Field(default="dev", alias="APP_ENV")

    data_dir: Path = Field(default=Path("Data"), alias="DATA_DIR")
    storage_dir: Path = Field(default=Path("storage"), alias="STORAGE_DIR")
    upload_dir: Path = Field(default=Path("uploads"), alias="UPLOAD_DIR")

    llm_provider: str = Field(default="gemini", alias="LLM_PROVIDER")
    gemini_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    gemini_model_name: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL_NAME")
    gemini_embedding_model_name: str = Field(
        default="gemini-embedding-001", alias="GEMINI_EMBEDDING_MODEL_NAME"
    )

    top_k: int = Field(default=5, alias="TOP_K")
    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="docquest", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    postgres_sslmode: str = Field(default="disable", alias="POSTGRES_SSLMODE")
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
        alias="CORS_ORIGINS",
    )
    auth_username: str = Field(default="admin", alias="AUTH_USERNAME")
    auth_password: str = Field(default="admin123", alias="AUTH_PASSWORD")
    auth_secret_key: str = Field(default="change_me_in_env", alias="AUTH_SECRET_KEY")
    auth_algorithm: str = Field(default="HS256", alias="AUTH_ALGORITHM")
    auth_token_expire_minutes: int = Field(default=60 * 12, alias="AUTH_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)


settings = Settings()


def get_database_url() -> str:
    if settings.database_url and settings.database_url.strip():
        return settings.database_url.strip()

    encoded_password = quote_plus(settings.postgres_password)
    return (
        f"postgresql+psycopg2://{settings.postgres_user}:{encoded_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        f"?sslmode={settings.postgres_sslmode}"
    )


def get_cors_origins() -> list[str]:
    defaults = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    configured = [origin.strip() for origin in settings.cors_origins_raw.split(",") if origin.strip()]

    # Keep defaults to support both Docker frontend (3000) and local dev frontend (3001).
    merged: list[str] = []
    for origin in [*defaults, *configured]:
        if origin not in merged:
            merged.append(origin)
    return merged


def ensure_directories() -> None:
    for directory in [settings.data_dir, settings.storage_dir, settings.upload_dir]:
        directory.mkdir(parents=True, exist_ok=True)
