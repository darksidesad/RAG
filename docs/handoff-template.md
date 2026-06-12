# Handoff Template

## Contexto del Proyecto

**Nombre:** mi-rag — Sistema RAG para documentos empresariales
**Estado actual:** Fase 1 - Ingesta de PDFs
**Fecha de handoff:** [FECHA]

## Resumen Ejecutivo

Sistema de Retrieval-Augmented Generation que permite:
1. Ingerir PDFs empresariales
2. Extraer texto y tablas estructuradas
3. Generar embeddings vectoriales
4. Almacenar en Qdrant para búsqueda semántica

## Estado Actual

### Completado
- [x] Script de ingestión (`scripts/ingest.py`)
- [x] Extracción de PDF con pdfplumber
- [x] Chunking de texto (512 tokens, overlap 64)
- [x] Generación de embeddings (OpenAI text-embedding-3-small)
- [x] Almacenamiento en Qdrant
- [x] Manejo de duplicados
- [x] Definición de agentes del equipo

### En Progreso
- [ ] Tests unitarios
- [ ] Tests de integración

### Pendiente (Próximas Fases)
- [ ] Módulo de query/retrieval
- [ ] Interfaz de usuario
- [ ] Evaluación de calidad RAG
- [ ] Optimización de chunks
- [ ] Soporte para múltiples formatos (DOCX, HTML)

## Archivos Clave

| Archivo | Descripción |
|---------|-------------|
| `scripts/ingest.py` | Script principal de ingestión |
| `requirements.txt` | Dependencias Python |
| `.opencode/agents/*.md` | Definiciones de agentes |
| `docs/architecture.md` | Documentación arquitectónica |

## Configuración Requerida

```bash
# Variables de entorno
OPENAI_API_KEY=sk-...
QDRANT_URL=http://localhost:6333

# Instalación
pip install -r requirements.txt

# Qdrant (Docker)
docker run -p 6333:6333 qdrant/qdrant
```

## Cómo Ejecutar

```bash
# Ingesta básica
python scripts/ingest.py --pdf documento.pdf --empresa "ACME" --año 2024

# Verificar en Qdrant
curl http://localhost:6333/collections/rag_docs
```

## Conocimiento Tribal

- **Qdrant crea la colección automáticamente** en la primera ingestión
- **pdfplumber** a veces no extrae tablas complejas con celdas combinadas
- **OpenAI embeddings** tienen rate limit de 200 textos por llamada
- **Overlap de 64 tokens** es suficiente para mantener contexto entre chunks

## Próximos Pasos Recomendados

1. Escribir tests para `ingest.py`
2. Implementar módulo de query
3. Agregar logging estructurado
4. Crear dashboard de monitoreo

## Contactos

- **Arquitecto:** Architect Agent
- **Desarrollador:** Developer Agent
- **DevOps:** DevOps Agent
- **QA:** QA Agent
- **Producto:** Product Owner Agent
