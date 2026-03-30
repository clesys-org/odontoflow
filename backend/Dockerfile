# ── Production build ──────────────────────────────
FROM python:3.12-slim AS production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .

COPY alembic/ alembic/
COPY alembic.ini .
COPY scripts/ scripts/

EXPOSE 8000
CMD ["sh", "-c", "uvicorn odontoflow.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

# ── Development build (hot-reload) ───────────────
FROM python:3.12-slim AS development

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir -e ".[dev]"

# volumes no compose substituem src/ para hot-reload
EXPOSE 8000
CMD ["uvicorn", "odontoflow.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
