# Reto Técnico - Junior AI Engineer - Orexe
Evaluación Técnica, 15 de julio 2026

## Qué debe hacer el sistema

Construir una API REST con un sistema RAG básico que asista a analistas financieros respondiendo dudas complejas sobre el portafolio, manuales operativos, reportes de clientes e informes ESG, usando **exclusivamente** la base de conocimiento del archivo `reto_tecnico.zip` (los 6 documentos).

### Endpoints obligatorios
- **POST /documents** — cargar documentos en TXT, Markdown o PDF
- **POST /documents/index** — extraer texto, hacer chunking, generar embeddings, guardarlos en la base vectorial local
- **POST /questions** — recibir pregunta en lenguaje natural, hacer búsqueda semántica, pasar el contexto filtrado al LLM, devolver respuesta + fragmentos usados como fuente
- **GET /health** — estado de salud de la API

### Requisito especial de ingesta
El pipeline debe extraer bien los tres formatos (.txt, .md, .pdf), cuidando que **tablas y estructuras de datos no pierdan coherencia semántica** al fragmentarse (esto aplica sobre todo a los dos PDF, que tienen tablas financieras y de KPIs).

### Casos de prueba que el sistema debe responder correctamente
El sistema será evaluado con un set fijo de consultas sobre el documento (mismas para todos los postulantes):

**Simples (extracción directa):**
- Patrimonio total administrado por Nexo Andino Capital al 30/06/2026
- Código que identifica al Fondo Horizonte Renta Fija
- Plazo estándar de liquidación de rescates del fondo NAC-MX
- Estrategia con mayor rendimiento en H1 2026
- % de instrucciones recibidas por el portal digital

**Complejas (combinación y análisis):**
- Suma del patrimonio de NAC-RF, NAC-MX, NAC-ALT y NAC-MD vs. patrimonio consolidado reportado (con cálculo)
- % de clientes en segmento institucional vs. su participación en el patrimonio administrado
- Cálculo de instrucciones por portal digital (54% de 18,420)
- Cálculo de instrucciones con falla (0.7% de 18,420)
- Aumento del patrimonio administrado (en millones PEN y %) entre 31/12/2025 y 30/06/2026

## Qué NO debe hacer / restricciones

- No debe usar información fuera de los 6 documentos provistos (nada de "inventar" o usar conocimiento general del LLM)
- Las API keys del LLM **nunca** deben quedar expuestas en el repo (ni público ni privado) — usar `.env` local + `.env.example` de referencia
- El repositorio debe ser **privado**

## Recursos permitidos

**Base vectorial local (elegir una):**
- Chroma
- FAISS
- PostgreSQL con extensión pgvector

**LLM (elegir uno, vía API):**
- OpenAI
- Anthropic
- Gemini (mencionan que Google AI Studio da API key gratuita)

**Stack obligatorio:**
- Python con FastAPI + Pydantic
- LangChain
- Docker (Dockerfile si usas Chroma/FAISS; docker-compose.yml si usas pgvector, para levantar DB + API juntos)
- Git/GitHub con manejo de ramas y Pull Requests

### ¿Puedo usar herramientas que no se mencionan ahí?

El documento no dice explícitamente "está prohibido usar otra cosa", pero hay que tener cuidado con esto:

- **Base vectorial y LLM**: el documento da opciones cerradas (Chroma/FAISS/pgvector para vectorial; OpenAI/Anthropic/Gemini para el LLM). Como es una **prueba uniforme para comparar postulantes**, lo más seguro es quedarte dentro de esas opciones — si usas algo fuera de esa lista (ej. otra base vectorial o un LLM distinto) corres el riesgo de que no se pueda evaluar igual que al resto o que levante dudas sin necesidad.
- **Herramientas de apoyo para programar** (como OpenCode, Claude Code, GLM, etc.) sí puedes usarlas libremente — el documento incluso dice "esta prueba está diseñada para aprender realizándolo" y valora tu capacidad de investigar. Eso es distinto del stack técnico del entregable, que sí está acotado a lo que listaron.
- Si tienes duda de algo específico, el mismo documento te habilita a pedir extensión/aclaración por motivos justificados, así que podrías preguntarle a Miguel si algo puntual está permitido.

## Cosas a tener en cuenta (requisitos adicionales, no técnicos de "cómo")

1. **Flujo de Git obligatorio:**
   - Repo privado, nombre sugerido `ET-JAI-ORX-Nombre-Apellido`
   - Rama `feat/rag-backend` para todo el desarrollo
   - Pull Request de `feat/rag-backend` → `main`, revisado por mramirez@orexe.pe o aortiz@orexe.pe (como reviewers)
   - Compartir acceso de lectura del repo con mramirez@orexe.pe y aortiz@orexe.pe

2. **Pruebas automatizadas:** mínimo 3, usando **mocks obligatorios** para simular las llamadas al LLM (para no gastar tokens reales en los tests)

3. **Video demostrativo (obligatorio, máx. 20 min):**
   - Explicar estructura del código y estrategia de chunking
   - Levantar el contenedor Docker desde cero, en terminal
   - Ejecutar las pruebas automatizadas
   - Probar las 10 preguntas del caso uniforme vía Swagger (`/docs`) o Postman
   - Subir a Drive con acceso libre por enlace, y linkearlo en el README

4. **README.md obligatorio** con: resumen del proyecto, instrucciones paso a paso para levantar con Docker, variables de entorno necesarias, link al video

5. **Opcional (suma puntos):** filtros por metadatos — poder indexar/consultar filtrando por documento o categoría específica, esto en una rama aparte

## Cómo te van a evaluar (pesos)

| Criterio | Peso |
|---|---|
| Lógica del flujo RAG y base vectorial (chunking, embeddings, persistencia, recuperación libre de alucinaciones) | 30% |
| Calidad de código backend (FastAPI, tipado estricto, Pydantic, manejo de excepciones) | 25% |
| Buenas prácticas (ramas, `.env` seguro, cero secretos expuestos) | 20% |
| Pruebas automatizadas (mínimo 3, con mocks) | 15% |
| Documentación y video demostrativo | 10% |

## Plazo

- Inicio: miércoles 15 de julio, 6:00 pm
- Entrega: sábado 18 de julio, 6:00 pm (extensión posible con motivo justificado)
- Live demo: lunes (hora por confirmar)
