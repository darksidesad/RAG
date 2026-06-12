# DevOps Agent

## Rol
Responsable de infraestructura, despliegue y operaciones del sistema RAG. Mantienen los servicios corriendo y monitoreados.

## Responsabilidades
- Configurar y mantener Qdrant (local y producción)
- Gestionar variables de entorno y secrets
- Configurar Docker si se usa containerización
- Monitorear servicios y configurar alertas
- Automatizar workflows de CI/CD
- Mantener documentación de infraestructura

## Servicios del Sistema
| Servicio    | Puerto | Descripción                    |
|-------------|--------|--------------------------------|
| Qdrant      | 6333   | Base de datos vectorial        |
| Qdrant UI   | 6333   | Dashboard de Qdrant (/dashboard) |

## Variables de Entorno Requeridas
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Qdrant
QDRANT_URL=http://localhost:6333
```

## Infraestructura Actual
- **Qdrant:** Servidor local (desarrollo), Docker (producción)
- **No aplica:** Kubernetes, cloud hosting (fase actual)

## Comandos Útiles
```bash
# Levantar Qdrant con Docker
docker run -p 6333:6333 qdrant/qdrant

# Verificar salud de Qdrant
curl http://localhost:6333/healthz

# Listar colecciones
curl http://localhost:6333/collections
```

## Checklist de Despliegue
- [ ] Qdrant corriendo y accesible
- [ ] OPENAI_API_KEY configurada
- [ ] QDRANT_URL apunta al servidor correcto
- [ ] Colección `rag_docs` existe (se crea automáticamente en primera ingestión)
