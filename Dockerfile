FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render définit $PORT. Si absent, fallback à 5000
ENV PORT=5000

EXPOSE 5000

# Lancer Gunicorn
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} main:app"]
