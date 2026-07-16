from tests.conftest import client


def test_health_responde_200():
    """El endpoint GET /health debe responder 200 con la estructura correcta."""
    response = client().get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "vector_store" in data
    assert "documents_indexed" in data
    assert data["status"] == "ok"


def test_health_vector_store_ready():
    """El vector store debe reportar estado 'ready'."""
    response = client().get("/health")
    data = response.json()

    assert data["vector_store"] == "ready"
