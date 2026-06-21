# bafa-comp-modernize

A working **MAP → BUILD → VERIFY** loop for modernizing legacy BAA screens to React —
plus a **brand-new, working React UI** for BAFA Comp (FA Comp Summary) that replaces the
old `business-analysis-next-ui` (which wouldn't boot). Built to run in the pod with
**GitHub Copilot CLI (gpt-5.4)** and a deterministic, no-LLM verify kit.

## What you get
- **`app/`** — a fresh **React 19 + Vite** UI: the FA Comp Summary **dashboard** (`/`) and the
  Compensation **widget** (`/compensation`). Minimal + dependency-light so it actually boots.
  Connects to the **same backend contract** as the original (token → report meta/data), so it
  works identically when pointed at the real backend.
- **`verify/`** — a deterministic Python+Playwright **parity kit** (happy / no-data / backend-error).
  No LLM. Rerunnable. It's the hard pass/fail the build is held to.
- **`skills/`** — three **GitHub Copilot CLI** skills (`bafa-map`, `bafa-build`, `bafa-verify`)
  to add the *next* legacy screens to `app/` the same way.

> Verified locally: the new app passes **6/6 journeys** (dashboard 3/3, widget 3/3); `selftest` 98 checks.

## The loop
| Stage | What | Who | LLM? |
|---|---|---|---|
| **MAP** | analyze one legacy screen → `output/spec.md` | copilot `/bafa-map` | yes |
| **BUILD** | add it to `app/`, honoring `CONTRACT.md` | copilot `/bafa-build` | yes |
| **VERIFY** | parity tests vs legacy behaviour → report | `verify/` (Python) | **no** |

`CONTRACT.md` is shared by BUILD and VERIFY, so gpt-5.4 builds against a hard pass/fail
instead of eyeballing screenshots.

## Quickstart (in the pod)
```bash
bash setup.sh          # installs skills + deps + the app, then PROVES it (offline tests + real-app parity)
```
That's the whole setup — it builds `app/`, runs the verify kit against it, and prints your
next steps. See the app immediately:
```bash
cd app && VITE_MOCK=1 npm run dev      # http://localhost:5173/  (dashboard)   and   /compensation
```
Re-verify any time: `bash verify-app.sh`. Add the next screen: `/bafa-map` → `/bafa-build` → `bash verify-app.sh`.

## Connect to the real backend (just like the original)
```bash
cd app && cp .env.example .env.local   # set VITE_AUTH_BASE / VITE_DATA_BASE / VITE_COMP_BASE
npm run dev
```
Same endpoints as the original (`/auth/token`, `/report-meta-data/{id}`, `/reports/{...}`,
`/fa-compensation/{fa}`). Defaults to `/BAA/api`; point `VITE_DATA_BASE` at the compensation service.

## What's here
```
README.md  COPILOT-GUIDE.md  RUNBOOK.md  CONTRACT.md  setup.sh  verify-app.sh
app/                                   # the new React UI (dashboard + widget)
skills/{bafa-map,bafa-build,bafa-verify}/SKILL.md
templates/{spec,status}.template.md
verify/                                # deterministic parity kit (see verify/README.md)
output/                                # saved spec.md, screenshots, reports
```

## Why not loom / the heavy agents
Loom re-implemented map+build+verify as one big LLM-wrapped engine — too much to keep
working. The pod's `baa-analysis`/`baa-modernization` agents are 900/700-line whole-app
prompts — too broad for reliable single-screen runs on gpt-5.4. This kit keeps each stage
small and scoped, makes VERIFY deterministic, and ships a real working app.

> Naming: BAFA/BAA only. No client identifiers in artifacts.
