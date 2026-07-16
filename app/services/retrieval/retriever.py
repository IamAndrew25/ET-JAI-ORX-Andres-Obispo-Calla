from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.config import settings
from app.storage.chroma_store import get_vectorstore


def get_retriever(vectorstore: Chroma | None = None):
    """
    Crea un retriever desde Chroma con MMR (Maximum Marginal Relevance).
    MMR evita que los resultados sean todos de la misma sección.
    """
    if vectorstore is None:
        vectorstore = get_vectorstore()

    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": settings.top_k,
            "fetch_k": settings.top_k * 2,
        },
    )


def retrieve(question: str, vectorstore: Chroma | None = None) -> list[Document]:
    """
    Busca los chunks más similares a la pregunta.
    Devuelve los Documents con su contenido y metadatos.
    """
    retriever = get_retriever(vectorstore)
    return retriever.invoke(question)
