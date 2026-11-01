# Używamy oficjalnego, lekkiego obrazu Pythona
FROM python:3.12-slim

# Blokujemy buforowanie stdout/stderr, aby logi serwera pojawiały się natychmiast
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Kopiujemy i instalujemy zależności jako osobny krok (wykorzystanie cache Dockera)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy kod aplikacji
COPY . .

# Wystawiamy port, na którym nasłuchuje FastAPI
EXPOSE 8000

# Uruchamiamy produkcyjny serwer Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]