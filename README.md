# bafa-comp-modernize — autonomous 1:1 JSP→React conversion loop

Convert the legacy **JSP/Struts BAA** UI into a **1:1 React replica** — **UI only** (same
backend + mainframe). You drive it with **Copilot CLI (gpt‑5.4)** and one master prompt; it
maps the original app, rebuilds each screen in `new-ui/`, and **loops a checker against the
original screenshots until every screen matches 1:1**.

## Three pieces, that's it
```
MASTER-PROMPT.md     # paste into Copilot CLI to run the whole loop (map → build → check → fix → repeat)
checker/compare.py   # the 1:1 gate: diffs a new screen vs the original screenshot -> PASS / FAIL
new-ui/              # the React replica (bootable Vite scaffold; the loop fills it, screen by screen)
screenshots/         # original-app screenshots captured during MAP (the targets to match)
```

## How to run it (in the pod)
```bash
# 1. one-time deps for the checker + the new app
pip install -r checker/requirements.txt && python -m playwright install chromium
( cd new-ui && npm install )

# 2. start Copilot CLI, edit the CONFIG block in MASTER-PROMPT.md, then paste the whole file in:
copilot
#   > (paste MASTER-PROMPT.md) -> it maps the app and converts screen by screen, non-stop.
```

## What the loop does each iteration
1. **MAP** the running original (`localhost:8080/BAA`) → `screenshots/<screen>.png` + `screens.md`.
2. **BUILD** the screen in `new-ui/` from the original **source code**, calling the **same backend**.
3. **CHECK**: `python checker/compare.py --baseline screenshots/<screen>.png --url http://localhost:5173/<route>`.
4. **FIX** until the checker prints `PASS (1:1)`, then the next screen. Repeat until the whole app is done.

The checker — not the model's judgment — is the 1:1 gate, so the loop has an objective signal
to keep going until the new UI matches the original exactly.

> UI only. Same backend. The screenshot is the source of truth. Naming: BAFA/BAA only.
