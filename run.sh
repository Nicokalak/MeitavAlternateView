#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  echo "error: .env not found. Copy .env.example to .env and fill in your values." >&2
  exit 1
fi

mkdir -p data

REBUILD=()
if [[ "${1:-}" == "--rebuild" ]]; then
  REBUILD=(--no-cache)
fi

APP_VERSION="$(uvx --from setuptools-scm python -m setuptools_scm 2>/dev/null || echo 0.0.0+local)"

docker stop meitav-app 2>/dev/null || true
docker build "${REBUILD[@]+"${REBUILD[@]}"}" \
  --build-arg APP_VERSION="${APP_VERSION}" \
  -t meitav-app:latest -f Dockerfile .
docker run --rm \
  --env-file .env \
  --name meitav-app \
  -p 8080:8080 \
  -v "$(pwd)/data:/app/data" \
  meitav-app:latest
