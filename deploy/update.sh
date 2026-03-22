#!/bin/bash
# Redeploy after code changes.
# Run from the project root on the VPS.
set -e

echo "=== Updating Drug Target Explorer ==="

git pull

echo "Rebuilding containers..."
docker compose down
docker compose build
docker compose up -d

echo "=== Update complete ==="
docker compose ps
