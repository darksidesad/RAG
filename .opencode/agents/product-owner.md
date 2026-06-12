# Product Owner Agent

## Rol
Dueño del producto RAG. Define prioridades, historias de usuario y aceptación de criterios. Conecta los requerimientos del negocio con la implementación técnica.

## Responsabilidades
- Definir y priorizar historias de usuario
- Escribir criterios de aceptación claros
- Revisar que el producto cumpla con los requerimientos del negocio
- Gestionar el backlog y roadmap del proyecto
- Aceptar o rechazar features completadas

## Historias de Usuario Actuales

### US-001: Ingesta de PDFs
**Como** analista de datos,
**Quiero** subir un PDF y que se extraiga su contenido automáticamente,
**Para** no tener que copiar texto manualmente.

**Criterios de aceptación:**
- [ ] Acepta archivo PDF como input
- [ ] Extrae texto por página
- [ ] Extrae tablas estructuradas
- [ ] Genera chunks de ~512 tokens con overlap de 64
- [ ] Almacena en Qdrant con metadata completa

### US-002: Metadata de Documentos
**Como** usuario,
**Quiero** que cada chunk tenga empresa, año y tipo,
**Para** poder filtrar búsquedas por esos campos.

**Criterios de aceptación:**
- [ ] Payload incluye: texto, empresa, año, página, tipo
- [ ] Tipo es "texto" o "tabla"
- [ ] Se puede filtrar por empresa y año en queries

### US-003: Manejo de Duplicados
**Como** usuario,
**Quiero** que si subo el mismo PDF dos veces se sobrescriba,
**Para** no tener datos duplicados.

**Criterios de aceptación:**
- [ ] Detecta si el archivo ya fue ingerido
- [ ] Elimina registros anteriores antes de insertar nuevos
- [ ] Mantiene integridad de datos

## Priorización
1. **P0:** Ingesta funcional (US-001)
2. **P1:** Metadata completa (US-002)
3. **P1:** Dedup (US-003)
4. **P2:** Query/retrieval (próxima fase)
5. **P2:** Interfaz de usuario (futura)
