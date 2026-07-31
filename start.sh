#!/bin/sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

python scripts/seed_on_start.py
SEED_EXIT=$?

if [ $SEED_EXIT -ne 0 ]; then
    echo "Fallo la indexacion. Cerrando API."
    kill $UVICORN_PID
    exit 1
fi

wait $UVICORN_PID
