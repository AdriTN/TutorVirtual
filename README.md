# Guía de Cambios Pendientes  
*(Actualizado: 2025-07-03)*

---

## 1&nbsp;· Diagrama Entidad‑Relación  
**Archivos afectados:** `03_aportaciones.tex`, `04_desarrollo.tex`

| Pendiente | Acción |
|-----------|--------|
| Alinear descripción textual con modelos **SQLAlchemy** (`UserResponse`, `UserThemeProgress`, …) | Re‑escribir párrafo explicativo bajo la figura |
| Ruta de la imagen incorrecta | Cambiar `Ilustraciones/er_diagram.png.png` → `Ilustraciones/er_diagram.png` |
| `caption` ambiguo | Sustituir por: *«Diagrama Entidad–Relación (vista conceptual del dominio)»* |
| Duplicidad de `\label` | Verificar que solo exista `\label{fig:er-diagram}` |

---

## 2&nbsp;· Nombre del Modelo LLM  
**Archivos:** `02_estado_objetivos.tex`, `03_aportaciones.tex`

| Pendiente | Acción |
|-----------|--------|
| Documentación menciona *Llama‑3 8B int4 GGUF* | Actualizar para reflejar alias **Ollama**: `profesor`, `profesor_generador_ejercicios` |
| Sincronizar tabla de versiones | Añadir columna «Alias interno» y rellenar |

---

## 3&nbsp;· Endpoints de la API  
**Archivo:** `03_aportaciones.tex`

| Pendiente | Acción |
|-----------|--------|
| Endpoint desactualizado | Reemplazar `GET /api/course/courses` → `GET /api/courses/all` en Tabla `endpoints_aportaciones` |

---

## 4&nbsp;· Payload de petición a Ollama  
**Archivo:** `04_desarrollo.tex` (`lst:desarrollo_ollama-req-payload`)

1. Sustituir JSON por:  
   ```json
   {
     "model": "profesor",
     "messages": [
       { "role": "system", "content": "<SYSTEM_PROMPT>" },
       { "role": "user",   "content": "<USER_PROMPT>"  }
     ],
     "stream": false,
     "temperature": 0.2
   }
   ```
2. Encerrar en entorno **minted** `json`.  
3. Añadir placeholders `<SYSTEM_PROMPT>` y `<USER_PROMPT>` claramente.

---

## 5&nbsp;· Schema *Pydantic* de Respuesta de IA  
**Archivo:** `04_desarrollo.tex` (`lst:desarrollo_ai-schema_response`)

| Campo | Acción |
|-------|--------|
| `id: int` | **Añadir** |
| `expected_solution` | Renombrar a `answer: str` |
| Revisar tipos (`difficulty`, `subject_id`, …) | Igualar a modelo real `AIExerciseOut` |
| Declarar `orm_mode = True` | Confirmar presente |

---

## 6&nbsp;· Estado del Proyecto  
**Archivo:** `02_estado_objetivos.tex` (Tabla `objetivos`)

- Cambiar fecha **[Junio 2025]** → **Junio 2024**  
- Marcar «Contenerización de la aplicación (Docker)» como **Completado (✓)** y riesgo **Bajo**

---

## 7&nbsp;· Referencias en `07_anexos.tex`

| Etiqueta | Acción |
|----------|--------|
| `lst:apx_useCourses_content` | Ruta correcta: `@services/api/endpoints/courses` |
| `lst:apx_axiosInterceptor_content` | `baseURL` debe ser `/api` |
| `lst:apx_mainFastAPI_content` | Prefijo routers: `/api` (ajustar `API_V1_STR`) |

---

## 8&nbsp;· DBML (Listado `apx_dbml_completo_contenido`)  
**Archivo:** `07_anexos.tex`

### Ajustes por tabla

| Tabla | Cambios |
|-------|---------|
| `users` | Eliminar `created_at`, `updated_at`; añadir tablas `users_providers`, `refresh_tokens` |
| `courses` | Eliminar `created_at`, `updated_at` |
| `subjects` | Eliminar `created_at`, `updated_at` |
| `themes` | Renombrar `title` → `name`; eliminar `created_at`, `updated_at` |
| `exercises` | Renombrar `expected_solution` → `answer`; eliminar `updated_at` |
| Tablas de asociación | `user_enrolled_courses` → `user_courses` (sin `enrollment_date`)<br>`user_enrolled_subjects` → `user_enrollments` (sin `enrollment_date`, añadir `course_id`, PK correcta) |
| `user_theme_progress` | Campos: `completed`, `correct`, `updated_at` (nombres exactos) |
| `user_responses` | Eliminar `theme_id`, `feedback_provided`; usar `answer`, `created_at`; añadir `UniqueConstraint` |
| **Nuevas** | Crear `chat_conversations`, `chat_messages` conforme a modelos `SQLAlchemy` |

---

### Pasos recomendados

1. Exportar modelos `SQLAlchemy` a DBML con `sqlacodegen` o herramienta similar.  
2. Comparar y sincronizar campos, tipos y *foreign keys*.  
3. Regenerar la figura si se deriva de la especificación DBML.

---

> **Consejo:** crea un *branch* dedicado (`doc/fixes`) y aplica cada grupo de cambios en *commits* separados para facilitar la revisión por *pull request*.
