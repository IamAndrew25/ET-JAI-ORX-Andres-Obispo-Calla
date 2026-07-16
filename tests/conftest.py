import sys
from pathlib import Path

# Agregar la carpeta root al path para poder importar app
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app


def client():
    """Cliente de tests para FastAPI."""
    return TestClient(app)
