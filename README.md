# TutorVirtual

## Despliegue con Docker

Esta aplicación se puede desplegar fácilmente utilizando Docker y Docker Compose. A continuación, se detallan los pasos necesarios y la configuración de los servicios.

### Prerrequisitos

- Docker Desktop (o Docker Engine) instalado. Puedes encontrar las instrucciones de instalación en la [documentación oficial de Docker](https://docs.docker.com/get-docker/).
- Docker Compose.
    - Docker Compose V2 viene incluido con las instalaciones recientes de Docker Desktop y se invoca con `docker compose` (con espacio).
    - Si tienes una versión más antigua (Docker Compose V1, invocada con `docker-compose` con guion), considera actualizar, ya que V1 ya no recibe actualizaciones. Puedes encontrar más información [aquí](https://docs.docker.com/compose/install/).

### Estructura de Servicios
(...)


**Nota sobre `ollama-docker-compose.yml`:**
(...)

### Pasos para el Despliegue
(...)

---

### Explicación de Variables de Entorno
(...)

---
### Gestión y Prioridad de Variables de Entorno
(...)

---
### Notas Adicionales y Consideraciones

*   **Migraciones de Base de Datos (Alembic):**
    *   El `Dockerfile` de `tutor-backend` (ubicado en `tutor-backend/Dockerfile`) utiliza un `entrypoint.sh` que está diseñado para ejecutar las migraciones de base de datos (`alembic upgrade head`) antes de iniciar la aplicación FastAPI. Esto asegura que el esquema de la base de datos esté actualizado.
    *   Sin embargo, la directiva `command` en el servicio `backend` dentro de `docker-compose.yml` (`uvicorn src.main:create_app --factory --reload --host 0.0.0.0 --port 8000`) **anula el `CMD` por defecto del Dockerfile y podría también anular la ejecución del `ENTRYPOINT` si no está configurado para pasar el comando.**
    *   **Verificación:** Después de iniciar los servicios con `docker compose up`, verifica los logs del contenedor `backend` para confirmar si las migraciones se ejecutaron.
        ```bash
        docker compose logs backend
        ```
    *   **Ejecución Manual (si es necesario):** Si las migraciones no se aplican automáticamente, puedes ejecutarlas manualmente en el contenedor `backend` (mientras los demás servicios, especialmente `tutor_db`, están corriendo):
        ```bash
        docker compose exec backend alembic upgrade head
        ```
    *   **Solución Permanente (Recomendado):** Para asegurar que las migraciones siempre se ejecuten antes de que inicie el servidor, modifica el `command` en `docker-compose.yml` para el servicio `backend` de la siguiente manera:
        ```yaml
        services:
          backend:
            # ... otras configuraciones ...
            command: bash -c "alembic upgrade head && uvicorn src.main:create_app --factory --reload --host 0.0.0.0 --port 8000"
            # ...
        ```
        Esto primero ejecuta `alembic upgrade head` y, si tiene éxito (`&&`), entonces inicia el servidor Uvicorn.

*   **Configuración para Desarrollo vs. Producción:**
    La configuración actual en `docker-compose.yml` está optimizada para desarrollo. Para un entorno de producción, considera lo siguiente:
    *   **Recarga Automática del Backend (`--reload`):** La opción `--reload` en el comando de Uvicorn para el servicio `backend` es útil para desarrollo, ya que reinicia el servidor automáticamente con los cambios en el código. En producción, esto debe eliminarse para mejorar el rendimiento y la estabilidad.
        *Producción `command`: `bash -c "alembic upgrade head && uvicorn src.main:create_app --factory --host 0.0.0.0 --port 8000"`*
    *   **Montaje de Volúmenes de Código:** El montaje de directorios locales como volúmenes (ej., `./tutor-backend:/app`) permite que los cambios en el código fuente se reflejen instantáneamente en el contenedor, ideal para desarrollo. En producción, el código de la aplicación debe ser copiado dentro de la imagen Docker durante el proceso de `build` (usando `COPY` en el Dockerfile). Esto crea imágenes autocontenidas y más portables. Deberías eliminar o modificar estas monturas de volumen para producción.
    *   **Modo Debug:** Asegúrate de que cualquier modo de depuración en FastAPI o Vite esté desactivado en producción.
    *   **Servicio de Archivos Estáticos del Frontend:** El `Dockerfile` del frontend (`tutor-frontend/Dockerfile`) ya compila la aplicación Vite para producción (`npm run build`) y utiliza `serve` para servir los archivos estáticos. Esto es adecuado para producción.

*   **Conexión a `OLLAMA_URL`:**
    *   Como se mencionó en la sección de variables de entorno, el `docker-compose.yml` establece `OLLAMA_URL: "http://open-webui:8080"` para el servicio `backend`. Esto dirige las solicitudes del backend al servicio `open-webui` en su puerto interno `8080`.
    *   Si prefieres que el backend se comunique **directamente** con el servicio `ollama`, deberías cambiar esta variable en `docker-compose.yml` a `OLLAMA_URL: "http://ollama_service:11434"`.
    *   La elección depende de si `open-webui` actúa como un simple proxy, si añade alguna capa de gestión/API que el backend necesita, o si prefieres la comunicación directa.

*   **Archivo `ollama-docker-compose.yml`:**
    *   Este archivo parece ser una configuración alternativa o simplificada que solo define el servicio `open-webui` (y su dependencia implícita en Ollama, que podría estar corriendo externamente o ser manejado por la imagen de `open-webui` si esta lo incluye).
    *   Dado que el `docker-compose.yml` principal ya integra `ollama` y `open-webui` de manera completa con el resto de la aplicación (backend, frontend, db), **se recomienda utilizar el `docker-compose.yml` principal para el despliegue completo.**
    *   Para evitar confusiones, considera **eliminar el archivo `ollama-docker-compose.yml`** si no tiene un propósito específico y documentado que difiera del despliegue principal. Si se decide mantenerlo, su propósito debería ser claramente documentado en este README.

*   **Uso de GPU para Ollama y Open WebUI (Recordatorio):**
    *   Los servicios `ollama` y `open-webui` en `docker-compose.yml` están configurados para solicitar acceso a GPUs NVIDIA a través de la sección `deploy.resources`.
    *   **Si no tienes una GPU NVIDIA** o no deseas usarla, **debes comentar o eliminar la sección `deploy` completa** en la definición de *ambos* servicios dentro de `docker-compose.yml`. De lo contrario, Docker Compose podría intentar asignar recursos de GPU inexistentes y fallar, o los servicios podrían no iniciarse correctamente.
    *   Al eliminar esta sección, Ollama (y por extensión Open WebUI) funcionará utilizando la CPU, lo cual puede ser significativamente más lento para la inferencia de modelos grandes.

*   **Persistencia de Datos:**
    *   **Base de Datos (`tutor_db`):** Utiliza un volumen nombrado `db_data` para persistir los datos de PostgreSQL. Esto significa que los datos de tu base de datos sobrevivirán si detienes y reinicias los contenedores (ej. `docker compose down` y luego `docker compose up`). Sin embargo, si ejecutas `docker compose down -v`, el volumen `db_data` (y por lo tanto todos los datos de la BD) será eliminado.
    *   **Ollama (`ollama_service`):** Utiliza un volumen nombrado `ollama_data` para persistir los modelos de lenguaje descargados y otros datos de configuración de Ollama. Esto evita tener que volver a descargar modelos grandes cada vez que reinicias el servicio. Similar a `db_data`, `docker compose down -v` eliminará este volumen.
    *   **Open WebUI:** El servicio `open-webui` monta `./open-webui:/app/backend/data`. Esto significa que los datos de Open WebUI se guardarán en una carpeta llamada `open-webui` en el directorio raíz de tu proyecto en la máquina host.

Este README asume que estás ejecutando los comandos `docker compose` desde el directorio raíz del proyecto donde se encuentra el archivo `docker-compose.yml`.
```
