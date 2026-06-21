# RUNBOOK — exact commands (pod)

Kit at `~/bafa-comp-modernize`. Rerunnable: re-run any block any time.

## 0. One-time setup (does everything + proves it)
```bash
git clone https://github.com/ap05-epic/bafa-comp-modernize.git ~/bafa-comp-modernize
cd ~/bafa-comp-modernize
bash setup.sh            # skills + deps + builds app/ + runs the parity kit against it
```

## A. The new app (replaces business-analysis-next-ui)
```bash
cd ~/bafa-comp-modernize/app

# see it instantly with sample data (no backend):
VITE_MOCK=1 npm run dev                 # http://localhost:5173/   and   /compensation

# connect to the REAL backend (just like the original):
cp .env.example .env.local              # set VITE_AUTH_BASE / VITE_DATA_BASE / VITE_COMP_BASE
npm run dev
# backend: run the legacy Tomcat for /BAA/api  ->  cd <...>/BAX-Test-MainRepo && ./run-bax-businessanalysis.sh
```

## B. Verify (deterministic, the parity ticket)
```bash
cd ~/bafa-comp-modernize
bash verify-app.sh                       # builds app/, serves it, runs dashboard + widget
# -> output/report-dashboard.html, output/report-widget.html  (PASS / FOLLOW-UP per journey)

# or against an already-running app, one screen:
python verify/parity/run_parity.py --screen dashboard --only backend_error --headed
```

## C. Add the NEXT legacy screen (the loop, in 'copilot')
```text
Use the /bafa-map skill on <the legacy screen>            # -> output/spec.md (+ screenshots)
Use the /bafa-build skill to add it to app/ per CONTRACT.md
```
```bash
bash verify-app.sh                       # verify the new screen
```

## D. Real-data parity spot-check (optional)
```bash
# capture an SSO session once (use your real QA host):
python3 ~/.copilot/skills/webapp-snapshot/scripts/save_auth_state.py \
  --url "https://REPLACE-ME-baa-qa-host/BAA/jsp/login.jsp" \
  --output ~/bafa-comp-modernize/verify/auth_state.json
# then run the app against real data and verify live:
python verify/parity/run_parity.py --screen widget --mode live
```

## If something's off (don't loop blindly)
- **App won't build/boot** → `cd app && npm run build` and read the error; deps are minimal by design.
- **A journey is FOLLOW-UP** → the report names the exact failing assert. Fix the React component
  in `app/src/screens/` to satisfy `CONTRACT.md` (widget) or `verify/screens/dashboard.json` (dashboard), re-run.
- **Wrong port / base** → `react_base_url` / `react_base_path` in `verify/config.json`.
- **Re-validate the kit itself** → `python verify/parity/selftest.py`.

Paste `output/report-*.html` (or the console) back to Claude to tighten anything.
