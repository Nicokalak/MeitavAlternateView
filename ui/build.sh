#!/bin/sh
set -e

cd "$(dirname "$0")"

# Run Vite build to generate production assets in dist/
./node_modules/.bin/vite build

# Ensure backwards-compatibility folders for test and legacy mounts if needed
mkdir -p dist/js dist/css
cp -r src/css/* dist/css/ 2>/dev/null || true
cp -r src/js/* dist/js/ 2>/dev/null || true

# Always copy compiled assets to backend static folder
STATIC_TARGET="../src/meitav_view/static"
mkdir -p "$STATIC_TARGET"
rm -rf "$STATIC_TARGET"/*
cp -r dist/* "$STATIC_TARGET/"

