from pathlib import Path

import pdfplumber
import pymupdf
from langchain_core.documents import Document


def load_file(file_path: Path) -> list[Document]:
    """
    Extrae texto de un archivo según su extensión.
    Devuelve una lista de Documents de LangChain con metadatos.
    """
    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        return _load_txt(file_path)
    elif suffix == ".md":
        return _load_md(file_path)
    elif suffix == ".pdf":
        return _load_pdf(file_path)
    else:
        raise ValueError(f"Formato no soportado: {suffix}")


def _load_txt(file_path: Path) -> list[Document]:
    text = file_path.read_text(encoding="utf-8")
    return [Document(
        page_content=text,
        metadata={"source": file_path.name, "format": "txt", "page": 0}
    )]


def _load_md(file_path: Path) -> list[Document]:
    text = file_path.read_text(encoding="utf-8")
    return [Document(
        page_content=text,
        metadata={"source": file_path.name, "format": "md", "page": 0}
    )]


def _load_pdf(file_path: Path) -> list[Document]:
    documents = []

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""

            tables = page.extract_tables() or []
            for table in tables:
                text += "\n\n" + _table_to_markdown(table)

            if text.strip():
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "source": file_path.name,
                        "format": "pdf",
                        "page": page_num + 1,
                    }
                ))

    return documents


def _table_to_markdown(table: list[list[list[str]]]) -> str:
    """Convierte una tabla extraída por pdfplumber a formato Markdown."""
    if not table or not table[0]:
        return ""

    header = table[0]
    rows = table[1:]

    def escape(cell):
        return str(cell).replace("\n", " ").replace("|", "\\|") if cell else ""

    lines = []
    lines.append("| " + " | ".join(escape(c) for c in header) + " |")
    lines.append("|" + "|".join("---" for _ in header) + "|")

    for row in rows:
        lines.append("| " + " | ".join(escape(c) for c in row) + " |")

    return "\n".join(lines)
