from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings


def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.gemini_api_key,
    )


def get_vectorstore() -> Chroma:
    """Crea o abre un Chroma store persistente."""
    return Chroma(
        collection_name="nexo_andino_kb",
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_path,
    )
