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

COPY app ./app

# Download the HuggingFace model weights during build
# This is a one-time download that gets baked into the image
RUN uv run python -c "from sentence_transformers import SentenceTransformer; \
    model = SentenceTransformer('intfloat/multilingual-e5-small'); \
    model.save('/app/models/multilingual-e5-small')"

# Disable HuggingFace network calls in production
ENV SENTENCE_TRANSFORMERS_HOME=/app/models
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

RUN mkdir -p /tmp/models

EXPOSE 8000

CMD ["uv", "run", "main.py"]