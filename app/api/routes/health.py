from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from app.models.schemas import HealthResponse
from app.storage.chroma_store import get_vectorstore

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    try:
        collection = (await run_in_threadpool(get_vectorstore))._collection
        records = await run_in_threadpool(collection.get, include=["metadatas"])
        document_ids = {
            metadata.get("document_id", metadata.get("source"))
            for metadata in records["metadatas"]
        }
        documents_indexed = len(document_ids)
    except Exception:
        raise HTTPException(status_code=503, detail="Vector store unavailable")

    return HealthResponse(status="ok", vector_store="ready", documents_indexed=documents_indexed)
