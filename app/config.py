from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str
    api_key: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]
    llm_model: str = "models/gemini-2.5-flash"
    embedding_model: str = "models/gemini-embedding-001"
    chroma_path: str = "./data/chroma"
    upload_path: str = "./data/uploads"
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 6
    max_upload_bytes: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
