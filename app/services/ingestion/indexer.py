from pathlib import Path

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings
from app.services.ingestion.chunker import chunk_documents
from app.services.ingestion.loader import load_file


def create_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.gemini_api_key,
    )


def index_document(file_path: Path) -> tuple[int, list[str]]:
    """
    Procesa un archivo: load → chunk → embed → return.
    Devuelve (chunks_count, chunk_ids).
    """
    documents = load_file(file_path)
    chunks = chunk_documents(documents)

    chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]

    return len(chunks), chunk_ids


def index_documents_to_chroma(
    file_paths: list[Path],
    vectorstore,
) -> tuple[int, int, list[str]]:
    """
    Indexa múltiples archivos en Chroma.
    Devuelve (docs_indexed, chunks_created, errors).
    """
    all_chunks: list[Document] = []
    errors: list[str] = []
    docs_indexed = 0

    for file_path in file_paths:
        try:
            documents = load_file(file_path)
            chunks = chunk_documents(documents)
            all_chunks.extend(chunks)
            docs_indexed += 1
        except Exception as e:
            errors.append(f"{file_path.name}: {str(e)}")

    if all_chunks:
        chunk_ids = [chunk.metadata["chunk_id"] for chunk in all_chunks]
        vectorstore.add_documents(all_chunks, ids=chunk_ids)

    return docs_indexed, len(all_chunks), errors
