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
COPY app/model ./model
COPY app/routes ./routes
COPY app/middleware ./middleware
COPY app/utils ./utils

# Create models directory
RUN mkdir -p /app/models /tmp/models

# Download the HuggingFace model weights during build
RUN .venv/bin/python -c "from sentence_transformers import SentenceTransformer; \
    model = SentenceTransformer('intfloat/multilingual-e5-small'); \
    model.save('/app/models/multilingual-e5-small')"

# Disable HuggingFace network calls in production
ENV SENTENCE_TRANSFORMERS_HOME=/app/models
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

EXPOSE 8000

# Set Python path so imports work correctly
ENV PYTHONPATH=/app

CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]