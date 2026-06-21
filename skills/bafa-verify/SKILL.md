---
name: bafa-verify
description: VERIFY a React BAA screen against legacy behaviour with the deterministic parity kit (happy / validation / backend-error), then read the report. Use for "verify the FA Comp Summary dashboard", "run the parity tests", "check the rebuilt widget matches legacy".
---

# bafa-verify — run the deterministic parity kit, read the result

You run the **no-LLM** parity kit and interpret its report. This is the rerunnable,
repeatable check the ticket asks for — not screenshot-eyeballing.

## Setup (once per pod)
```bash
cd <this-kit>/verify
pip install -r requirements.txt && python -m playwright install chromium
cp config.example.json config.json   # adjust only if the pod differs
```

## Run a screen
Easiest — build, serve `app/`, and verify both screens in one go:
```bash
bash verify-app.sh
```
Or start the app yourself and verify one screen:
```bash
cd app && npm run dev          # serves :5173 (add VITE_MOCK=1 for bundled sample data)
python verify/parity/run_parity.py --screen dashboard   # FA Comp Summary dashboard
python verify/parity/run_parity.py --screen widget      # Compensation widget
```
Options: `--only <journey>` (happy | validation_nodata | backend_error), `--headed`,
`--mode live` (real data + `auth_state.json` + legacy pixel baseline).

It runs each journey with stubbed REST (offline, deterministic), asserts the on-screen
contract, screenshots each state, and writes `output/report-<screen>.html` + `.json`.
Exit code 0 = all match; 1 = something needs follow-up.

## Read the result
- Open `output/report-<screen>.html`: each journey is **PASS** (matches legacy) or
  **FOLLOW-UP** (with the exact failing assert + a screenshot).
- For a FOLLOW-UP on the **widget**: the fix belongs in the React component — make it
  satisfy `CONTRACT.md`, then re-run (loop with `bafa-build`).
- For a FOLLOW-UP on the **dashboard**: it's a real behaviour gap vs the expected legacy
  semantics — record it in `verify/PARITY-DELTAS.md` and raise it.
- Log any intentional visual differences (e.g. redesign) in `verify/PARITY-DELTAS.md`
  as **accepted** vs **follow-up**.

## Rerun
Re-invoke the same command any time (after a React change, or in CI). Fixtures and
`auth_state.json` are reused — no manual setup to rebuild. That satisfies the
"rerunnable without reconstructing the setup" criterion.

## Sanity check the kit itself (offline, no browser)
`python verify/parity/selftest.py` — confirms fixtures, screen configs, the image-diff
util, and the report renderer are all consistent.
