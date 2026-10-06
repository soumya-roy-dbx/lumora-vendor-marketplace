#!/usr/bin/env bash
# Capture the Databricks App's recent logs (build + runtime) as text evidence.
#   bash evidence/tools/capture_app_logs.sh [app-name] [seconds]
APP="${1:-lumora-data-marketplace}"; SECS="${2:-25}"; OUT="$(dirname "$0")/../app_logs.md"
TMP=$(mktemp)
databricks apps logs "$APP" -p "${DATABRICKS_PROFILE:-DEFAULT}" --tail-lines 300 > "$TMP" 2>&1 &
PID=$!; sleep "$SECS"; kill "$PID" 2>/dev/null
{
  echo "# Databricks App logs — $APP"
  echo
  echo "_Captured $(date -u '+%Y-%m-%d %H:%M:%S UTC') with \`databricks apps logs\` (last 300 lines; pip-install noise removed)._"
  echo
  echo '```text'
  grep -v "Requirement already satisfied" "$TMP"
  echo '```'
} > "$OUT"
rm -f "$TMP"; echo "wrote $OUT"
