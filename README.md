# Guía de Dockerización de la Aplicación Tutor Virtual

Esta guía describe cómo construir, ejecutar y gestionar la aplicación Tutor Virtual utilizando Docker y Docker Compose.

## Prerrequisitos

- Docker instalado ([https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/))
- Docker Compose instalado (generalmente viene con Docker Desktop)

## Estructura de Servicios

La aplicación se compone de tres servicios principales orquestados por `docker-compose.yml`:

1.  **`tutor_db`**:
    *   Imagen: `postgres:16`
    *   Propósito: Base de datos PostgreSQL para la aplicación.
    *   Puerto expuesto (host:contenedor): `5432:5432`
    *   Datos: Persistidos en un volumen Docker llamado `db_data`.
    *   Credenciales por defecto (ver `docker-compose.yml`):
        *   Usuario: `postgres`
        *   Contraseña: `postgres`
        *   Base de datos: `tutorvirtual`

2.  **`backend`**:
    *   Construcción: A partir de `tutor-backend/Dockerfile`.
    *   Propósito: API de FastAPI escrita en Python.
    *   Puerto expuesto (host:contenedor): `8000:8000`.
    *   Dependencias: `tutor_db`. Espera a que la base de datos esté saludable antes de iniciar.
    *   Migraciones: Las migraciones de Alembic se aplican automáticamente al iniciar el contenedor gracias a un script `entrypoint.sh`.
    *   Variables de entorno: Configuradas a través de `tutor-backend/.env`. La `DATABASE_URL` se define en `docker-compose.yml` para conectarse a `tutor_db`.
    *   Hot Reloading: Habilitado para desarrollo, el código fuente de `tutor-backend` está montado en el contenedor.

3.  **`frontend`**:
    *   Construcción: A partir de `tutor-frontend/Dockerfile`.
    *   Propósito: Aplicación de React/Vite.
    *   Puerto expuesto (host:contenedor): `5173:5173`.
    *   Dependencias: `backend`.
    *   Configuración: Sirve los archivos estáticos compilados (del directorio `dist`).
    *   Variables de entorno: La `VITE_BACKEND_URL` se define en `docker-compose.yml` para apuntar al servicio `backend`. Otras variables se pueden gestionar mediante `tutor-frontend/.env`.

## Configuración de Variables de Entorno

Antes de construir y ejecutar, asegúrate de tener los archivos `.env` necesarios:

1.  **`tutor-backend/.env`**:
    *   Copia `tutor-backend/.env.example` a `tutor-backend/.env` si aún no existe.
    *   Rellena las variables necesarias como `JWT_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OLLAMA_URL`, etc.
    *   La `DATABASE_URL` es proporcionada por `docker-compose.yml` y no necesita estar en este archivo cuando se ejecuta con Docker.

2.  **`tutor-frontend/.env`**:
    *   Crea este archivo si necesitas configurar variables específicas del frontend, por ejemplo, `VITE_GOOGLE_CLIENT_ID`.
    *   La `VITE_BACKEND_URL` es proporcionada por `docker-compose.yml`.

3.  **`.env` (en la raíz del proyecto, junto a `docker-compose.yml`):**
    *   Docker Compose puede cargar variables de un archivo `.env` en el mismo directorio que `docker-compose.yml`. Esto se puede usar para centralizar algunas configuraciones si se desea, aunque la configuración actual favorece los `.env` específicos de cada servicio.

## Script Entrypoint para Migraciones del Backend (`tutor-backend/entrypoint.sh`)

Para asegurar que las migraciones de la base de datos se apliquen automáticamente, el servicio `backend` utilizará un script de entrada. Crea el archivo `tutor-backend/entrypoint.sh` con el siguiente contenido:

```bash
#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# Aplicar migraciones de base de datos
echo "Aplicando migraciones de base de datos..."
alembic upgrade head

# Ejecutar el comando pasado como argumentos a este script (CMD del Dockerfile)
exec "$@"
```

Asegúrate de que este script tenga permisos de ejecución:
`chmod +x tutor-backend/entrypoint.sh`

Y modifica `tutor-backend/Dockerfile` para usar este entrypoint:
```dockerfile
# ... (otras instrucciones) ...

# Copiamos el resto del código
COPY . .

# Copiar y dar permisos al entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exponer el puerto en el contenedor
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
# Comando para iniciar la app
CMD ["uvicorn", "src.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```
*(Nota: El `CMD` en `docker-compose.yml` para el backend (`uvicorn src.main:create_app --factory --reload`) anulará el `CMD` del Dockerfile. El `entrypoint.sh` seguirá ejecutándose, y luego ejecutará el comando de `docker-compose.yml`)*.

## Comandos Docker

### 1. Construir las imágenes

Desde la raíz del proyecto (donde está `docker-compose.yml`):

```bash
docker-compose build
```

Este comando leerá los `Dockerfile` de `tutor-backend` y `tutor-frontend` y construirá las imágenes correspondientes.

### 2. Iniciar todos los servicios

```bash
docker-compose up
```
O para ejecutar en segundo plano (detached mode):
```bash
docker-compose up -d
```
Esto iniciará `tutor_db`, luego `backend` (aplicando migraciones), y finalmente `frontend`.

Podrás acceder a:
-   Frontend: `http://localhost:5173`
-   Backend API: `http://localhost:8000`
-   Base de datos (si tienes un cliente PG): `localhost:5432`

### 3. Ver logs de los contenedores

Si los contenedores se ejecutan en segundo plano:
```bash
docker-compose logs -f
```
Para ver los logs de un servicio específico (e.g., `backend`):
```bash
docker-compose logs -f backend
```

### 4. Detener los servicios

```bash
docker-compose down
```
Esto detendrá y eliminará los contenedores. Los datos de la base de datos persistidos en el volumen `db_data` no se eliminarán.
Si deseas eliminar también los volúmenes (¡CUIDADO! Esto borrará los datos de la BD):
```bash
docker-compose down -v
```

### 5. Ejecutar comandos dentro de un contenedor

Por ejemplo, para abrir un shell en el contenedor del backend:
```bash
docker-compose exec backend bash
```
Una vez dentro, puedes ejecutar comandos como `alembic current` o gestionar la aplicación.

### 6. Reconstruir una imagen específica y reiniciar

Si haces cambios en el `Dockerfile` o en el código fuente de un servicio (e.g., `backend`) y necesitas reconstruir:

```bash
docker-compose build backend
docker-compose up -d --no-deps backend 
```
La opción `--no-deps` evita reiniciar los servicios dependientes si no es necesario.

## Flujo de Migraciones de Alembic

Como se mencionó, las migraciones se aplican automáticamente al iniciar el servicio `backend` gracias al script `entrypoint.sh`.

Si necesitas crear una nueva migración:
1.  Asegúrate de que los servicios (al menos `tutor_db` y `backend`) estén corriendo: `docker-compose up -d`
2.  Ejecuta el comando de Alembic para generar la revisión dentro del contenedor del backend:
    ```bash
    docker-compose exec backend alembic revision -m "nombre_descriptivo_de_la_migracion"
    ```
3.  Esto creará un nuevo archivo de migración en `tutor-backend/migrations/versions/`.
4.  Edita este archivo según sea necesario.
5.  La próxima vez que el backend se inicie (o si lo reinicias: `docker-compose restart backend`), el `entrypoint.sh` aplicará la nueva migración.

Alternativamente, para aplicar la nueva migración sin reiniciar:
```bash
docker-compose exec backend alembic upgrade head
```

## Consideraciones Adicionales

*   **Producción**: Para un despliegue en producción, el `CMD` del backend en `docker-compose.yml` debería modificarse para no usar `--reload`. Por ejemplo:
    ```yaml
    services:
      backend:
        # ...
        # CMD del Dockerfile se usará si command no está aquí, o define uno específico para prod:
        # command: uvicorn src.main:create_app --factory --host 0.0.0.0 --port 8000
    ```
    El `Dockerfile` del frontend ya construye para producción y sirve archivos estáticos, lo cual es adecuado.
*   **Seguridad de Secretos**: Para producción, considera métodos más seguros para gestionar secretos que archivos `.env` versionados (e.g., Docker secrets, HashiCorp Vault, variables de entorno inyectadas por el sistema CI/CD).

Este documento proporciona una base sólida para trabajar con la aplicación en un entorno Docker.
```
