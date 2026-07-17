#!/bin/sh
# Levantar Uvicorn en background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Esperar y indexar los 6 documentos la primera vez
python scripts/seed_on_start.py

# Traer el proceso de Uvicorn al frente para que el contenedor no muera
wait
