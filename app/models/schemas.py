from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    document_ids: list[str] | None = Field(
        default=None, description="IDs de documentos a indexar. Si es None, indexa todos los pendientes."
    )


class IndexResponse(BaseModel):
    indexed: int = Field(description="Cantidad de documentos indexados")
    chunks_created: int = Field(description="Cantidad de chunks generados")
    errors: list[str] = Field(default_factory=list, description="Errores encontrados")


class QuestionRequest(BaseModel):
    question: str = Field(description="Pregunta en lenguaje natural")


class SourceResponse(BaseModel):
    document: str = Field(description="Nombre del documento fuente")
    chunk_id: str = Field(description="ID del chunk recuperado")
    excerpt: str = Field(description="Fragmento de texto usado como fuente")
    score: float = Field(description="Score de similaridad")


class QuestionResponse(BaseModel):
    answer: str = Field(description="Respuesta generada por el LLM")
    sources: list[SourceResponse] = Field(description="Fragmentos usados como fuente")


class HealthResponse(BaseModel):
    status: str
    vector_store: str
    documents_indexed: int


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    format: str
    status: str
