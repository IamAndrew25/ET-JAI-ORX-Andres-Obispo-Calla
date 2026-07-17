import requests
import time
import sys

SEED_ENDPOINT = "http://localhost:8000/documents/index"
TIMEOUT_SECONDS = 30

def wait_for_api():
    """Esperar a que la API esté lista antes de indexar."""
    start = time.time()
    while time.time() - start < TIMEOUT_SECONDS:
        try:
            r = requests.get("http://localhost:8000/health", timeout=2)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False

def seed_database():
    """Llamar al endpoint de indexación para poblar Chroma."""
    if not wait_for_api():
        print("No se pudo conectar a la API para indexar. Continuando de todas formas.")
        return

    try:
        print("API lista. Iniciando indexación de documentos semilla...")
        r = requests.post(SEED_ENDPOINT, timeout=300)
        if r.status_code == 200:
            data = r.json()
            print(f"Indexación exitosa: {data.get('indexed')} documentos. {data.get('chunks_created')} chunks creados.")
        else:
            print(f"Falló la indexación. Código: {r.status_code}, Respuesta: {r.text}")
    except Exception as e:
        print(f"Error al indexar: {e}")

if __name__ == "__main__":
    seed_database()
