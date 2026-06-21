# bafa-comp-modernize

A lean, working **MAP → BUILD → VERIFY** loop for modernizing legacy BAA screens to
React — built to run in the pod with **GitHub Copilot CLI (gpt-5.4)** and your
existing pod skills. First screen: **BAFA Comp** (FA Comp Summary).

This is the loom idea (map the old app → rebuild in React → prove parity) **stripped to
what actually works**: the LLM does only what it's good at (explore, write code) against
a **deterministic spec and a deterministic test**. No custom engine to break.

## The loop

| Stage | What | Who runs it | LLM? |
|---|---|---|---|
| **MAP** | analyze one legacy screen, save `output/spec.md` + screenshots | copilot `/bafa-map` | yes |
| **BUILD** | rebuild it in React, honoring `CONTRACT.md` | copilot `/bafa-build` | yes |
| **VERIFY** | deterministic parity tests (happy/validation/error) → report | `verify/` (Python) | **no** |

The trick that makes it converge: **`CONTRACT.md` is shared by BUILD and VERIFY**, so
gpt-5.4 builds against a hard pass/fail instead of eyeballing screenshots.

## Two screens, one kit
- **Dashboard** (already React) → `--screen dashboard`: verify-only behaviour parity = **your ticket**, runnable immediately.
- **Compensation widget** (still legacy JSP) → `--screen widget`: the full MAP→BUILD→VERIFY demo, with pixel + data parity.

## Quickstart (in the pod)
```bash
# 1. one-shot setup: installs skills + deps and PROVES the engine works (offline + browser smoke)
bash setup.sh

# 2. VERIFY the dashboard = the ticket (no build needed)
( cd …/business-analysis-next-ui && npm install && npm run dev )   # serves :5173
python verify/parity/run_parity.py --screen dashboard              # -> output/report-dashboard.html

# 3. full loop for the widget:  /bafa-map  →  /bafa-build  →  python verify/parity/run_parity.py --screen widget
```
`setup.sh` ends by printing your exact next steps. Prefer manual control? See
**[COPILOT-GUIDE.md](COPILOT-GUIDE.md)** / **[RUNBOOK.md](RUNBOOK.md)**.

**Full step-by-step with Copilot:** see **[COPILOT-GUIDE.md](COPILOT-GUIDE.md)**.
**Exact command sequence:** see **[RUNBOOK.md](RUNBOOK.md)**.

## What's here
```
README.md  COPILOT-GUIDE.md  RUNBOOK.md  CONTRACT.md
skills/{bafa-map,bafa-build,bafa-verify}/SKILL.md   # GitHub Copilot CLI skills
templates/{spec,status}.template.md                  # MAP fills these
verify/                                              # the deterministic kit (see verify/README.md)
output/                                              # saved spec.md, screenshots, reports
copilot-instructions.snippet.md                      # optional build-conventions for the React repo
```

## Why not loom / the heavy agents
Loom re-implemented map+build+verify as one big LLM-wrapped engine — too much surface to
keep working. The pod's `baa-analysis`/`baa-modernization` agents are 900/700-line
whole-app prompts — too broad for reliable single-screen runs on gpt-5.4. This kit keeps
each stage **small and scoped**, and makes VERIFY deterministic. It's the reliable core;
the heavy agents remain available for a broad whole-app pass.

> Naming: BAFA/BAA only. No client identifiers in artifacts.
