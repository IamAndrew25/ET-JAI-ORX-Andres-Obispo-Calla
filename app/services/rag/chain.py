import logging
from typing import Any

from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.services.retrieval.retriever import retrieve
from app.services.rag.prompts import get_rag_prompt

logger = logging.getLogger(__name__)

FALLBACK_MODEL = "models/gemini-flash-latest"


def get_llm() -> ChatGoogleGenerativeAI:
    """Crea el LLM de Gemini con temperatura 0 para evitar alucinaciones."""
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.gemini_api_key,
        temperature=0,
    )


def get_fallback_llm() -> ChatGoogleGenerativeAI:
    """Crea el LLM de fallback (gemini-1.5-flash) en caso de que el principal falle."""
    return ChatGoogleGenerativeAI(
        model=FALLBACK_MODEL,
        google_api_key=settings.gemini_api_key,
        temperature=0,
    )


def format_docs(docs: list[Document]) -> str:
    """Formatea los chunks recuperados como contexto para el prompt."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "desconocido")
        formatted.append(f"[Fuente {i} - {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


def answer_question(question: str) -> dict[str, Any]:
    """
    Ejecuta el flujo RAG completo:
    1. Recupera chunks relevantes
    2. Genera respuesta con LLM
    3. Devuelve respuesta + fuentes
    """
    docs = retrieve(question)
    context = format_docs(docs)
    prompt = get_rag_prompt()
    
    chain = prompt | get_llm() | StrOutputParser()

    try:
        answer = chain.invoke({
            "context": context,
            "question": question,
        })
    except Exception as e:
        logger.warning(f"Error con el modelo principal {settings.llm_model}: {e}. Intentando con fallback {FALLBACK_MODEL}...")
        fallback_chain = prompt | get_fallback_llm() | StrOutputParser()
        answer = fallback_chain.invoke({
            "context": context,
            "question": question,
        })

    sources = []
    for doc in docs:
        sources.append({
            "document": doc.metadata.get("source", "desconocido"),
            "chunk_id": doc.metadata.get("chunk_id", ""),
            "excerpt": doc.page_content[:200],
            "score": doc.metadata.get("score", 0.0),
        })

    return {"answer": answer, "sources": sources}
