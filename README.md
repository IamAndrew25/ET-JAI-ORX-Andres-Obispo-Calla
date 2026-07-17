# Nexo Andino RAG API - Reto Tecnico Orexe (Junior AI Engineer)

Sistema RAG (Retrieval-Augmented Generation) que permite a analistas financieros de Nexo Andino Capital realizar consultas sobre portafolio, manules operativos, reportes de clientes e informes ESG, utilizando exclusivamente la base de conocimiento provista (6 documentos).

## Stack Tecnologico

- **Framework:** FastAPI + Pydantic v2
- **Orquestacion RAG:** LangChain
- **LLM:** Google Gemini (gemini-2.5-flash) con fallback automatico a gemini-flash-latest
- **Embeddings:** Google Gemini (models/gemini-embedding-001)
- **Base Vectorial:** ChromaDB (persistente local)
- **PDF Parsing:** pymupdf + pdfplumber (preservacion de tablas)
- **Testing:** pytest con mocks (sin consumo de tokens)
- **Contenedor:** Docker

## Arquitectura

```
reto-tecnico/
├── app/
│   ├── api/routes/          # Endpoints HTTP (health, documents, questions)
│   ├── core/                # Configuracion y excepciones
│   ├── models/             # Schemas Pydantic
│   ├── services/
│   │   ├── ingestion/      # Loader + Chunker tabla-aware + Indexer
│   │   ├── retrieval/      # Busqueda semantica (MMR)
│   │   └── rag/            # Chain de LangChain + Prompt anti-alucinacion
│   └── storage/            # Chroma store
├── data/
│   ├── seed/               # 6 documentos provistos
│   ├── uploads/            # Documentos subidos via API
│   └── chroma/             # Base vectorial persistente
├── tests/                  # 5 tests automatizados con mocks
├── scripts/                # Script de seed
├── Dockerfile
└── requirements.txt
```

## Como levantar el sistema con Docker

### 1. Clonar el repo

```bash
git clone https://github.com/IamAndrew25/ET-JAI-ORX-Andres-Obispo-Calla.git
cd ET-JAI-ORX-Andres-Obispo-Calla
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` y agregar tu API key de Gemini (gratis en https://aistudio.google.com/apikey):

```
GEMINI_API_KEY=tu_api_key_aqui
```

### 3. Construir la imagen Docker

```bash
docker build -t nexo-rag .
```

### 4. Levantar el contenedor

```bash
docker run -d \
  --name nexo-rag-api \
  --env-file .env \
  -p 8000:8000 \
  nexo-rag
```

### 5. Indexar los documentos

Antes de hacer consultas, indexar los 6 documentos seed:

```bash
curl -X POST http://localhost:8000/documents/index
```

### 6. Abrir Swagger

Ir a http://localhost:8000/docs para probar los endpoints.

## Variables de entorno

| Variable | Descripcion | Default |
|---|---|---|
| `GEMINI_API_KEY` | API key de Google Gemini (obligatoria) | - |
| `LLM_MODEL` | Modelo de chat | `models/gemini-2.5-flash` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `models/gemini-embedding-001` |
| `CHROMA_PATH` | Ruta de persistencia de Chroma | `./data/chroma` |
| `UPLOAD_PATH` | Ruta de uploads | `./data/uploads` |
| `CHUNK_SIZE` | Tamano de chunk (caracteres) | `800` |
| `CHUNK_OVERLAP` | Overlap entre chunks | `100` |
| `TOP_K` | Chunks recuperados por consulta | `6` |

## Pruebas automatizadas

```bash
source venv/bin/activate
pytest tests/ -v
```

## Video demostrativo

*(En proceso de grabación - Se actualizará con el link de Google Drive a la brevedad)*
