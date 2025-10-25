# Lightweight Python base
FROM python:3.10-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Allow inbound requests by default inside container; override as needed
    ALLOWED_IPS=0.0.0.0/0 \
    FLASK_ENV=production

WORKDIR /app

# Install deps first for better layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Service port
EXPOSE 5000

# Default command
CMD ["python", "app.py"]
