from pathlib import Path
from hashlib import sha256

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
    errors: list[str] = []
    docs_indexed = 0
    chunks_created = 0

    for file_path in file_paths:
        try:
            documents = load_file(file_path)
            document_id = _document_id(file_path)
            for document in documents:
                document.metadata["document_id"] = document_id
            chunks = chunk_documents(documents)
            if not chunks:
                errors.append(f"{file_path.name}: no text could be extracted")
                continue
            chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]
            existing_ids = vectorstore._collection.get(
                where={"document_id": document_id},
                include=[],
            )["ids"]
            vectorstore.add_documents(chunks, ids=chunk_ids)
            stale_ids = list(set(existing_ids) - set(chunk_ids))
            if stale_ids:
                vectorstore._collection.delete(ids=stale_ids)
            docs_indexed += 1
            chunks_created += len(chunks)
        except Exception:
            errors.append(f"{file_path.name}: could not be indexed")

    return docs_indexed, chunks_created, errors


def _document_id(file_path: Path) -> str:
    upload_root = Path(settings.upload_path).resolve()
    try:
        relative_path = file_path.resolve().relative_to(upload_root)
    except ValueError:
        return sha256(str(file_path.resolve()).encode("utf-8")).hexdigest()

    if len(relative_path.parts) > 1:
        return relative_path.parts[0]
    return sha256(str(relative_path).encode("utf-8")).hexdigest()
