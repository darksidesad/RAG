# Definition of Done (DOD)

## Criterios Generales

Una tarea se considera completada cuando:

### Código
- [ ] El código compila sin errores (`python -m py_compile`)
- [ ] Sigue las convenciones de estilo del proyecto (PEP 8)
- [ ] Tiene type hints en funciones públicas
- [ ] Tiene docstrings descriptivos
- [ ] No tiene imports no usados

### Testing
- [ ] Tests unitarios escritos y pasando
- [ ] Tests de integración relevantes pasando
- [ ] Coverage mínimo del 80% en módulos nuevos
- [ ] Edge cases probados (errores, archivos vacíos, etc.)

### Documentación
- [ ] README actualizado si aplica
- [ ] docs/ actualizado con cambios arquitectónicos
- [ ] Comentarios en código complejo (no obvios)

### Code Review
- [ ] PR creado con descripción clara
- [ ] Al menos 1 aprobación de otro agente
- [ ] Comentarios resueltos

### Deploy
- [ ] Variables de entorno documentadas
- [ ] Dependencias en requirements.txt actualizadas
- [ ] Funciona en entorno limpio

---

## DOD Específico por Componente

### Script de Ingestión (`ingest.py`)
- [ ] Acepta --pdf, --empresa, --año como argumentos CLI
- [ ] Extrae texto y tablas de PDFs correctamente
- [ ] Chunks respetan límite de 512 tokens
- [ ] Tablas se almacenan como chunks completos
- [ ] Embeddings generados con dimensión 1536
- [ ] Payload en Qdrant tiene todos los campos requeridos
- [ ] Duplicados se sobrescriben correctamente
- [ ] Maneja errores de archivos no encontrados
- [ ] Maneja errores de conexión a Qdrant

### Módulo de Query (próximamente)
- [ ] Acepta query de texto libre
- [ ] Retorna top-K resultados relevantes
- [ ] Filtra por empresa/año cuando se especifica
- [ ] Incluye scores de similaridad

### Interfaz de Usuario (futura)
- [ ] Permite subir PDFs via web
- [ ] Muestra estado de ingesta
- [ ] Permite buscar documentos
- [ ] Responsive design
