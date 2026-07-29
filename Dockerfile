# Stage 1: Build Frontend Static Assets
FROM node:24-slim AS frontend-builder
WORKDIR /app/ui

# Install UI dependencies into ui/node_modules
COPY ./ui/package*.json ./
RUN npm ci --ignore-scripts

COPY ./ui ./
RUN npm run build

# Stage 2: Install Python Dependencies & Project with uv
FROM python:3.12-slim AS python-builder

# Pin uv to a stable minor version to ensure build repeatability
COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /uvx /bin/

# Version injected at build time (e.g. from `git describe --tags`)
ARG APP_VERSION=0.0.0.dev0

WORKDIR /app

# Copy dependency specifications first for Docker layer caching
COPY pyproject.toml uv.lock ./

# Install main runtime dependencies into /app/.venv (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY src ./src

# Sanitize git tag version strings (e.g., v1.1.2-12-g7d88f12) into a PEP 440-compliant 
# format (e.g., 1.1.2.dev12+g7d88f12) right before running the final sync.
RUN --mount=type=cache,target=/root/.cache/uv \
    CLEAN_VERSION=$(echo "${APP_VERSION}" | sed 's/^v//;s/-\([0-9]\+\)-g/.dev\1+/') && \
    SETUPTOOLS_SCM_PRETEND_VERSION=${CLEAN_VERSION} \
    HATCH_BUILD_VERSION=${CLEAN_VERSION} \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    uv sync --frozen --no-dev --no-editable

# Stage 3: Slim Production Runtime
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Create non-root system user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && chown -R appuser:appuser /app

# Copy pre-built Python virtual environment (contains your built, non-editable meitav-view package)
COPY --from=python-builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy compiled frontend static assets directly into the built package's destination directory
COPY --from=frontend-builder --chown=appuser:appuser /app/ui/dist /app/.venv/lib/python3.12/site-packages/meitav_view/static

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -m meitav_view.healthcheck || exit 1

CMD ["meitav_view"]