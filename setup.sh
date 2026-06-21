#!/usr/bin/env bash
# One-shot setup for the BAFA Comp kit in the pod (Linux). Idempotent & safe to re-run.
# Installs the Copilot CLI skills, the verify deps, and the brand-new React app, then
# PROVES everything works (offline self-tests + a real-app parity run) before you wire
# in the real backend.
#
#   bash setup.sh
#
set -u

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python || true)"
say() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
die() { printf '\033[31mERROR: %s\033[0m\n' "$1" >&2; exit 1; }

[ -n "$PY" ] || die "python3 not found on PATH"
command -v npm >/dev/null 2>&1 || die "npm not found on PATH"
say "Using python: $PY ($($PY --version 2>&1)) ; node $(node --version 2>&1)"

say "1/6  Install Copilot CLI skills  ->  ~/.copilot/skills/"
mkdir -p "$HOME/.copilot/skills"
cp -r "$KIT_DIR"/skills/bafa-map "$KIT_DIR"/skills/bafa-build "$KIT_DIR"/skills/bafa-verify "$HOME/.copilot/skills/"
echo "   installed: $(ls -1 "$HOME/.copilot/skills" | grep -E '^bafa-' | tr '\n' ' ')"
echo "   -> in 'copilot':  /skills reload   then   /skills info bafa-map"

say "2/6  Install verify dependencies (Playwright + Pillow)"
( cd "$KIT_DIR/verify" && "$PY" -m pip install -r requirements.txt ) || die "pip install failed (check the pod's internal index)"
"$PY" -m playwright install chromium || die "playwright browser install failed"

say "3/6  Install + build the new React app (app/)"
( cd "$KIT_DIR/app" && npm install --no-fund --no-audit && npm run build ) || die "app install/build failed"

say "4/6  Config"
if [ -f "$KIT_DIR/verify/config.json" ]; then
  echo "   verify/config.json already exists (left as-is)"
else
  cp "$KIT_DIR/verify/config.example.json" "$KIT_DIR/verify/config.json"
  echo "   created verify/config.json"
fi

say "5/6  Offline self-tests (no browser, then engine smoke)"
"$PY" "$KIT_DIR/verify/parity/selftest.py" || die "selftest failed"
"$PY" "$KIT_DIR/verify/parity/e2e_smoke.py" || die "engine smoke failed -- send the output to Claude"

say "6/6  Real-app parity (serves app/ + runs dashboard + widget)"
bash "$KIT_DIR/verify-app.sh" || echo "   (some journeys need follow-up -- see output/report-*.html)"

say "DONE."
cat <<EOF

YOUR NEXT STEPS
---------------
1) See the new app instantly (bundled sample data, no backend):
     cd "$KIT_DIR/app" && VITE_MOCK=1 npm run dev      # http://localhost:5173/  and  /compensation

2) Connect it to the REAL backend (just like the original):
     cd "$KIT_DIR/app" && cp .env.example .env.local   # set VITE_AUTH_BASE / VITE_DATA_BASE / VITE_COMP_BASE
     npm run dev
   (Backend: run the legacy Tomcat for /BAA/api, and point VITE_DATA_BASE at the compensation service.)

3) Re-run the parity check any time:
     bash "$KIT_DIR/verify-app.sh"                      # builds, serves, verifies dashboard + widget

4) Add the NEXT legacy screen (the loop, in 'copilot'):
     /bafa-map    -> output/spec.md          (analyze one legacy screen)
     /bafa-build  -> a new screen in app/     (honoring CONTRACT.md)
     bash verify-app.sh                       (verify it)

The new app/ replaces business-analysis-next-ui. See app/README.md and COPILOT-GUIDE.md.
EOF
