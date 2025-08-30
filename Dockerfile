FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render attribue dynamiquement le port via la variable d’environnement $PORT
EXPOSE 10000

# Lancer avec gunicorn via sh -c (pour interpréter $PORT)
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} app:app"]
