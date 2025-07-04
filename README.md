# TutorVirtual

## Despliegue con Docker

Esta aplicación se puede desplegar fácilmente utilizando Docker y Docker Compose. A continuación, se detallan los pasos necesarios y la configuración de los servicios.

### Prerrequisitos

- Docker instalado
- Docker Compose instalado

### Estructura de Servicios

El archivo `docker-compose.yml` define los siguientes servicios:

- **tutor_db**:
    - Imagen: `postgres:16`
    - Contenedor: `tutor_db`
    - Variables de entorno:
        - `POSTGRES_USER`: postgres
        - `POSTGRES_PASSWORD`: postgres
        - `POSTGRES_DB`: tutorvirtual
    - Puertos: `5432:5432`
    - Volúmenes: `db_data:/var/lib/postgresql/data` (para persistencia de datos)
- **backend**:
    - Construcción: a partir de `tutor-backend/Dockerfile`
    - Contenedor: `tutor_backend`
    - Depende de: `tutor_db`
    - Puertos: `8000:8000`
    - Variables de entorno:
        - `DATABASE_URL`: "postgresql://postgres:postgres@tutor_db:5432/tutorvirtual" (Configurada para la red Docker).
        - Otras variables (como `JWT_SECRET`, `GOOGLE_CLIENT_ID`, etc.) son cargadas por la aplicación FastAPI desde `tutor-backend/.env`.
    - Volúmenes: `./tutor-backend:/app` (monta el código local, permitiendo que `tutor-backend/.env` sea accesible).
    - Comando: Ejecuta las migraciones de Alembic (`alembic upgrade head`) y luego inicia el servidor Uvicorn (`uvicorn src.main:create_app --factory --host 0.0.0.0 --port 8000 --reload`).
- **frontend**:
    - Construcción: a partir de `tutor-frontend/Dockerfile`.
    - Contenedor: `tutor_frontend`.
    - Depende de: `backend`.
    - Puertos: `5173:5173`.
    - Variables de entorno:
        - `VITE_BACKEND_URL`: "http://localhost:8000" (URL para que el frontend se comunique con el backend).
        - Otras variables como `VITE_GOOGLE_CLIENT_ID` son cargadas por la aplicación Vite desde `tutor-frontend/.env`.

### Pasos para el Despliegue

1.  **Clonar el repositorio (si aún no lo has hecho):**
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-repositorio>
    ```

2.  **Preparar archivos `.env`:**
    *   **Para el Backend:**
        Navega a la carpeta `tutor-backend/`. Si no existe un archivo `.env` allí, cópialo desde el ejemplo general (que está en la raíz del proyecto):
        ```bash
        cd tutor-backend
        cp ../.env.example .env 
        # Si .env.example estuviera en tutor-backend/: cp .env.example .env
        cd .. 
        ```
        Luego, **edita `tutor-backend/.env`** con los valores correctos para `PORT`, `DATABASE_URL` (aunque el de Docker Compose suele tener precedencia si la app no lo define explícitamente), `JWT_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `OLLAMA_URL`, y `API_KEY`.
    *   **Para el Frontend:**
        Navega a la carpeta `tutor-frontend/`. Si no existe un archivo `.env` allí, puedes crear uno. Las variables relevantes del `.env.example` general son `VITE_BACKEND_URL` (aunque ya se pasa en `docker-compose.yml`) y `VITE_GOOGLE_CLIENT_ID`.
        ```bash
        cd tutor-frontend
        # Crea un archivo .env aquí si es necesario, por ejemplo:
        # echo "VITE_GOOGLE_CLIENT_ID=tu_id_de_cliente_google_para_frontend" > .env
        # echo "VITE_BACKEND_URL=http://localhost:8000" >> .env # Opcional si ya está en docker-compose
        cd ..
        ```
        Asegúrate de que los archivos `.env` específicos de cada subdirectorio (`tutor-backend/.env`, `tutor-frontend/.env`) estén en el `.gitignore` si decides usar esta estructura (ej. `tutor-backend/.env`, `tutor-frontend/.env`). El `.gitignore` actual cubre `*.env` globalmente, lo cual es bueno. El archivo `.env.example` general en la raíz sirve como plantilla maestra.

3.  **Construir y ejecutar los contenedores:**
    Desde el directorio raíz del proyecto (donde se encuentra `docker-compose.yml`), ejecuta:
    ```bash
    docker-compose up --build
    ```
    Para ejecuciones posteriores sin cambios en Dockerfiles:
    ```bash
    docker-compose up
    ```
    En segundo plano:
    ```bash
    docker-compose up -d
    ```

4.  **Acceder a la aplicación:**
    -   Frontend: `http://localhost:5173`
    -   Backend API: `http://localhost:8000` (docs en `http://localhost:8000/docs`)

5.  **Detener los contenedores:**
    `Ctrl+C` (si están en primer plano) o `docker-compose down` (si están en segundo plano o para detener y eliminar).
    Para eliminar volúmenes (¡cuidado, borra datos de BD!): `docker-compose down -v`

### Gestión Detallada de Variables de Entorno

-   **`.env.example` (Raíz del Proyecto):**
    Este archivo, ubicado en la raíz del proyecto, sirve como una **plantilla maestra** que documenta **todas** las variables de entorno que la aplicación (backend y frontend) podría necesitar. Es la fuente de verdad para saber qué configurar.

-   **Carga de Variables en el Backend (`tutor-backend/.env`):**
    -   La aplicación FastAPI (`tutor-backend/src/core/config.py`) está configurada para leer un archivo llamado `.env` desde su directorio de trabajo (que, dentro del contenedor Docker, es `/app`, correspondiente a `tutor-backend/` gracias al montaje de volumen).
    -   Por lo tanto, debes asegurarte de que exista un archivo `tutor-backend/.env` con las configuraciones necesarias para el backend. Puedes crearlo copiando las secciones relevantes del `.env.example` raíz.
    -   La variable `DATABASE_URL` en `docker-compose.yml` para el servicio `backend` anulará cualquier `DATABASE_URL` en `tutor-backend/.env` si la aplicación la lee de las variables de entorno del proceso antes que del archivo, o si `pydantic-settings` prioriza las variables de entorno del sistema/proceso. Generalmente, para la URL de la base de datos en Docker, es más robusto definirla en `docker-compose.yml` para asegurar que apunta al servicio de base de datos de Docker (`tutor_db`).

-   **Carga de Variables en el Frontend (`tutor-frontend/.env`):**
    -   Las aplicaciones Vite (como el frontend) cargan variables de entorno desde archivos `.env` en la raíz del proyecto frontend (`tutor-frontend/`). Solo las variables prefijadas con `VITE_` son expuestas al código del cliente.
    -   Debes crear un archivo `tutor-frontend/.env` con las variables como `VITE_GOOGLE_CLIENT_ID`.
    -   La variable `VITE_BACKEND_URL` se pasa explícitamente en `docker-compose.yml` al entorno del contenedor frontend, lo que generalmente tiene precedencia o es la forma más directa de configurar la URL del backend para el entorno de Docker.

-   **Prioridad de Carga (General):**
    1.  Variables pasadas directamente en `docker-compose.yml` en la sección `environment` de un servicio.
    2.  Variables de entorno del shell del host (si se usa interpolación como `${VAR_HOST}` en `docker-compose.yml`).
    3.  Variables definidas en un archivo `.env` en la raíz del proyecto Docker Compose (usadas por `docker-compose` mismo para interpolación).
    4.  Variables definidas en un archivo `.env` específico de la aplicación (ej. `tutor-backend/.env`) cargadas por el código de la aplicación.

-   **Seguridad:**
    -   **Nunca subas archivos `.env` reales a Git.** El `.gitignore` ya está configurado para esto (`*.env`).
    -   Para producción, considera mecanismos más seguros para gestionar secretos que archivos `.env` en el servidor (ej. variables de entorno del sistema host, Docker secrets, servicios de gestión de secretos en la nube).

### Notas Adicionales

-   **Migraciones de Base de Datos:** El servicio `backend` ejecuta `alembic upgrade head` al inicio.
-   **Desarrollo vs. Producción:**
    -   **Recarga del Backend:** El comando del backend en `docker-compose.yml` incluye `--reload`. Elimínalo para producción.
    -   **Montaje de Código:** El montaje de código local es para desarrollo. En producción, copia el código en la imagen.
    -   **JWT_SECRET:** Usa una clave fuerte y única en producción (ver `.env.example` para cómo generarla).
    -   **OLLAMA_URL:** Configura `OLLAMA_URL` en `tutor-backend/.env` según la ubicación de tu servicio Ollama:
        -   Si Ollama es otro servicio en el mismo `docker-compose.yml` (ej. llamado `ollama_service`): `http://ollama_service:11434` (o el puerto que use).
        -   Si Ollama corre en la máquina host (fuera de Docker, pero accesible desde Docker Desktop): `http://host.docker.internal:PUERTO_OLLAMA`.
        -   Si Ollama es un servicio externo: `https://tu.ollama.externo/api`.
-   **Dockerfile del Frontend:** Compila para producción y sirve estáticos.
    -   **Dockerfile del Frontend:** El `tutor-frontend/Dockerfile` está configurado para construir la aplicación de frontend para producción (`npm run build`) y luego servir los archivos estáticos resultantes usando `serve`. Esto es una práctica estándar para desplegar aplicaciones frontend.
-   **Ollama Docker Compose:** Existe un archivo `ollama-docker-compose.yml` en el repositorio. Este archivo parece estar destinado a una configuración separada o alternativa que podría incluir un servicio `ollama` (posiblemente para inferencia de modelos de lenguaje). Las instrucciones y configuraciones en este `README.md` se centran en el despliegue principal de la aplicación definido en el archivo `docker-compose.yml` principal. Si necesitas información sobre cómo desplegar o usar la configuración relacionada con Ollama, deberás consultar `ollama-docker-compose.yml` y posiblemente documentación adicional específica para esa parte del sistema.
