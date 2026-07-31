from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str
    llm_model: str = "models/gemini-2.5-flash"
    embedding_model: str = "models/gemini-embedding-001"
    chroma_path: str = "./data/chroma"
    upload_path: str = "./data/uploads"
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 6

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
