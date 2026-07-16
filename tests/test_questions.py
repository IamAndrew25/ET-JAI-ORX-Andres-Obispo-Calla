from unittest.mock import patch, MagicMock

from tests.conftest import client


@patch("app.services.rag.chain.retrieve")
@patch("app.api.routes.questions.answer_question")
def test_questions_devuelve_answer_y_sources(mock_answer, mock_retrieve):
    """Post /questions debe devolver answer + sources[] usando mock del LLM."""
    # Mock directo de la funcion answer_question
    mock_answer.return_value = {
        "answer": "El patrimonio es PEN 512,0 millones.",
        "sources": [
            {
                "document": "03_Portafolio_y_Desempeno_H1_2026.md",
                "chunk_id": "test-chunk-001",
                "excerpt": "Patrimonio administrado consolidado: PEN 512,0 millones",
                "score": 0.0,
            }
        ],
    }

    response = client().post("/questions", json={"question": "patrimonio total"})

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0
    assert "document" in data["sources"][0]
    assert "excerpt" in data["sources"][0]
    mock_answer.assert_called_once_with("patrimonio total")
