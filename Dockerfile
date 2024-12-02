# Utilisation de Python officiel
FROM python:latest

# Répertoire de travail
WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY kameleon_back/ ./kameleon_back/ 
COPY .env /app/.env
COPY back/ ./back/
COPY manage.py .

RUN ls

# Exposer le port
EXPOSE 8000