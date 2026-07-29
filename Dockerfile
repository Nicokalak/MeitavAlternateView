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

# Copy uv binary directly from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Version injected at build time so hatch-vcs doesn't need a .git directory
ARG APP_VERSION=0.0.0.dev0

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    SETUPTOOLS_SCM_PRETEND_VERSION=${APP_VERSION} \
    HATCH_BUILD_VERSION=${APP_VERSION}

WORKDIR /app

# Copy dependency specifications first for Docker layer caching
COPY pyproject.toml uv.lock ./

# Install main runtime dependencies into /app/.venv (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy application source and install project package firmly into /app/.venv
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Stage 3: Slim Production Runtime
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Create non-root system user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && chown -R appuser:appuser /app

# Copy pre-built Python virtual environment (contains your built meitav-view package)
COPY --from=python-builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy compiled frontend static assets directly into the virtual environment's site-packages 
# or wherever your backend expects it. (Adjust this path if your app reads from /app/src instead)
COPY --from=frontend-builder --chown=appuser:appuser /app/ui/dist /app/.venv/lib/python3.12/site-packages/meitav_view/static

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -m meitav_view.healthcheck || exit 1

CMD ["meitav_view"]