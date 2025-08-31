FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render attribue dynamiquement le port via la variable d’environnement $PORT
EXPOSE 10000

# Lancer avec gunicorn sur main:app
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT} main:app"]
