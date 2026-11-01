# --- Etap 1: Budowanie aplikacji React (Node.js) ---
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# --- Etap 2: Serwowanie plików produkcyjnych przez Nginx ---
FROM nginx:alpine

# Kopiujemy konfigurację Reverse Proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Kopiujemy skompilowane pliki z Etapu 1 do katalogu serwera Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]