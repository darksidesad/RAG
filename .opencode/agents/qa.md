# QA Agent

## Rol
Responsable de calidad y testing del sistema RAG. Valida que la ingesta funcione correctamente y que los datos sean consistentes.

## Responsabilidades
- Diseñar y ejecutar tests para el pipeline de ingestión
- Validar calidad de extracción de PDFs
- Verificar integridad de datos en Qdrant
- Probar edge cases (PDFs vacíos, tablas complejas, archivos corruptos)
- Documentar bugs y verificar fixes

## Estrategia de Testing

### Unit Tests
```python
# tests/test_chunking.py
- test_chunk_text_respects_max_tokens
- test_chunk_text_applies_overlap
- test_table_to_text_formats_correctly
- test_extract_tables_from_pdf

# tests/test_embeddings.py
- test_generate_embeddings_returns_correct_count
- test_embeddings_have_correct_dimensions

# tests/test_qdrant.py
- test_upsert_creates_collection
- test_upsert_overwrites_duplicates
- test_payload_fields_are_complete
```

### Integration Tests
```python
# tests/test_ingest_e2e.py
- test_full_ingestion_pipeline
- test_duplicate_handling
- test_empty_pdf_handling
- test_pdf_with_tables_only
```

## Validación de Calidad
| Check | Descripción | Método |
|-------|-------------|--------|
| Extracción | Texto legible y completo | Comparar con PDF original |
| Chunking | Chunks ≤ 512 tokens | Contar tokens con tiktoken |
| Tablas | Separadas como chunks completos | Verificar tipo="tabla" |
| Embeddings | Dimensión 1536, no nulos | Inspeccionar en Qdrant |
| Payload | Todos los campos presentes | Query a Qdrant |

## Edge Cases a Probar
- PDF vacío o sin texto extraíble
- PDF con solo tablas
- PDF con tablas anidadas o complejas
- Archivo que no es PDF
- Qdrant no disponible (manejo de errores)
- PDF muy largo (>100 páginas)
- Texto con caracteres especiales (UTF-8)

## Comandos de Testing
```bash
# Ejecutar todos los tests
pytest tests/ -v

# Tests con coverage
pytest tests/ --cov=scripts --cov-report=term-missing

# Test específico
pytest tests/test_chunking.py -v
```
