FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Compilamos para producción
RUN npm run build

# Usar un servidor de archivos estáticos
RUN npm install -g serve

# El servidor 'serve' por defecto escucha en 3000.
# Lo configuramos para que escuche en 5173.
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
