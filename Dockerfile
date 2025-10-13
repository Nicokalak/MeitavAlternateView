FROM python:3-slim AS base

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir poetry

WORKDIR /app

# Copy dependency files and install dependencies
COPY pyproject.toml poetry.lock* ./
COPY src src

FROM base AS quality_check
COPY tests tests
RUN poetry update
RUN poetry install

RUN echo "--- Running Quality Checks ---" && \
    poetry run ruff check src && \
    poetry run ruff format --check src && \
    poetry run mypy src && \
    poetry run pytest tests && \
    echo "--- Quality Checks Passed! ---"

FROM base AS runtime
RUN poetry update && poetry install --only main --no-interaction --no-ansi && rm -rf /root/.cache/

EXPOSE 8080

HEALTHCHECK CMD poetry run python src/meitav_view/healthcheck.py  || exit 1
CMD ["poetry", "run", "meitav_view"]
