#!/bin/sh
set -e

cd "$(dirname "$0")"

# Refuse to run concurrently: parallel builds clobber dist/ and the static folder.
LOCK_DIR=".build.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    OWNER_PID="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
    if [ -n "$OWNER_PID" ] && kill -0 "$OWNER_PID" 2>/dev/null; then
        echo "Another build is already running (pid $OWNER_PID). Refusing to run in parallel." >&2
        exit 1
    fi
    # Stale lock left by a killed build.
    rm -rf "$LOCK_DIR"
    mkdir "$LOCK_DIR" || { echo "Could not acquire build lock." >&2; exit 1; }
fi
echo $$ > "$LOCK_DIR/pid"
trap 'rm -rf "$LOCK_DIR"' EXIT INT TERM HUP

# Run Vite build to generate production assets in dist/
./node_modules/.bin/vite build

# Ensure backwards-compatibility folders for test and legacy mounts if needed
mkdir -p dist/css dist/assets/favicon
cp -r src/css/* dist/css/ 2>/dev/null || true
cp -r src/favicon/* dist/assets/favicon/ 2>/dev/null || true

# Always copy compiled assets to backend static folder
STATIC_TARGET="../src/meitav_view/static"
mkdir -p "$STATIC_TARGET"
rm -rf "$STATIC_TARGET"/*
cp -r dist/* "$STATIC_TARGET/"

