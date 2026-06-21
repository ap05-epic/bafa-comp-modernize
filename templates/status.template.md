# Status — <Screen Name>

> Lightweight control plane. `bafa-map` seeds it; `bafa-build`/`bafa-verify` update it.

## Project config
- Legacy webapp: `/home/devpod/.copilot/BAX-Test-MainRepo/BAX-BusinessAnalysis/BAA/src/main/webapp`
- React app: `…/business-analysis-next-ui` (Vite, dev `:5173`, base `/BAA/businessAnalysisNext/`)
- Legacy local run: `cd …/BAX-Test-MainRepo && ./run-bax-businessanalysis.sh` (Tomcat `:8080`)
- Verify kit: `<this kit>/verify` · screen config: `verify/screens/<name>.json`
- Spec: `output/spec.md` · QA login: `…/BAA/jsp/login.jsp` · auth state: `verify/auth_state.json`

## This screen
- **Screen**: <name>  ·  **Verify config**: `<name>.json`
- **Stage**: `mapped` → `building` → `verifying` → `done`
- **Current stage**: <mapped>

## Loop log
| date | stage | result | notes |
|---|---|---|---|
| <YYYY-MM-DD> | map | spec saved | <screenshots: …> |
| | build | <PASS/FOLLOW-UP> | <…> |
| | verify | <n/3 journeys> | <report-… .html> |

## Status semantics (strict — same discipline as the BAA agents)
- `mapped` — spec.md + screenshots saved
- `building` — React code in progress
- `verifying` — running `run_parity.py`; not yet all-green
- `done` — all verify journeys PASS (+ pixel within threshold or delta logged)

## Blockers / notes
- <…>

## Next step
- <e.g. run bafa-build for the Compensation widget>
