# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.14

# Stage 1: Build frontend static assets (runs natively on the build host)
FROM --platform=$BUILDPLATFORM node:24-slim AS ui
WORKDIR /app/ui

COPY ui/package.json ui/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --ignore-scripts --no-audit --no-fund

# The build writes to ../src/meitav_view/static, i.e. /app/src/meitav_view/static
COPY ui/ ./
ARG APP_VERSION=0.0.0+local
RUN APP_VERSION="${APP_VERSION}" npm run build

# Stage 2: Install Python dependencies and the project with uv
FROM python:${PYTHON_VERSION}-slim AS python-builder

# Pin uv to a stable minor version to ensure build repeatability
COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Dependencies only: this layer is independent of source and version changes
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY --from=ui /app/src/meitav_view/static ./src/meitav_view/static

ARG APP_VERSION=0.0.0+local
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    SETUPTOOLS_SCM_PRETEND_VERSION="${APP_VERSION}" \
    uv sync --frozen --no-dev --no-editable

# Stage 3: Slim production runtime
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN useradd --system --uid 1000 --create-home appuser && \
    install -d -o appuser -g appuser /app/data

COPY --from=python-builder --chown=appuser:appuser /app/.venv /app/.venv

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "-m", "meitav_view.healthcheck"]

ARG APP_VERSION=0.0.0+local
LABEL org.opencontainers.image.title="meitav-view" \
      org.opencontainers.image.version="${APP_VERSION}"

CMD ["meitav_view"]
