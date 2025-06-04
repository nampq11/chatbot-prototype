FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY uv.lock pyproject.toml README.md ./

RUN uv sync --frozen --no-cache

COPY src/ src/

CMD ["app/.venv/bin/fastapi", "run", "src/infastructure/api.py", "--port", "8000", "--host", "0.0.0.0"]