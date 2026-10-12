import uuid
from pathlib import Path, PureWindowsPath

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.core.security import require_api_key
from app.models.schemas import DocumentUploadResponse, IndexRequest, IndexResponse
from app.services.ingestion.indexer import index_documents_to_chroma
from app.storage.chroma_store import get_vectorstore

router = APIRouter(dependencies=[Depends(require_api_key)])

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}
UPLOAD_CHUNK_SIZE = 1024 * 1024


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or ""
    if (
        not filename
        or "\x00" in filename
        or Path(filename).name != filename
        or PureWindowsPath(filename).name != filename
    ):
        raise HTTPException(status_code=400, detail="Invalid filename")

    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {suffix}. Formatos permitidos: {ALLOWED_EXTENSIONS}"
        )

    document_id = str(uuid.uuid4())
    upload_dir = Path(settings.upload_path) / document_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / filename
    try:
        with file_path.open("wb") as destination:
            bytes_written = 0
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                bytes_written += len(chunk)
                if bytes_written > settings.max_upload_bytes:
                    raise HTTPException(status_code=413, detail="File exceeds the upload size limit")
                destination.write(chunk)
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise
    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Document upload failed")
    finally:
        await file.close()

    try:
        vectorstore = await run_in_threadpool(get_vectorstore)
        docs_indexed, chunks_created, errors = await run_in_threadpool(
            index_documents_to_chroma,
            [file_path],
            vectorstore,
        )
        if docs_indexed != 1 or chunks_created == 0 or errors:
            raise RuntimeError("Indexing did not produce a complete document")
    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Document upload could not be indexed",
        )

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        format=suffix.lstrip("."),
        status="indexed",
    )


@router.post("/documents/index", response_model=IndexResponse)
async def index_documents(request: IndexRequest | None = None):
    upload_path = Path(settings.upload_path)
    seed_path = Path("data/seed")

    files_to_index = []

    if request and request.document_ids:
        for doc_id in request.document_ids:
            doc_dir = upload_path / str(doc_id)
            if doc_dir.exists():
                files_to_index.extend(doc_dir.glob("*"))
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Documento no encontrado: {doc_id}"
                )
    else:
        if upload_path.exists():
            for doc_dir in upload_path.iterdir():
                if doc_dir.is_dir():
                    files_to_index.extend(doc_dir.glob("*"))
        if seed_path.exists():
            files_to_index.extend(seed_path.glob("*"))

    if not files_to_index:
        raise HTTPException(
            status_code=400,
            detail="No hay documentos para indexar"
        )

    try:
        vectorstore = await run_in_threadpool(get_vectorstore)
        docs_indexed, chunks_created, errors = await run_in_threadpool(
            index_documents_to_chroma,
            files_to_index, vectorstore
        )

        return IndexResponse(
            indexed=docs_indexed,
            chunks_created=chunks_created,
            errors=errors,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Documents could not be indexed"
        )
