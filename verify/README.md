# verify/ — the deterministic parity kit

No LLM. Plain Python + Playwright. Drives the React app through happy / validation /
backend-error journeys with **stubbed REST** (offline, deterministic), asserts the
on-screen contract, screenshots each state, and writes an HTML/JSON report. This is the
rerunnable "VERIFY" stage of MAP → BUILD → VERIFY.

## Install (pod)
```bash
pip install -r requirements.txt
python -m playwright install chromium
cp config.example.json config.json     # edit only if the pod differs
```

## Run
```bash
# React app must be running:  (cd …/business-analysis-next-ui && npm install && npm run dev)
python parity/run_parity.py --screen dashboard     # already-built dashboard (the ticket)
python parity/run_parity.py --screen widget        # rebuilt Compensation widget (after BUILD)
# options: --only happy|validation_nodata|backend_error   --headed   --mode live
```
→ `../output/report-<screen>.html` (+ `.json`), screenshots in `../output/screenshots/`.
Exit 0 = all journeys match; 1 = follow-up.

## Prove the engine works — without the pod
```bash
python parity/selftest.py      # offline: validates fixtures, screen configs, imgdiff, report renderer
python parity/e2e_smoke.py      # end-to-end: serves a faithful dashboard MOCK + runs the real runner
```
`e2e_smoke.py` is the real proof: it launches a browser, stubs the REST calls, asserts
all three paths (happy / no-data / backend-error), screenshots them, and writes the
report — exactly as a pod run would, but against a built-in mock. Expect
`E2E SMOKE OK` and a report in `../output/report-dashboard.html`. (It tests the *engine
+ dashboard.json config*, not the real React app — that needs the pod.)

## Layout
```
verify/
├── config.example.json     # URLs, params, viewport (1366x768), paths
├── requirements.txt        # playwright (+ pillow for the soft pixel diff)
├── screens/
│   ├── dashboard.json       # verify-only: 3 behaviour journeys (the ticket)
│   └── widget.json          # full-loop: pixel + data + behaviour (asserts CONTRACT testids)
├── fixtures/                # exact REST shapes (token, report meta/customization/data; comp_*)
└── parity/
    ├── run_parity.py        # the runner (CLI)
    ├── stubs.py             # route() handlers: fixtures or __500__/__abort__/__ok__
    ├── assertions.py        # assert types + offline validator
    ├── imgdiff.py           # soft visual diff (Pillow)
    ├── report.py            # JSON + HTML report
    ├── capture_legacy.py    # live mode: capture legacy #faComp baseline + data (widget)
    └── selftest.py          # offline consistency check
```

## How modes differ
- **stub** (default): REST is intercepted and answered from `fixtures/`. No backend, no
  DB2/mainframe, no SSO. Deterministic and rerunnable — use this for CI and day-to-day.
- **live**: uses `auth_state.json` (from the pod's `save_auth_state.py`) + real data, and
  enables the widget pixel baseline (`capture_legacy.py`). Use for a real data spot-check.

## Adding the next screen
Drop a new `screens/<name>.json` (copy `dashboard.json`/`widget.json`), add any fixtures,
run `python parity/selftest.py`, then `run_parity.py --screen <name>`. The three skills
(`bafa-map`/`bafa-build`/`bafa-verify`) handle the rest.
