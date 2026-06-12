# Product Requirements Document (PRD)

## Nombre del Producto
**mi-rag** — Sistema de Retrieval-Augmented Generation para Documentos Empresariales

## Versión
1.0 — Fase 1: Ingesta de PDFs

## Fecha
[FECHA]

---

## 1. Resumen Ejecutivo

Sistema que permite ingerir documentos PDF empresariales, extraer su contenido (texto y tablas), generar representaciones vectoriales y almacenarlas para búsqueda semántica posterior.

## 2. Problema

Las organizaciones acumulan grandes volúmenes de documentos PDF (reportes financieros, contratos, manuales) que son difíciles de buscar y analizar manualmente. No existe una forma eficiente de encontrar información relevante dispersa en múltiples documentos.

## 3. Solución

Pipeline automatizado de ingestión que:
- Extrae texto y tablas de PDFs
- Genera embeddings semánticos
- Almacena en base de datos vectorial
- Permite búsqueda por similitud semántica

## 4. Usuarios

| Usuario | Necesidad |
|---------|-----------|
| Analista de datos | Buscar información en reportes |
| Gerencia | Resumenes ejecutivos de documentos |
| Legal | Encontrar cláusulas específicas en contratos |
| Compliance | Verificar cumulative de regulaciones |

## 5. Requerimientos Funcionales

### RF-001: Ingesta de PDFs
- **Descripción:** El sistema acepta archivos PDF y extrae su contenido
- **Input:** Archivo PDF + metadata (empresa, año)
- **Output:** Chunks almacenados en Qdrant
- **Prioridad:** P0

### RF-002: Extracción de Tablas
- **Descripción:** Las tablas se extraen como chunks completos
- **Formato:** Texto estructurado con separador "|"
- **Prioridad:** P0

### RF-003: Metadata de Documentos
- **Descripción:** Cada chunk incluye empresa, año, página y tipo
- **Campos:** texto, empresa, año, página, tipo, archivo, hash
- **Prioridad:** P1

### RF-004: Manejo de Duplicados
- **Descripción:** Si se ingesta el mismo archivo, se sobrescriben los datos
- **Mecanismo:** Delete + re-insert por nombre de archivo
- **Prioridad:** P1

### RF-005: Búsqueda Semántica (Fase 2)
- **Descripción:** Buscar chunks relevantes dado un query de texto
- **Output:** Top-K chunks con scores de similaridad
- **Prioridad:** P2

## 6. Requerimientos No Funcionales

| Categoría | Requerimiento |
|-----------|---------------|
| Performance | Ingesta de 100 páginas en < 60 segundos |
| Escalabilidad | Soportar 10,000+ documentos |
| Disponibilidad | Qdrant 99.9% uptime |
| Seguridad | API keys en variables de entorno |
| Mantenibilidad | Tests con 80%+ coverage |

## 7. Tecnologías

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Lenguaje | Python | 3.11+ |
| PDF | pdfplumber | 0.11+ |
| Tokens | tiktoken | 0.7+ |
| Embeddings | OpenAI | text-embedding-3-small |
| Vector DB | Qdrant | 1.9+ |

## 8. Métricas de Éxito

| Métrica | Target |
|---------|--------|
| Tasa de extracción exitosa | > 95% |
| Chunks generados por página | 3-10 (promedio) |
| Tiempo de ingestion por PDF | < 2s/página |
| Precisión de búsqueda (Fase 2) | > 85% |

## 9. Restricciones

- Solo PDFs con texto seleccionable (no escaneados)
- Límite de API de OpenAI para embeddings
- Qdrant debe estar corriendo localmente o en la nube

## 10. Fuera de Alcance (Fase 1)

- OCR para PDFs escaneados
- Procesamiento de imágenes
- Interfaz web
- Multi-idioma
- Indexación en tiempo real

## 11. Roadmap

| Fase | Features | Timeline |
|------|----------|----------|
| Fase 1 | Ingesta de PDFs | Actual |
| Fase 2 | Query/Retrieval | +2 semanas |
| Fase 3 | Evaluación RAG | +4 semanas |
| Fase 4 | Interfaz Web | +6 semanas |
| Fase 5 | Optimización | +8 semanas |
