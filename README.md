# TutorVirtual: Plataforma Educativa Inteligente

Bienvenido a TutorVirtual, una plataforma educativa diseñada para ofrecer una experiencia de aprendizaje interactiva y personalizada, potenciada por inteligencia artificial.

## Tabla de Contenidos

1.  [Prerrequisitos](#prerrequisitos)
2.  [Estructura de Servicios Docker](#estructura-de-servicios-docker)
3.  [Configuración Inicial: Variables de Entorno (`.env`)](#configuración-inicial-variables-de-entorno-env)
    *   [Variables del Backend (`tutor-backend/.env`)](#variables-del-backend-tutor-backendenv)
    *   [Variables del Frontend (`tutor-frontend/.env`)](#variables-del-frontend-tutor-frontendenv)
4.  [Pasos para el Despliegue](#pasos-para-el-despliegue)
    *   [Opción 1: Despliegue desde Repositorio GitHub](#opción-1-despliegue-desde-repositorio-github-recomendado-para-usuarios-finales)
    *   [Opción 2: Despliegue y Desarrollo desde Código Fuente (Recomendado para el Tribunal TFG)](#opción-2-despliegue-y-desarrollo-desde-código-fuente-para-desarrolladores)
5.  [Acceder a la Aplicación](#acceder-a-la-aplicación)
6.  [Detener la Aplicación](#detener-la-aplicación)
7.  [Gestión y Prioridad de Variables de Entorno en Docker](#gestión-y-prioridad-de-variables-de-entorno-en-docker)
8.  [Notas Adicionales y Consideraciones](#notas-adicionales-y-consideraciones)
    *   [Migraciones de Base de Datos (Alembic)](#migraciones-de-base-de-datos-alembic)
    *   [Configuración para Desarrollo vs. Producción](#configuración-para-desarrollo-vs-producción)
    *   [Conexión a `OLLAMA_URL`](#conexión-a-ollama_url)
    *   [Archivo `ollama-docker-compose.yml`](#archivo-ollama-docker-composeyml)
    *   [Uso de GPU para Ollama y Open WebUI](#uso-de-gpu-para-ollama-y-open-webui)
    *   [Persistencia de Datos](#persistencia-de-datos)
9.  [Flujo de Prueba para Generación de Ejercicios (Tribunal TFG)](#9-flujo-de-prueba-para-generación-de-ejercicios-tribunal-tfg)

---

## 1. Prerrequisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

*   **Docker Desktop (o Docker Engine):** Necesario para construir y ejecutar los contenedores de la aplicación.
    *   Instrucciones de instalación: [Documentación oficial de Docker](https://docs.docker.com/get-docker/)
*   **Docker Compose:** Herramienta para definir y ejecutar aplicaciones Docker multi-contenedor.
    *   **Docker Compose V2 (recomendado):** Viene incluido con las instalaciones recientes de Docker Desktop y se invoca con el comando `docker compose` (con espacio).
    *   **Docker Compose V1 (antiguo):** Se invoca con `docker-compose` (con guion). Si tienes esta versión, considera actualizar, ya que V1 no recibe más actualizaciones. Más información [aquí](https://docs.docker.com/compose/install/).

    *Este README utilizará la sintaxis de Docker Compose V2 (`docker compose`). Si usas V1, simplemente reemplaza `docker compose` por `docker-compose` en los comandos.*

---

## 2. Estructura de Servicios Docker

El archivo `docker-compose.yml` en la raíz del proyecto orquesta los siguientes servicios:

*   **`tutor_db` (Base de Datos):**
    *   **Imagen:** `postgres:16`
    *   **Descripción:** Servicio de base de datos PostgreSQL que almacena todos los datos de la aplicación (usuarios, cursos, progreso, etc.).
    *   **Persistencia:** Los datos se guardan en un volumen Docker llamado `db_data` para asegurar que no se pierdan al detener o reiniciar los contenedores.
    *   **Puerto expuesto (host:contenedor):** `5432:5432`

*   **`backend` (Servidor Principal):**
    *   **Construcción:** A partir del `Dockerfile` en `tutor-backend/`.
    *   **Descripción:** El núcleo de la aplicación, una API desarrollada con FastAPI (Python) que maneja la lógica de negocio, autenticación, interacciones con la base de datos y comunicación con los servicios de IA.
    *   **Dependencias:** Se inicia después de que `tutor_db` esté saludable.
    *   **Puerto expuesto (host:contenedor):** `8000:8000`
    *   **Variables de entorno clave (desde `docker-compose.yml`):**
        *   `DATABASE_URL`: Apunta a `tutor_db`.
        *   `OLLAMA_URL`: Apunta a `open-webui` (ver más abajo).
    *   **Volumen (desarrollo):** Monta `./tutor-backend:/app` para reflejar cambios en el código local inmediatamente.

*   **`frontend` (Interfaz de Usuario):**
    *   **Construcción:** A partir del `Dockerfile` en `tutor-frontend/`.
    *   **Descripción:** La interfaz web con la que los usuarios interactúan, desarrollada con React (Vite).
    *   **Dependencias:** Depende del servicio `backend`.
    *   **Puerto expuesto (host:contenedor):** `5173:5173`
    *   **Variable de entorno clave (desde `docker-compose.yml`):**
        *   `VITE_BACKEND_URL`: Apunta al servicio `backend` (`http://localhost:8000`).

*   **`ollama` (Servicio de Inferencia LLM):**
    *   **Imagen:** `ollama/ollama`
    *   **Descripción:** Permite ejecutar modelos de lenguaje grandes (LLMs) localmente. Esencial para las funcionalidades de IA de TutorVirtual.
    *   **Persistencia:** Los modelos descargados se guardan en el volumen `ollama_data`.
    *   **Puerto expuesto (host:contenedor):** `11434:11434`
    *   **Uso de GPU:** Configurado para usar GPUs NVIDIA si están disponibles. **Ver la sección [Uso de GPU](#uso-de-gpu-para-ollama-y-open-webui) para instrucciones si no tienes GPU.**

*   **`open-webui` (Interfaz para Ollama):**
    *   **Imagen:** `ghcr.io/open-webui/open-webui:ollama`
    *   **Descripción:** Una interfaz de usuario web amigable para interactuar y gestionar los modelos de Ollama. El backend de TutorVirtual se comunica con Ollama a través de esta interfaz según la configuración por defecto.
    *   **Persistencia:** Sus datos se guardan en `./open-webui` en el host.
    *   **Puerto expuesto (host:contenedor):** `3000:8080` (Accedes a Open WebUI en el puerto `3000` de tu host).
    *   **Uso de GPU:** También configurado para GPUs NVIDIA. **Ver la sección [Uso de GPU](#uso-de-gpu-para-ollama-y-open-webui) para instrucciones si no tienes GPU.**

---

## 3. Configuración Inicial: Variables de Entorno (`.env`)

Antes de iniciar la aplicación, necesitas configurar variables de entorno específicas para el backend y el frontend. Estas contienen información sensible como claves API y secretos de configuración.

**Procedimiento General:**
1.  Localiza el archivo `.env.example` en los directorios `tutor-backend/` y `tutor-frontend/`.
2.  Copia cada `.env.example` a un nuevo archivo llamado `.env` en su respectivo directorio.
    *   En `tutor-backend/`: `cp .env.example .env`
    *   En `tutor-frontend/`: `cp .env.example .env`
3.  Edita los archivos `.env` recién creados con tus valores específicos.

**¡Importante!** Los archivos `.env` contienen información sensible y **NUNCA** deben ser subidos a repositorios Git. El archivo `.gitignore` del proyecto ya está configurado para excluirlos. Por esto no adjunto determinados datos reales en el `.env.example`.

### Variables del Backend (`tutor-backend/.env`)

Edita `tutor-backend/.env` con la siguiente información:

*   `PORT=8000`
    *   **Descripción:** Puerto interno en el que escuchará el servidor FastAPI.
    *   **Acción:** No necestia cambios.

*   `DATABASE_URL="postgresql://postgres:Talaveranaranjo7@localhost:5432/tutorvirtual"`
    *   **Descripción:** URL de conexión a PostgreSQL.
    *   **Acción en Docker:** Este valor es **ignorado** cuando se ejecuta con `docker compose`, ya que `docker-compose.yml` provee `DATABASE_URL="postgresql://postgres:postgres@tutor_db:5432/tutorvirtual"` que apunta al servicio Docker de la base de datos. El valor en `.env` se usaría si ejecutas el backend directamente en tu host fuera de Docker.

*   `JWT_SECRET="...tu_secreto_aqui..."`
    *   **Descripción:** Clave secreta para firmar y verificar JSON Web Tokens (JWT) para la autenticación.
    *   **Acción:** **¡CRÍTICO!** Reemplaza el valor de ejemplo por una cadena larga, aleatoria y segura. Puedes generar una con: `openssl rand -hex 32`, o bien hacer uso de la que se presta en `.env.example`.

*   `GOOGLE_CLIENT_ID="...tu_client_id.apps.googleusercontent.com"`
    *   **Descripción:** ID de Cliente OAuth 2.0 de Google para la funcionalidad "Iniciar sesión con Google".
    *   **Acción:** Obtén esto desde la [Consola de Google Cloud](https://console.cloud.google.com/apis/credentials) creando credenciales de tipo "ID de cliente de OAuth 2.0" para una "Aplicación web". No adjunto la mía en este repositorio Git por seguridad.

*   `GOOGLE_CLIENT_SECRET="...tu_google_client_secret..."`
    *   **Descripción:** Secreto de Cliente OAuth 2.0 de Google.
    *   **Acción:** Se obtiene junto con el `GOOGLE_CLIENT_ID` desde la Consola de Google Cloud.

*   `GOOGLE_REDIRECT_URI="http://localhost:5173"`
    *   **Descripción:** URI al que Google redirigirá después de una autenticación exitosa.
    *   **Acción:** Debe coincidir exactamente con uno de los "URI de redireccionamiento autorizados" configurados en tus credenciales de Google Cloud. Para desarrollo local, `http://localhost:5173` (URL del frontend) es común.

*   `OLLAMA_URL="http://localhost:3000"`
    *   **Descripción:** URL del servicio Ollama o su interfaz (Open WebUI).
    *   **Acción en Docker:** Este valor es **ignorado** cuando se ejecuta con `docker compose`, ya que `docker-compose.yml` provee `OLLAMA_URL="http://open-webui:8080"` que apunta al servicio Docker de Open WebUI. El valor en `.env` se usaría si ejecutas el backend directamente.

*   `API_KEY="...tu_api_key..."`
    *   **Descripción:** Clave API genérica para usar "OpenWeb UI como RAG".
    *   **Acción:** Verifica la documentación de Open WebUI para saber cómo obtenerla y su propósito.

*   `ADMIN_EMAIL="admin@example.com"`
*   `ADMIN_USERNAME="admin"`
*   `ADMIN_PASSWORD="SecureAdminPassword123!"`
    *   **Descripción:** Credenciales para un usuario administrador inicial (puedes usarlo para pruebas).

### Variables del Frontend (`tutor-frontend/.env`)

Edita `tutor-frontend/.env` con la siguiente información:

*   `VITE_BACKEND_URL=http://localhost:8000`
    *   **Descripción:** URL base del backend al que el frontend hará peticiones.
    *   **Acción en Docker:** Este valor es **ignorado** si `VITE_BACKEND_URL` está definida en la sección `environment` del servicio `frontend` en `docker-compose.yml` (que es el caso, y está correctamente configurada a `http://localhost:8000`). `localhost:8000` en el navegador se resuelve al puerto del host mapeado al servicio backend.

*   `VITE_GOOGLE_CLIENT_ID="...tu_client_id.apps.googleusercontent.com"`
    *   **Descripción:** ID de Cliente OAuth 2.0 de Google (el mismo que en `tutor-backend/.env`).
    *   **Acción:** Necesario para que el SDK de Google en el frontend inicie el flujo de autenticación. Asegúrate de que este ID de cliente en Google Cloud tenga `http://localhost:5173` (URL del frontend) listado en "Orígenes de JavaScript autorizados".

---

## 4. Pasos para el Despliegue

Elige una de las siguientes opciones para desplegar TutorVirtual.

### Opción 1: Despliegue desde Repositorio GitHub

Esta opción es la más sencilla si solo quieres ejecutar la aplicación sin posibilidad de realizar ejercicios o ver el chat bot.

1.  **Clonar el Repositorio:**
    ```bash
    git clone https://github.com/AdriTN/TutorVirtual.git 
    cd tu_repositorio 
    ```

2.  **Configurar Variables de Entorno:**
    *   Navega a `tutor-backend/` y crea/edita tu archivo `.env` como se describe en la sección [Variables del Backend](#variables-del-backend-tutor-backendenv).
    *   Navega a `tutor-frontend/` y crea/edita tu archivo `.env` como se describe en la sección [Variables del Frontend](#variables-del-frontend-tutor-frontendenv).
    *   Regresa al directorio raíz del proyecto.

3.  **(Opcional) Ajustes para Equipos sin GPU:**
    Si no tienes una GPU NVIDIA, edita el archivo `docker-compose.yml` y comenta o elimina los servicios `ollama` y `open-webui` como se detalla en la sección [Uso de GPU](#uso-de-gpu-para-ollama-y-open-webui).

4.  **Construir y Ejecutar:**
    Desde el directorio raíz del proyecto (donde está `docker-compose.yml`):
    ```bash
    docker compose up --build
    ```
    *   `--build`: Construye las imágenes si no existen o si los Dockerfiles cambiaron.
    *   La primera vez puede tardar un poco mientras se descargan las imágenes base y se construyen las de la aplicación.

5.  **Acceder a la Aplicación:**
    Consulta la sección [Acceder a la Aplicación](#acceder-a-la-aplicación).

### Opción 2: Despliegue y Desarrollo desde Código Fuente (Recomendado para el Tribunal TFG)

Esta opción es para el Tribunal de este TFG que quiera visualizar la aplicación y probarla.

1.  **Obtener el Código Fuente:**
    *   Clona el repositorio (si aún no lo has hecho).
        ```bash
        git clone https://github.com/AdriTN/TutorVirtual.git
        cd tu_repositorio
        ```

2.  **Configurar Variables de Entorno:**
    *   En este caso no hace falta configurar las variables de entorno ya que el `.zip` facilitado con el código fuente hace uso de mis variables de entorno personales. Por favor, **no las difundas**, solo las he compartido por comodidad para las pruebas.

3.  **(Opcional) Ajustes para Equipos sin GPU:**
    *   Si no tienes una GPU NVIDIA, modifica `docker-compose.yml` como se describe en la "Opción 1" y se detalla en la sección [Uso de GPU](#uso-de-gpu-para-ollama-y-open-webui).

4.  **Construir y Ejecutar:**
    Desde el directorio raíz del proyecto:
    ```bash
    docker compose up --build
    ```
    *   La opción `--build` es importante si has modificado los `Dockerfile` o si es la primera vez que construyes las imágenes.
    *   **Recarga en Caliente:** Gracias a los volúmenes montados en `docker-compose.yml` (ej. `./tutor-backend:/app`) y a las herramientas de desarrollo (Uvicorn con `--reload` para el backend, Vite HMR para el frontend), los cambios que hagas en el código fuente de `tutor-backend/` o `tutor-frontend/` deberían reflejarse automáticamente en los contenedores en ejecución (el backend se reiniciará, el frontend se actualizará en el navegador).

5.  **Verificar Logs y Estado:**
    *   Si ejecutas sin `-d`, los logs se mostrarán en tu terminal.
    *   Si ejecutas con `-d`, puedes ver los logs con: `docker compose logs -f` (todos los servicios) o `docker compose logs -f backend`, `docker compose logs -f frontend` (un servicio específico).
    *   Verifica el estado de los contenedores: `docker compose ps`

6.  **Acceder a la Aplicación:**
    Consulta la sección [Acceder a la Aplicación](#acceder-a-la-aplicación).

---

## 5. Acceder a la Aplicación

Una vez que los contenedores estén en funcionamiento:

*   **Frontend (Interfaz Principal):** `http://localhost:5173`
*   **Backend API (Documentación Swagger/OpenAPI):** `http://localhost:8000/docs`
*   **Open WebUI (Interfaz para Ollama):** `http://localhost:3000` (si los servicios `ollama` y `open-webui` están activos).

:::nota
> Recuerda que el proyecto se ejecuta en local y que **Open WebUI** requiere de un inicio de sesión.
:::

---

## 6. Detener la Aplicación

*   **Si se ejecuta en primer plano:** Presiona `Ctrl+C` en la terminal donde `docker compose up` está corriendo.
*   **Si se ejecuta en segundo plano (modo `-d`) o para una detención completa:**
    Desde el directorio raíz del proyecto:
    ```bash
    docker compose down
    ```
*   **Para detener Y eliminar los volúmenes de datos** (¡PRECAUCIÓN! Borrará datos de BD y modelos Ollama):
    ```bash
    docker compose down -v
    ```

---

## 7. Gestión y Prioridad de Variables de Entorno en Docker

Esta sección pretende comprender cómo se cargan y priorizan las variables de entorno para una configuración correcta en un entorno Dockerizado.

*   **Archivos `.env.example` vs. `.env`**:
    *   Los archivos con extensión `.env.example` (ej., `tutor-backend/.env.example`) son **plantillas**. Deben incluirse en el control de versiones (Git) y sirven como guía de las variables requeridas por cada servicio. **No deben contener valores sensibles o secretos reales.**
    *   Los archivos con extensión `.env` (ej., `tutor-backend/.env`) contienen los **valores reales** de las variables para un entorno específico. Estos archivos son leídos por las aplicaciones (FastAPI en el backend, Vite en el frontend) en tiempo de ejecución. **NUNCA deben subirse al control de versiones (Git)**. El archivo `.gitignore` del proyecto ya está (y debe estar) configurado para ignorar `*.env` globalmente.

*   **Ubicación de los Archivos `.env`**:
    *   El backend (FastAPI) espera encontrar un archivo `.env` en su directorio de trabajo, que dentro del contenedor Docker es `/app/` (mapeado desde `./tutor-backend/` en el host). Por lo tanto, el archivo debe ser `tutor-backend/.env`.
    *   El frontend (Vite) espera encontrar un archivo `.env` en la raíz de su proyecto, es decir, `tutor-frontend/.env`. Vite solo expone al código del navegador las variables prefijadas con `VITE_`.

*   **Prioridad de Carga de Variables en Docker Compose**:
    Cuando se trabaja con Docker Compose, las variables de entorno para los servicios pueden provenir de varias fuentes. El orden de precedencia general (de mayor a menor) es:

    1.  **Variables definidas en la sección `environment` de un servicio en `docker-compose.yml`**:
        Estas variables se inyectan directamente en el entorno del contenedor y tienen la máxima prioridad. Anularán cualquier variable con el mismo nombre proveniente de otras fuentes para ese servicio específico.
        *Ejemplo: En `docker-compose.yml`, `DATABASE_URL` y `OLLAMA_URL` para el servicio `backend`, y `VITE_BACKEND_URL` para el servicio `frontend`.*

    2.  **Variables de entorno del shell del host (si se usa interpolación)**:
        Si en `docker-compose.yml` se utiliza la sintaxis de interpolación (ej., `VARIABLE_EN_COMPOSE: ${VARIABLE_DEL_HOST}`), Docker Compose intentará reemplazar `${VARIABLE_DEL_HOST}` con el valor de una variable de entorno existente en el shell donde se ejecuta `docker compose up`. Si no se encuentra, generalmente se usa una cadena vacía (a menos que se defina un valor predeterminado). *Este método no se usa prominentemente en la configuración actual para las variables principales de la aplicación.*

    3.  **Variables definidas en un archivo `.env` en el directorio raíz del proyecto Docker Compose**:
        Si existe un archivo llamado `.env` en el mismo directorio que `docker-compose.yml`, Docker Compose lo leerá automáticamente. Estas variables se utilizan para la [sustitución de variables dentro del propio archivo `docker-compose.yml`](https://docs.docker.com/compose/environment-variables/set-environment-variables/#substitute-with-an-env-file) y también pueden ser pasadas a los contenedores si no se anulan por los métodos anteriores.

    4.  **Variables definidas en archivos `.env` específicos de la aplicación (cargadas por el código de la aplicación)**:
        Estas son las variables en `tutor-backend/.env` y `tutor-frontend/.env`. Son leídas por el código de la aplicación (FastAPI o Vite) después de que el contenedor se ha iniciado. Si una variable ya fue establecida en el entorno del contenedor por Docker Compose (método 1), ese valor del entorno generalmente tiene precedencia sobre el valor en el archivo `.env` de la aplicación, dependiendo de cómo la aplicación cargue su configuración (muchas librerías de configuración priorizan variables de entorno del sistema sobre las de archivos `.env`).
        *En la configuración actual, `DATABASE_URL` y `OLLAMA_URL` para el backend, y `VITE_BACKEND_URL` para el frontend, son establecidas por Docker Compose (método 1), por lo que los valores para estas claves específicas en los archivos `.env` de las aplicaciones no tendrán efecto cuando se ejecuten dentro de Docker.*

*   **Conclusión sobre Prioridad para esta Aplicación**:
    *   Para la comunicación entre contenedores (como `DATABASE_URL`, `OLLAMA_URL` del backend) y configuraciones esenciales para el entorno Docker (como `VITE_BACKEND_URL` del frontend), **los valores en `docker-compose.yml` son los que mandan.**
    *   Para otras variables específicas de la aplicación (como `JWT_SECRET`, credenciales de Google, `API_KEY`, `ADMIN_*`), estas deben configurarse en los archivos `tutor-backend/.env` y `tutor-frontend/.env` respectivamente, ya que la aplicación las leerá desde allí.

*   **Seguridad de Secretos en Producción**:
    Para entornos de producción, almacenar secretos directamente en archivos `.env` en el servidor puede no ser la práctica más segura. Se pueden considera alternativas más robustas como:
    *   **Variables de entorno inyectadas por el sistema host o el orquestador de contenedores:** Por ejemplo, definidas a nivel del sistema operativo del servidor o mediante mecanismos de secretos de plataformas como Kubernetes (Secrets), Docker Swarm (Secrets), o servicios PaaS.
    -   **Servicios de gestión de secretos dedicados:** Herramientas como HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, o Google Cloud Secret Manager proporcionan almacenamiento seguro y gestión centralizada de secretos con control de acceso granular.

---

## 8. Notas Adicionales y Consideraciones

*   **Archivo `ollama-docker-compose.yml`:**
    *   Este archivo sirve para desplegar en el host local el servicio de Open WebUI. Esto es para facilitar el desarrollo del programa.

*   **Uso de GPU para Ollama y Open WebUI:**
    *   Los servicios `ollama` y `open-webui` están configurados para GPUs NVIDIA.
    *   **Sin GPU NVIDIA:** **Comenta o elimina los servicios `ollama` y `open-webui` completas** para usar CPU.
        ```yaml
        #  ollama:
        #    image: ollama/ollama
        #    container_name: ollama_service
        #    ports:
        #    - "11434:11434"
        #    volumes:
        #    - ollama_data:/root/.ollama
        #    restart: always
        #    deploy:
        #    resources:
        #        reservations:
        #        devices:
        #            - driver: nvidia
        #            count: all
        #            capabilities: [gpu]

        #  open-webui:
        #      image: ghcr.io/open-webui/open-webui:ollama
        #      ports:
        #      - "3000:8080"
        #      volumes:
        #      - ./ollama:/root/.ollama
        #      - ./open-webui:/app/backend/data
        #      restart: always
        #      deploy:
        #      resources:
        #          reservations:
        #          devices:
        #              - driver: nvidia
        #              count: all
        #              capabilities: [gpu]
        ```

*   **Persistencia de Datos:**
    *   `tutor_db`: Volumen `db_data` (persistente).
    *   `ollama`: Volumen `ollama_data` (modelos persistentes).
    *   `open-webui`: Datos en `./open-webui` en el host.
    *   `docker compose down -v` elimina estos volúmenes y datos.

---
Este README asume que los comandos `docker compose` se ejecutan desde el directorio raíz del proyecto.

---

## 9. Flujo de Prueba para Generación de Ejercicios (Tribunal TFG)

Esta sección describe los pasos recomendados para que un miembro del tribunal del TFG pueda probar la funcionalidad principal de generación de ejercicios. Se asume que la aplicación está desplegada y accesible según las instrucciones anteriores.

**Usuario Requerido:** Se recomienda realizar estos pasos con un usuario que tenga permisos de administrador para poder crear y gestionar cursos, asignaturas y temas. Puede utilizar el usuario administrador creado por defecto (ver `ADMIN_EMAIL`, `ADMIN_PASSWORD` en `tutor-backend/.env`).

**Pasos a seguir:**

1.  **Iniciar Sesión:**
    *   Accede al frontend de TutorVirtual (`http://localhost:5173`).
    *   Inicia sesión con el usuario administrador.

2.  **Navegar al Panel de Administración:**
    *   Una vez iniciada la sesión, busca en la barra de navegación o en el menú de usuario una opción que te lleve al "Panel de Administración" o "Admin Dashboard". En este caso en menú lateral hay una opción `Panel admin` habilitada para ello.

3.  **Crear un Nuevo Curso:**
    *   Dentro del panel de administración, localiza la sección "Catálogo".
    *   Crea un nuevo curso (ej. Nombre: "Curso de Prueba TFG", Descripción: "Curso para demostración").

4.  **Crear una Nueva Asignatura:**
    *   En el panel de administración, ve a la sección de "Catálogo".
    *   Crea una nueva asignatura (ej. Nombre: "Matemáticas de Prueba", Descripción: "Asignatura de prueba para TFG").

5.  **Crear un Nuevo Tema:**
    *   Dirígete a la sección "Catálogo" en el panel de administración.
    *   Crea un nuevo tema (ej. Nombre: "Números Naturales", Descripción: "Tema sobre operaciones aritméticas elementales").
    *   **Importante:** Al crear el tema, asegúrate de **vincularlo a la Asignatura** "Matemáticas de Prueba" creada en el paso anterior. Debería haber un selector o campo para esto.

6.  **Vincular la Asignatura al Curso:**
    *   Ve a la sección "Vínculos" del panel del administrador.
    *   En la parte "Asignatura ↔ Curso", selecciona el curso creado y la asignatura creada y añádela.
    *   Saldrá una notificación arriba a la derecha mencionando la correcta ejecución.

7.  **Matricularse en el Curso (como usuario):**.
    *   Navega a la sección de "Explorar".
    *   Busca y selecciona "Curso de Prueba TFG".
    *   Elige la asignatura "Matemáticas de Prueba".
    *   Confirma la operación.

8.  **Acceder a la Sección de Estudio y Generar Ejercicio:**
    *   Una vez matriculado, navega a "Mis cursos".
    *   Selecciona "Ver asignaturas" en "Curso de Prueba TFG".
    *   Dentro de la asignatura, deberías ver el tema "Sumas y Restas Básicas".
    *   Busca un botón o enlace que diga **"Estudiar"**.
    *   Selecciona el tema "Números Naturales" en el desplegable y la dificultad que se desee en el otro desplegable (arriba a la derecha).
    *   Pinchar en "Generar pregunta".

9.  **Verificar el Ejercicio:**
    *   Se debería mostrar un ejercicio en pantalla y un chat para comunicarse con la IA.
    *   Verifica que el contenido del ejercicio sea coherente con el tema.

Este flujo permite probar la creación de la estructura educativa básica y la funcionalidad de generación de ejercicios basada en IA.

> [!NOTA]
> Es importante crear el tema de ejemplo mencionado (**Números Naturales**), ya que el modelos está entrenado únicamente
> para ejercicios relacionados con dicho tema.
