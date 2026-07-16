import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.config import settings
from app.models.schemas import DocumentUploadResponse, IndexRequest, IndexResponse
from app.services.ingestion.indexer import index_documents_to_chroma
from app.storage.chroma_store import get_vectorstore

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Carga un documento en TXT, Markdown o PDF.
    El archivo se guarda localmente para despues ser indexado.
    """
    suffix = Path(file.filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {suffix}. Formatos permitidos: {ALLOWED_EXTENSIONS}"
        )

    document_id = str(uuid.uuid4())
    upload_dir = Path(settings.upload_path) / document_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        format=suffix.lstrip("."),
        status="uploaded",
    )


@router.post("/documents/index", response_model=IndexResponse)
async def index_documents(request: IndexRequest = None):
    """
    Indexa documentos en la base vectorial.
    Si no se especifican document_ids, indexa todos los archivos en data/uploads
    y los 6 documentos seed de data/seed.
    """
    upload_path = Path(settings.upload_path)
    seed_path = Path("data/seed")

    files_to_index = []

    if request and request.document_ids:
        for doc_id in request.document_ids:
            doc_dir = upload_path / doc_id
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
        vectorstore = get_vectorstore()
        docs_indexed, chunks_created, errors = index_documents_to_chroma(
            files_to_index, vectorstore
        )

        return IndexResponse(
            indexed=docs_indexed,
            chunks_created=chunks_created,
            errors=errors,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error indexando documentos: {str(e)}"
        )
