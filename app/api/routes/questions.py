from fastapi import APIRouter, HTTPException

from app.models.schemas import QuestionRequest, QuestionResponse
from app.services.rag.chain import answer_question

router = APIRouter()


@router.post("/questions", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Recibe una pregunta en lenguaje natural, busca en la base de conocimiento
    y devuelve una respuesta + los fragmentos usados como fuente.
    """
    try:
        result = answer_question(request.question)
        return QuestionResponse(
            answer=result["answer"],
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando pregunta: {str(e)}")
