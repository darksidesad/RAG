# Arquitectura del Sistema RAG

## Visión General

Sistema de Retrieval-Augmented Generation (RAG) para ingestión, almacenamiento y recuperación de información de documentos PDF empresariales.

## Diagrama del Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   PDF       │───▶│  Extracción │───▶│  Chunking   │───▶│  Embeddings │
│  (input)    │    │  pdfplumber │    │  512 tok    │    │  OpenAI     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                               │
                                                               ▼
                                                        ┌─────────────┐
                                                        │   Qdrant    │
                                                        │  (storage)  │
                                                        └─────────────┘
```

## Componentes

### 1. Extracción (`extract_pdf_content`)
- **Librería:** pdfplumber
- **Input:** Archivo PDF
- **Output:** Lista de páginas con texto y tablas
- **Por página:** texto plano + tablas estructuradas (listas de listas)

### 2. Chunking (`build_chunks`)
- **Estrategia:** Texto dividido en chunks de ~512 tokens
- **Overlap:** 64 tokens entre chunks consecuentes
- **Tablas:** Se almacenan como chunk completo sin dividir
- **Respeto:** Párrafos y oraciones no se cortan innecesariamente

### 3. Embeddings (`generate_embeddings`)
- **Modelo:** text-embedding-3-small (OpenAI)
- **Dimensiones:** 1536
- **Batch:** Hasta 200 textos por llamada API

### 4. Almacenamiento (`upsert_to_qdrant`)
- **Base de datos:** Qdrant (vector database)
- **Colección:** `rag_docs`
- **Distance:** Cosine similarity
- **Dedup:** Elimina registros del mismo archivo antes de re-insertar

## Esquema de Payload

Cada punto en Qdrant tiene este payload:

```json
{
  "texto": "Contenido del chunk...",
  "empresa": "Nombre de la empresa",
  "año": "2024",
  "página": 1,
  "tipo": "texto | tabla",
  "archivo": "documento.pdf",
  "hash": "sha256_del_archivo"
}
```

## Decisiones de Arquitectura

| Decisión | Alternativa descartada | Justificación |
|----------|------------------------|---------------|
| pdfplumber sobre PyMuPDF | PyMuPDF, camelot | Mejor soporte de tablas, API simple |
| Qdrant sobre ChromaDB | ChromaDB, Weaviate | Mejor rendimiento, API REST completa |
| text-embedding-3-small | ada-002, all-MiniLM | Mejor calidad/costo, dimensiones reducidas |
| Chunking por tokens | Por caracteres | Más preciso, respeta límites del modelo |

## Variables de Entorno

```bash
OPENAI_API_KEY=sk-...          # API key de OpenAI
QDRANT_URL=http://localhost:6333  # URL del servidor Qdrant
```

## Estructura del Proyecto

```
mi-rag/
├── .opencode/agents/     # Definiciones de agentes
├── docs/                 # Documentación
├── scripts/
│   └── ingest.py         # Script principal de ingestión
├── tests/                # Tests (próximamente)
├── requirements.txt      # Dependencias Python
└── AGENTS.md             # Configuración de agentes opencode
```
