# AGENTS.md — Configuración de Agentes

## Proyecto: mi-rag

Sistema de Retrieval-Augmented Generation para documentos empresariales.

## Agentes Disponibles

### Architect Agent
- **Rol:** Diseñador técnico
- **Archivo:** `.opencode/agents/architect.md`
- **Uso:** Cuando necesites decisiones de arquitectura, diseño de sistema o revisión técnica

### Developer Agent
- **Rol:** Desarrollador principal
- **Archivo:** `.opencode/agents/developer.md`
- **Uso:** Para implementar features,写代码, resolver bugs técnicos

### DevOps Agent
- **Rol:** Infraestructura y operaciones
- **Archivo:** `.opencode/agents/devops.md`
- **Uso:** Para configurar servicios, Docker, variables de entorno, monitoreo

### Product Owner Agent
- **Rol:** Dueño del producto
- **Archivo:** `.opencode/agents/product-owner.md`
- **Uso:** Para definir requerimientos, prioridades, criterios de aceptación

### QA Agent
- **Rol:** Calidad y testing
- **Archivo:** `.opencode/agents/qa.md`
- **Uso:** Para escribir tests, validar funcionalidad, reportar bugs

## Convenciones del Proyecto

### Código
- Python 3.11+
- PEP 8 con ruff/black
- Type hints en funciones públicas
- Docstrings descriptivos

### Comandos
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar ingestión
python scripts/ingest.py --pdf doc.pdf --empresa "ACME" --año 2024

# Verificar sintaxis
python -m py_compile scripts/ingest.py

# Tests
pytest tests/ -v
```

### Variables de Entorno
```bash
OPENAI_API_KEY=sk-...
QDRANT_URL=http://localhost:6333
```

### Estructura
```
mi-rag/
├── .opencode/agents/   # Definiciones de agentes
├── docs/               # Documentación del proyecto
├── scripts/            # Scripts ejecutables
│   └── ingest.py       # Pipeline de ingestión
├── tests/              # Tests (próximamente)
├── requirements.txt    # Dependencias
└── AGENTS.md           # Este archivo
```

## Flujo de Trabajo

1. **Product Owner** define la tarea y criterios de aceptación
2. **Architect** diseña la solución técnica
3. **Developer** implementa el código
4. **QA** valida con tests
5. **DevOps** despliega y monitorea

## Reglas

- Siempre ejecutar `python -m py_compile` antes de commit
- No hardcodear valores — usar variables de entorno
- Documentar decisiones técnicas en `docs/`
- Mantener los agentes actualizados con información del proyecto
