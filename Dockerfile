# --- ETAP 1: Budowanie frontendu w Node.js ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY klocki-frontend/package*.json ./
RUN npm install
COPY klocki-frontend/ ./
RUN npm run build

# --- ETAP 2: Środowisko uruchomieniowe Pythona (FastAPI) ---
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Kopiowanie i instalacja zależności backendu
COPY klocki-backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu backendu
COPY klocki-backend/ ./

# Kopiowanie zbudowanego frontendu z Etapu 1 do katalogu static
COPY --from=frontend-builder /app/frontend/dist ./static

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]