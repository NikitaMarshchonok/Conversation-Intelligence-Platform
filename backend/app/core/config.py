from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg2://conversation:conversation@localhost:5432/conversation_db"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "document_chunks"
    embedding_vector_size: int = 128
    llm_provider: str = "local_grounded"
    upload_storage_dir: str = "./storage/uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
