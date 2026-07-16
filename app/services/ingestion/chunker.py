import re
import uuid

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


def chunk_documents(documents: list[Document]) -> list[Document]:
    """
    Divide Documents en chunks preservando tablas completas.
    Detecta bloques de tabla (líneas con |) y los mantiene indivisibles.
    """
    chunks = []

    table_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n| ", "\n", " ", ""],
    )

    for doc in documents:
        content = doc.page_content
        metadata = doc.metadata

        sections = _split_by_tables(content)

        for section in sections:
            is_table = section.startswith("|")

            if is_table:
                split_docs = table_splitter.split_documents([Document(
                    page_content=section, metadata=metadata.copy()
                )])
            else:
                split_docs = text_splitter.split_documents([Document(
                    page_content=section, metadata=metadata.copy()
                )])

            for split_doc in split_docs:
                chunk_metadata = split_doc.metadata.copy()
                chunk_metadata["chunk_id"] = str(uuid.uuid4())
                chunk_metadata["chunk_type"] = "table" if is_table else "text"

                chunks.append(Document(
                    page_content=split_doc.page_content,
                    metadata=chunk_metadata,
                ))

    return chunks


def _split_by_tables(content: str) -> list[str]:
    """
    Separa el contenido en secciones: bloques de tabla y bloques de texto.
    Un bloque de tabla son líneas consecutivas que empiezan con |.
    """
    lines = content.split("\n")
    sections = []
    current_section = []
    in_table = False

    for line in lines:
        is_table_line = line.strip().startswith("|")

        if is_table_line:
            if not in_table:
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []
                in_table = True
            current_section.append(line)
        else:
            if in_table:
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []
                in_table = False
            current_section.append(line)

    if current_section:
        sections.append("\n".join(current_section))

    return sections
