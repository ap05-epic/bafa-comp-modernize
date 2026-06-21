#!/usr/bin/env bash
# One-shot setup for the BAFA Comp kit in the pod (Linux). Idempotent & safe to re-run.
# It installs the Copilot CLI skills, the verify dependencies, and PROVES the engine works
# (offline self-test + a real browser smoke test) before you touch the real app.
#
#   bash setup.sh
#
set -u

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python || true)"
say() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
die() { printf '\033[31mERROR: %s\033[0m\n' "$1" >&2; exit 1; }

[ -n "$PY" ] || die "python3 not found on PATH"
say "Using python: $PY ($($PY --version 2>&1))"

say "1/5  Install Copilot CLI skills  ->  ~/.copilot/skills/"
mkdir -p "$HOME/.copilot/skills"
cp -r "$KIT_DIR"/skills/bafa-map "$KIT_DIR"/skills/bafa-build "$KIT_DIR"/skills/bafa-verify "$HOME/.copilot/skills/"
echo "   installed: $(ls -1 "$HOME/.copilot/skills" | grep -E '^bafa-' | tr '\n' ' ')"
echo "   -> in 'copilot', run:  /skills reload   then   /skills info bafa-map"

say "2/5  Install verify dependencies (Playwright + Pillow)"
cd "$KIT_DIR/verify"
"$PY" -m pip install -r requirements.txt || die "pip install failed (check the pod's internal index)"
"$PY" -m playwright install chromium || die "playwright browser install failed"

say "3/5  Config"
if [ -f config.json ]; then
  echo "   config.json already exists (left as-is)"
else
  cp config.example.json config.json
  echo "   created config.json (edit react_base_url / params only if the pod differs)"
fi

say "4/5  Offline self-test (no browser)"
"$PY" parity/selftest.py || die "selftest failed"

say "5/5  End-to-end engine smoke test (real browser + built-in mock)"
"$PY" parity/e2e_smoke.py || die "smoke test failed -- send the output to Claude"

say "DONE -- the verify engine works on this pod."
cat <<EOF

YOUR NEXT STEPS
---------------
1) Start the React app (separate terminal, or background it):
     cd <...>/BAX-BusinessAnalysis/business-analysis-next-ui
     npm install && npm run dev        # serves http://localhost:5173

2) Run the parity check for the dashboard  ==> THIS IS THE TICKET (no build needed):
     cd "$KIT_DIR"
     $PY verify/parity/run_parity.py --screen dashboard
   Result: output/report-dashboard.html (+ .json), screenshots in output/screenshots/.
   (Headless pod: copy the html out to view, or read report-dashboard.json / the console lines.)

3) Full MAP -> BUILD -> VERIFY loop for the Compensation widget (in 'copilot'):
     Use the /bafa-map skill on the Compensation widget (jsp/fa_compensation.jsp)
     Use the /bafa-build skill to build it from output/spec.md, honoring CONTRACT.md
     $PY verify/parity/run_parity.py --screen widget

If a journey shows FOLLOW-UP, the report names the exact failing assert -- fix the one
line in verify/screens/dashboard.json (or the React component for the widget) and re-run.
See COPILOT-GUIDE.md and RUNBOOK.md for detail.
EOF
