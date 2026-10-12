from unittest.mock import patch


@patch("app.api.routes.questions.answer_question")
def test_question_returns_answer_and_sources(mock_answer, client, api_headers):
    mock_answer.return_value = {
        "answer": "El patrimonio es PEN 512,0 millones.",
        "sources": [{"document": "document.md", "chunk_id": "chunk-1", "excerpt": "Patrimonio", "score": 0.0}],
    }

    response = client.post("/questions", json={"question": " patrimonio total "}, headers=api_headers)

    assert response.status_code == 200
    assert response.json()["sources"]
    mock_answer.assert_called_once_with("patrimonio total")


def test_question_rejects_blank_value(client, api_headers):
    response = client.post("/questions", json={"question": " \t "}, headers=api_headers)

    assert response.status_code == 422


def test_question_rejects_overlong_value(client, api_headers):
    response = client.post("/questions", json={"question": "x" * 4001}, headers=api_headers)

    assert response.status_code == 422


@patch("app.api.routes.questions.answer_question", side_effect=RuntimeError("provider details"))
def test_question_hides_internal_errors(mock_answer, client, api_headers):
    response = client.post("/questions", json={"question": "patrimonio total"}, headers=api_headers)

    assert response.status_code == 500
    assert response.json()["detail"] == "Question could not be processed"
    assert "provider details" not in response.text


def test_question_endpoint_requires_api_key(client):
    response = client.post("/questions", json={"question": "patrimonio total"})

    assert response.status_code == 401
