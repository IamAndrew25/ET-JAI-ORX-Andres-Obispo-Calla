from unittest.mock import patch

from tests.conftest import client


@patch("app.api.routes.questions.answer_question")
def test_questions_devuelve_answer_y_sources(mock_answer):
    """Post /questions debe devolver answer + sources[] usando mock del LLM."""
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


@patch("app.api.routes.questions.answer_question")
def test_questions_respuesta_cita_fuente(mock_answer):
    """La respuesta debe citar el documento fuente (anti-alucinacion)."""
    mock_answer.return_value = {
        "answer": "PEN 512,0 millones. [Fuente: 03_Portafolio_y_Desempeno_H1_2026.md]",
        "sources": [
            {"document": "03_Portafolio_y_Desempeno_H1_2026.md", "chunk_id": "c1", "excerpt": "...", "score": 0.0}
        ],
    }

    response = client().post("/questions", json={"question": "patrimonio total"})

    assert response.status_code == 200
    answer = response.json()["answer"]
    assert "Fuente" in answer or "03_Portafolio" in answer


@patch("app.api.routes.questions.answer_question")
def test_questions_no_encuentra_responde_honestamente(mock_answer):
    """Si no hay info, el sistema debe decirlo en vez de inventar (anti-alucinacion)."""
    mock_answer.return_value = {
        "answer": "No encontre esa informacion en los documentos disponibles.",
        "sources": [],
    }

    response = client().post("/questions", json={"question": "quien gano el mundial 2022"})

    assert response.status_code == 200
    answer = response.json()["answer"]
    assert "no encontre" in answer.lower()


@patch("app.api.routes.questions.answer_question")
def test_questions_calculo_muestra_procedimiento(mock_answer):
    """Las respuestas con calculo deben mostrar el procedimiento paso a paso."""
    mock_answer.return_value = {
        "answer": "18,420 x 0.54 = 9,947 instrucciones. [Fuente: 04_Clientes]",
        "sources": [
            {"document": "04_Clientes_Ventas_y_Operaciones_H1_2026.md", "chunk_id": "c2", "excerpt": "...", "score": 0.0}
        ],
    }

    response = client().post("/questions", json={"question": "instrucciones por portal"})

    assert response.status_code == 200
    answer = response.json()["answer"]
    assert "18,420" in answer
    assert "0.54" in answer or "54%" in answer
    assert "9,947" in answer
