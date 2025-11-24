FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy alembic files
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY models/ ./models/

COPY lambda_handler.py .

CMD ["lambda_handler.handler"]