#!/usr/bin/env bash
# Serve the new React app and run the deterministic parity kit against it
# (dashboard + widget). Stub mode = no backend needed; it proves the app's rendering +
# the 3 paths. For real-data parity, run the app with the backend env set and use --mode live.
#
#   bash verify-app.sh
#
set -u
KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python || true)"
[ -n "$PY" ] || { echo "python3 not found"; exit 1; }

cd "$KIT_DIR/app"
[ -d node_modules ] || npm install --no-fund --no-audit
echo "building app..."; npm run build >/tmp/bafa-build.log 2>&1 || { echo "build failed (see /tmp/bafa-build.log)"; tail -20 /tmp/bafa-build.log; exit 1; }

npm run preview >/tmp/bafa-preview.log 2>&1 &
PID=$!
cd "$KIT_DIR"
curl -s --retry 30 --retry-delay 1 --retry-connrefused -o /dev/null http://127.0.0.1:5173/ 2>/dev/null || true

RC=0
echo "=== DASHBOARD ==="; "$PY" verify/parity/run_parity.py --screen dashboard || RC=1
echo "=== WIDGET ==="; "$PY" verify/parity/run_parity.py --screen widget || RC=1

kill "$PID" 2>/dev/null || true
pkill -f "vite preview" 2>/dev/null || true
echo
if [ "$RC" -eq 0 ]; then
  echo "ALL GREEN -- the new app passes the parity kit (dashboard + widget)."
  echo "Reports: output/report-dashboard.html, output/report-widget.html"
else
  echo "Some journeys need follow-up -- open output/report-*.html (the failing assert is named)."
fi
exit "$RC"
