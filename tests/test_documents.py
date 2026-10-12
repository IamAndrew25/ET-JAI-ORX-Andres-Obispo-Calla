import io
from unittest.mock import Mock, patch


def test_upload_indexes_valid_document(client, api_headers):
    with (
        patch("app.api.routes.documents.get_vectorstore", return_value=Mock()),
        patch("app.api.routes.documents.index_documents_to_chroma", return_value=(1, 1, [])),
    ):
        response = client.post(
            "/documents",
            files={"file": ("test.md", io.BytesIO(b"# Test"), "text/markdown")},
            headers=api_headers,
        )

    assert response.status_code == 200
    assert response.json()["filename"] == "test.md"
    assert response.json()["status"] == "indexed"


def test_upload_rejects_path_traversal(client, api_headers):
    response = client.post(
        "/documents",
        files={"file": ("../outside.md", io.BytesIO(b"# Test"), "text/markdown")},
        headers=api_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid filename"


def test_upload_rejects_oversized_file(client, api_headers):
    response = client.post(
        "/documents",
        files={"file": ("large.md", io.BytesIO(b"x" * 1025), "text/markdown")},
        headers=api_headers,
    )

    assert response.status_code == 413


def test_upload_fails_when_indexer_has_errors(client, api_headers):
    with (
        patch("app.api.routes.documents.get_vectorstore", return_value=Mock()),
        patch("app.api.routes.documents.index_documents_to_chroma", return_value=(1, 1, ["failed"])),
    ):
        response = client.post(
            "/documents",
            files={"file": ("test.md", io.BytesIO(b"# Test"), "text/markdown")},
            headers=api_headers,
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Document upload could not be indexed"


def test_upload_fails_when_indexer_creates_no_chunks(client, api_headers):
    with (
        patch("app.api.routes.documents.get_vectorstore", return_value=Mock()),
        patch("app.api.routes.documents.index_documents_to_chroma", return_value=(1, 0, [])),
    ):
        response = client.post(
            "/documents",
            files={"file": ("test.md", io.BytesIO(b"# Test"), "text/markdown")},
            headers=api_headers,
        )

    assert response.status_code == 500


def test_index_rejects_invalid_document_id(client, api_headers):
    response = client.post("/documents/index", json={"document_ids": ["../seed"]}, headers=api_headers)

    assert response.status_code == 422


def test_document_endpoints_require_api_key(client):
    response = client.post("/documents/index", json={})

    assert response.status_code == 401


def test_document_endpoints_reject_invalid_api_key(client):
    response = client.post("/documents/index", json={}, headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401
