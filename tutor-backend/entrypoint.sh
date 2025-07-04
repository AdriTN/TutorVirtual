#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# Aplicar migraciones de base de datos
echo "Aplicando migraciones de base de datos..."
alembic upgrade head

# Ejecutar el comando pasado como argumentos a este script (CMD del Dockerfile)
exec "$@"