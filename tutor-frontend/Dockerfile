FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Compilamos para producción
RUN npm run build

# Usar un servidor de archivos estáticos
RUN npm install -g serve

# El servidor corre en 4173 por defecto
EXPOSE 4173
CMD ["serve", "-s", "dist"]
