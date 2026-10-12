# Nexo Andino RAG API - Reto Tecnico Orexe (Junior AI Engineer)

Sistema RAG (Retrieval-Augmented Generation) que permite a analistas financieros de Nexo Andino Capital realizar consultas sobre portafolio, manuales operativos, reportes de clientes e informes ESG, utilizando exclusivamente la base de conocimiento provista (6 documentos).

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
├── scripts/                # Script de seed automatico
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

**⚠️ ESTE PASO ES OBLIGATORIO. Sin la API key, el sistema no funciona.**

```bash
cp .env.example .env
```

Editar `.env` y completar `GEMINI_API_KEY` con tu API key de Google Gemini:

```bash
# Obtener API key gratuita en:
# https://aistudio.google.com/apikey

GEMINI_API_KEY=AIza...tu_key_aqui...
API_KEY=una-clave-secreta-larga
```

Los demas valores ya estan pre-configurados con los modelos correctos. **No los cambies a menos que sepas lo que haces.**

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

El sistema **indexa los 6 documentos automaticamente al arrancar**. No requiere `curl` manual.

### 5. Verificar que todo anduvo bien

Esperar 20 segundos y revisar los logs:

```bash
sleep 20 && docker logs nexo-rag-api
```

**Deberias ver:**
```
Indexacion exitosa: 6 docs. 54 chunks.
```

**Si ves esto, no seguir:**
```
Fallo la indexacion. Cerrando API.
```
Eso significa que la API key no se configuro correctamente en el paso 2.

### 6. Abrir Swagger

Ir a http://localhost:8000/docs para probar los endpoints.

## Verificacion rapida (post-levantamiento)

```bash
# Check salud
curl http://localhost:8000/health

# Test pregunta
curl -X POST http://localhost:8000/questions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: una-clave-secreta-larga" \
  -d '{"question": "Cual es el patrimonio total administrado al 30/06/2026?"}'
```

Respuesta esperada: `PEN 512,0 millones` con las fuentes citadas.

## Variables de entorno

| Variable | Descripcion | Default |
|---|---|---|
| `GEMINI_API_KEY` | API key de Google Gemini (**obligatoria**) | - |
| `API_KEY` | Clave requerida en `X-API-Key` para documentos y preguntas (**obligatoria**) | - |
| `CORS_ORIGINS` | Origenes CORS permitidos (lista JSON) | `["http://localhost:3000"]` |
| `LLM_MODEL` | Modelo de chat | `models/gemini-2.5-flash` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `models/gemini-embedding-001` |
| `CHROMA_PATH` | Ruta de persistencia de Chroma | `./data/chroma` |
| `UPLOAD_PATH` | Ruta de uploads | `./data/uploads` |
| `CHUNK_SIZE` | Tamano de chunk (caracteres) | `800` |
| `CHUNK_OVERLAP` | Overlap entre chunks | `100` |
| `TOP_K` | Chunks recuperados por consulta | `6` |
| `MAX_UPLOAD_BYTES` | Tamano maximo de archivo subido | `10485760` |

## Pruebas automatizadas

```bash
source venv/bin/activate
pytest tests/ -v
```

19 tests deterministas con mocks, sin consumir tokens de Gemini:
- `test_documents.py`: cargas, autenticación, traversal, límites y fallos de indexado.
- `test_health.py`: disponibilidad y conteo real de documentos.
- `test_indexer.py`: IDs estables e indexado idempotente.
- `test_questions.py`: validación, autenticación y errores internos.
- `test_seed_on_start.py`: autenticación del indexado automático al iniciar Docker.

## Endpoints

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/health` | Estado de la API |
| POST | `/documents` | Subir documento (lo indexa automaticamente) |
| POST | `/documents/index` | Re-indexar todos los documentos |
| POST | `/questions` | Consulta en lenguaje natural (devuelve respuesta + fuentes) |

## Video demostrativo

[Ver video demostrativo en Google Drive](https://drive.google.com/file/d/1B10OAqa5YMESZ26I6olqsFpxJG5lGeku/view?usp=sharing)
