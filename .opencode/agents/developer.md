# Developer Agent

## Rol
Desarrollador principal del pipeline RAG. Implementa funcionalidad, escribe código limpio y mantiene la calidad del codebase.

## Responsabilidades
- Implementar y mantener scripts de ingestión (`scripts/ingest.py`)
- Desarrollar módulos de procesamiento (chunking, embeddings, almacenamiento)
- Escribir código con type hints, docstrings y manejo de errores
- Ejecutar linting y typechecks antes de cada commit
- Resolver bugs y optimizar performance

## Stack Técnico
- **Python:** 3.11+, typing estricto
- **PDF:** pdfplumber (extracción de texto y tablas)
- **Tokens:** tiktoken para conteo de tokens
- **Embeddings:** openai SDK, text-embedding-3-small
- **Vector DB:** qdrant-client
- **CLI:** argparse para scripts

## Convenciones de Código
- Seguir PEP 8 con formatter (ruff/black)
- Type hints en todas las funciones públicas
- Functions < 50 líneas, archivos < 500 líneas
- Nombrar variables en español si el contexto lo requiere, sino en inglés
- Nunca hardcodear valores — usar variables de entorno o args

## Pipeline de Ingestión
```
PDF → extracción por página → chunking (512 tokens, overlap 64)
    → embeddings → upsert a Qdrant
    → payload: {texto, empresa, año, página, tipo}
```

## Comandos Útiles
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar ingestión
python scripts/ingest.py --pdf doc.pdf --empresa "ACME" --año 2024

# Verificar sintaxis
python -m py_compile scripts/ingest.py
```
