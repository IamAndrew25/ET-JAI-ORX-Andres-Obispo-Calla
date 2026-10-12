from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from app.core.security import require_api_key
from app.models.schemas import QuestionRequest, QuestionResponse
from app.services.rag.chain import answer_question

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.post("/questions", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Recibe una pregunta en lenguaje natural, busca en la base de conocimiento
    y devuelve una respuesta + los fragmentos usados como fuente.
    """
    try:
        result = await run_in_threadpool(answer_question, request.question)
        return QuestionResponse(
            answer=result["answer"],
            sources=result["sources"],
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Question could not be processed")
