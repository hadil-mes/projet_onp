# Image Python officielle
FROM python:3.11-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier seulement les dépendances d'abord
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet
COPY . .

# Exposer le port Flask (Render utilisera $PORT)
EXPOSE 10000

# Lancer avec gunicorn (Render fournit la variable $PORT)
CMD ["gunicorn", "-b", "0.0.0.0:$PORT", "app:app"]
