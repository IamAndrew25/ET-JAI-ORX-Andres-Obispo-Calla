import io
from tests.conftest import client


def test_subir_documento_md_exitoso():
    """Subir un archivo .md válido debe responder 200 con document_id."""
    contenido = b"# Documento de prueba\n\nEste es un contenido de prueba."
    archivo = {"file": ("test.md", io.BytesIO(contenido), "text/markdown")}

    response = client().post("/documents", files=archivo)

    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "filename" in data
    assert data["filename"] == "test.md"
    assert data["format"] == "md"
    assert data["status"] == "indexed"


def test_subir_documento_invalido_rechazado():
    """Subir un archivo .docx debe fallar con 400."""
    contenido = b"contenido falso de docx"
    archivo = {"file": ("test.docx", io.BytesIO(contenido), "application/octet-stream")}

    response = client().post("/documents", files=archivo)

    assert response.status_code == 400
