import sys
from pathlib import Path

import pytest

# Agregar la carpeta root al path para poder importar app
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.config import settings
from app.main import app


@pytest.fixture(autouse=True)
def test_settings(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "api_key", "test-api-key")
    monkeypatch.setattr(settings, "upload_path", str(tmp_path / "uploads"))
    monkeypatch.setattr(settings, "max_upload_bytes", 1024)


@pytest.fixture
def api_headers():
    return {"X-API-Key": "test-api-key"}


@pytest.fixture
def client():
    """Cliente de tests para FastAPI."""
    with TestClient(app) as test_client:
        yield test_client
