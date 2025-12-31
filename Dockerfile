# ===============================================
# BASE BUILDER IMAGE
# ===============================================
FROM python:3.14-slim AS builder

# Prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system packages required to build Python deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies in a virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirement files early
COPY requirements.txt .

# Install with no cache
RUN pip install --no-cache-dir -r requirements.txt


# ===============================================
# FINAL RUNTIME IMAGE
# ===============================================
FROM python:3.14-slim

# Prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser

# Set work directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy project code
COPY . .

# Expose fastapi ports
EXPOSE 8000

# Switch to non-root user
USER appuser

# Run the application
CMD ["gunicorn", "app.main:app", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "4", \
    "--timeout", "120"]
