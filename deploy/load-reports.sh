#!/bin/bash
# Load a new report JSON into Neo4j.
# Usage: ./deploy/load-reports.sh reports/report-new-disease.json
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <report.json or reports-directory>"
    exit 1
fi

REPORT_PATH="$1"

if [ ! -e "$REPORT_PATH" ]; then
    echo "Error: $REPORT_PATH does not exist"
    exit 1
fi

echo "Loading $REPORT_PATH into Neo4j..."
docker compose run --rm \
    -v "$(cd "$(dirname "$REPORT_PATH")" && pwd):/app/reports:ro" \
    api python -m src.neo4j_loader "/app/reports/$(basename "$REPORT_PATH")"

echo "Done. Data available immediately via API."
