# RUNBOOK — exact commands (pod)

Copy-paste sequence for the MAP → BUILD → VERIFY loop. Paths assume the kit at
`~/bafa-comp-modernize` and the workspace at
`/home/devpod/.copilot/BAX-Test-MainRepo/BAX-BusinessAnalysis`. Rerunnable: re-run any
block any time.

## 0. One-time setup
```bash
# kit + skills
git clone <this-repo> ~/bafa-comp-modernize
cp -r ~/bafa-comp-modernize/skills/* ~/.copilot/skills/      # copilot: /skills reload

# verify deps
cd ~/bafa-comp-modernize/verify
pip install -r requirements.txt && python -m playwright install chromium
cp config.example.json config.json
python parity/selftest.py            # sanity: expect "SELFTEST OK"

# (live mode only) capture an SSO session for the legacy app, once:
python3 ~/.copilot/skills/webapp-snapshot/scripts/save_auth_state.py \
  --url "https://REPLACE-ME-baa-qa-host/BAA/jsp/login.jsp" \
  --output ~/bafa-comp-modernize/verify/auth_state.json   # use your real QA host
```

## A. VERIFY the dashboard (the ticket — no build needed)
```bash
# start the React app
cd /home/devpod/.copilot/BAX-Test-MainRepo/BAX-BusinessAnalysis/business-analysis-next-ui
npm install && npm run dev &        # serves http://localhost:5173

cd ~/bafa-comp-modernize
python verify/parity/run_parity.py --screen dashboard
# -> output/report-dashboard.html  (PASS/FOLLOW-UP per journey; exit 0 = all match)
```
If a selector differs in the real build, adjust `verify/screens/dashboard.json`, re-run
`python verify/parity/selftest.py`, then re-run the screen. (copilot can do this.)

## B. Full loop — Compensation widget
```bash
# MAP (in copilot, from the legacy repo)
#   Use the /bafa-map skill on the Compensation widget (BAA/src/main/webapp/jsp/fa_compensation.jsp)
#   -> output/spec.md + output/screenshots/*   (review, commit)

# (live pixel/data baseline, optional)
python ~/bafa-comp-modernize/verify/parity/capture_legacy.py --screen widget
#   -> output/baseline/widget_legacy.png + widget_legacy_data.json

# BUILD (in copilot, from business-analysis-next-ui)
#   Use the /bafa-build skill to build the Compensation widget from output/spec.md, honoring CONTRACT.md
#   -> React component + endpoint exposing the data-testids

# VERIFY (loops with BUILD until green)
python ~/bafa-comp-modernize/verify/parity/run_parity.py --screen widget
# -> output/report-widget.html
```

## Handy
```bash
# one journey, watch the browser
python verify/parity/run_parity.py --screen dashboard --only backend_error --headed

# real data instead of stubs (needs auth_state.json)
python verify/parity/run_parity.py --screen widget --mode live

# re-validate the kit after editing a screen/fixture
python verify/parity/selftest.py
```

## If something's off (don't loop blindly)
- **React app didn't start / wrong port** → fix `react_base_url` in `verify/config.json`.
- **Happy fails on a selector** → the real build's class/testid differs; update the
  screen JSON (dashboard) or the React component (widget, to match `CONTRACT.md`).
- **Legacy deep link 500s** in `capture_legacy.py` → BAA is stateful; reach `#faComp`
  via the real menu (login → Quick Search AB10 → hydrate) or capture it with the
  `webapp-snapshot` skill and drop the two files into `output/baseline/` yourself.
- **Pillow missing** → `pip install pillow` (pixel diff is optional/soft; asserts still run).

Report results back (OCR is fine) and we iterate.
