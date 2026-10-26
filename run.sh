#!/usr/bin/env bash
# Build and run the app in Docker. The Meitav web-query link is mounted as a
# secret file (never passed through the environment).
#
#   ./run.sh [--rebuild]
#
# Optional environment:
#   PORTFOLIO_SECRET_FILE  path to the file holding the link (default: .secrets/portfolio_url)
set -euo pipefail

cd "$(dirname "$0")"

SECRET_FILE="${PORTFOLIO_SECRET_FILE:-.secrets/portfolio_url}"
if [[ ! -s "${SECRET_FILE}" ]]; then
  echo "error: secret file '${SECRET_FILE}' is missing or empty." >&2
  echo "Create it with: mkdir -p .secrets && printf '%s' '<your link>' > .secrets/portfolio_url" >&2
  exit 1
fi
SECRET_FILE="$(cd "$(dirname "${SECRET_FILE}")" && pwd)/$(basename "${SECRET_FILE}")"

mkdir -p data

REBUILD=()
if [[ "${1:-}" == "--rebuild" ]]; then
  REBUILD=(--no-cache)
fi

ENV_FILE=()
if [[ -f .env ]]; then
  ENV_FILE=(--env-file .env)
fi

APP_VERSION="$(uvx --from setuptools-scm python -m setuptools_scm 2>/dev/null || echo 0.0.0+local)"

docker stop meitav-app 2>/dev/null || true
docker build "${REBUILD[@]+"${REBUILD[@]}"}" \
  --build-arg APP_VERSION="${APP_VERSION}" \
  -t meitav-app:latest -f Dockerfile .
docker run --rm \
  "${ENV_FILE[@]+"${ENV_FILE[@]}"}" \
  --name meitav-app \
  -e MEITAV_PORTFOLIO_URL_FILE=/run/secrets/portfolio_url \
  -v "${SECRET_FILE}:/run/secrets/portfolio_url:ro" \
  -p 8080:8080 \
  -v "$(pwd)/data:/app/data" \
  meitav-app:latest
