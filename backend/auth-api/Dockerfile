FROM python:3.12-slim

WORKDIR /app

# install system dependencies needed for python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy app contents to /app instead of /app/app
COPY app/* ./
COPY app/db ./db
COPY app/middleware ./middleware
COPY app/models ./models
COPY app/routes ./routes
COPY app/schemas ./schemas
COPY app/utils ./utils

EXPOSE 8001

# Set Python path so imports work correctly
ENV PYTHONPATH=/app

CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]