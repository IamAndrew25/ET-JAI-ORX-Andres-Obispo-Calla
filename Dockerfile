FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY data/seed/ ./data/seed/
COPY scripts/ ./scripts/
COPY start.sh ./start.sh

RUN mkdir -p data/uploads data/chroma

RUN chmod +x scripts/*.py start.sh 2>/dev/null || true

# Exponer el puerto de Uvicorn
EXPOSE 8000

# Comando que levanta la API e indexa los docs automaticamente
CMD ["sh", "start.sh"]
