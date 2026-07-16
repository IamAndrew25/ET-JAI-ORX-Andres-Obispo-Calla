from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.questions import router as questions_router
from app.api.routes.documents import router as documents_router

app = FastAPI(
    title="Nexo Andino RAG API",
    description="Sistema RAG para consultas sobre portafolio, operaciones e informes ESG de Nexo Andino Capital",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(questions_router)


@app.get("/")
async def root():
    return {"message": "Nexo Andino RAG API. Visita /docs para Swagger."}
