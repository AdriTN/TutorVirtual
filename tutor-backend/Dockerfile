FROM python:3.11-slim

# Instalar dependencias de compilación y de Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev

# Establecer directorio de trabajo
WORKDIR /app

# Copiamos archivo de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponer el puerto en el contenedor (por defecto FastAPI en 8000)
EXPOSE 8000

# Comando para iniciar la app: uvicorn con hotreload no se recomienda en producción,
# pero para desarrollo puedes usarlo. En producción, querrás uvicorn sin reload o gunicorn.
# El --reload se gestionará a través de docker-compose.yml para mayor flexibilidad.
CMD ["uvicorn", "src.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
