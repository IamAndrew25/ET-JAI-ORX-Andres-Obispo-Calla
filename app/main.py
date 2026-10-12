from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.questions import router as questions_router
from app.api.routes.documents import router as documents_router
from app.config import settings

class UploadTooLarge(Exception):
    pass


class UploadSizeLimitMiddleware:
    def __init__(self, app, max_upload_bytes: int):
        self.app = app
        # The extra space allows multipart headers while the route enforces the file limit.
        self.max_request_bytes = max_upload_bytes + 1024 * 1024

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] != "/documents":
            await self.app(scope, receive, send)
            return

        received_bytes = 0

        async def limited_receive():
            nonlocal received_bytes
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_request_bytes:
                    raise UploadTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except UploadTooLarge:
            response = JSONResponse(
                status_code=413,
                content={"detail": "File exceeds the upload size limit"},
            )
            await response(scope, receive, send)


app = FastAPI(
    title="Nexo Andino RAG API",
    description="Sistema RAG para consultas sobre portafolio, operaciones e informes ESG de Nexo Andino Capital",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


app.add_middleware(UploadSizeLimitMiddleware, max_upload_bytes=settings.max_upload_bytes)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(questions_router)


@app.get("/")
async def root():
    return {"message": "Nexo Andino RAG API. Visita /docs para Swagger."}
