# Stage 1: Build & assemble frontend static assets
FROM node:slim AS frontend-builder
WORKDIR /app
COPY package.json package-lock.json* ./
COPY scripts scripts
COPY src/meitav_view/static src/meitav_view/static
RUN npm ci || npm install
RUN node scripts/sync-assets.js

# Stage 2: Python base environment
FROM python:3-slim AS base

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir poetry

WORKDIR /app

# Copy dependency files and source code
COPY pyproject.toml poetry.lock* ./
COPY src src

# Copy compiled/synced static assets from frontend-builder stage
COPY --from=frontend-builder /app/src/meitav_view/static /app/src/meitav_view/static

# Stage 3: Production runtime environment
FROM base AS runtime
RUN poetry install --without dev --only main --no-interaction --no-ansi && rm -rf /root/.cache/

EXPOSE 8080

HEALTHCHECK CMD poetry run python src/meitav_view/healthcheck.py || exit 1
CMD ["poetry", "run", "meitav_view"]
