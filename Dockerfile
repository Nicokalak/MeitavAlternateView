FROM python:3-slim AS base

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir poetry

WORKDIR /app

# Copy dependency files and install dependencies
COPY pyproject.toml poetry.lock* ./
COPY src src

FROM base AS runtime
RUN poetry install --without dev --only main --no-interaction --no-ansi && rm -rf /root/.cache/

EXPOSE 8080

HEALTHCHECK CMD poetry run python src/meitav_view/healthcheck.py  || exit 1
CMD ["poetry", "run", "meitav_view"]
