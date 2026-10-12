from unittest.mock import Mock, patch


def test_health_returns_chroma_document_count(client):
    vectorstore = Mock()
    vectorstore._collection.get.return_value = {
        "metadatas": [
            {"document_id": "first"},
            {"document_id": "first"},
            {"document_id": "second"},
        ]
    }

    with patch("app.api.routes.health.get_vectorstore", return_value=vectorstore):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["documents_indexed"] == 2


def test_health_returns_503_when_chroma_is_unavailable(client):
    with patch("app.api.routes.health.get_vectorstore", side_effect=RuntimeError("connection refused")):
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["detail"] == "Vector store unavailable"
