import requests
import sys
import time

SEED_ENDPOINT = "http://localhost:8000/documents/index"
TIMEOUT_SECONDS = 30


def wait_for_api():
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
    if not wait_for_api():
        print("No se pudo conectar a la API para indexar.")
        return 1

    try:
        print("API lista. Iniciando indexacion de documentos semilla...")
        r = requests.post(SEED_ENDPOINT, timeout=300)
        if r.status_code == 200:
            data = r.json()
            if data.get("chunks_created", 0) == 0:
                print("Indexacion fallo: cero chunks creados.")
                return 1
            print(f"Indexacion exitosa: {data.get('indexed')} docs. {data.get('chunks_created')} chunks.")
            return 0
        else:
            print(f"Fallo la indexacion. Codigo: {r.status_code}, Respuesta: {r.text}")
            return 1
    except Exception as e:
        print(f"Error al indexar: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(seed_database())
