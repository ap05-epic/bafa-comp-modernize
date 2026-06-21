# app/ — brand-new FA Comp Summary (BAFA Comp) React UI

Replaces `business-analysis-next-ui`. React 19 + Vite + TypeScript, deliberately minimal
and dependency-light so it boots reliably. Connects to the **same backend contract** as
the original (token flow → report metadata/customization/data), so pointing it at the
real backend in the pod works identically.

## Screens
- `/` — full-page **FA Comp Summary dashboard** (metadata-driven table, legend, disclaimer, Export)
- `/compensation` — rebuilt **summary-shell Compensation widget** (Production / Comp NNA / CL/MTG × Daily/MTD/YTD)

## Run it
```bash
npm install
# See it work instantly with bundled sample data (no backend):
VITE_MOCK=1 npm run dev          # http://localhost:5173/  and  /compensation
# Real backend (pod): set the bases, then:
cp .env.example .env.local       # edit VITE_AUTH_BASE / VITE_DATA_BASE / VITE_COMP_BASE
npm run dev
```

## Backend endpoints (same as the original)
- `GET {VITE_AUTH_BASE}/auth/token` → `{ apiAuthentication: { accessToken, tokenType } }`, then bearer-auth:
- `GET {VITE_DATA_BASE}/report-meta-data/{id}` · `/report-customization-metadata/{id}` · `/reports/{id}/{period}/{orgHierCode}/{orgHierRole}/{orgIdentifier}`
- `GET {VITE_COMP_BASE}/fa-compensation/{fa}` (widget) → `{ asOf, rows[] }`

Defaults are `/BAA/api` (so a local Tomcat backend at `:8080/BAA/api` works via a proxy or
same origin). In the pod, set `VITE_DATA_BASE` to the real compensation service base.

## States (all three, per screen)
happy (data) · no-data (empty → message) · backend-error (fetch fails → message). These map
1:1 to the verify kit's journeys.

## Verify it
```bash
# from the repo root, with the app running (npm run dev):
python verify/parity/run_parity.py --screen dashboard
python verify/parity/run_parity.py --screen widget
```
The kit stubs the network (deterministic) and asserts the contract. Selectors/texts here
match `verify/screens/dashboard.json` and `CONTRACT.md` exactly.

## Embed in the legacy shell (optional, later)
`VITE_BASE=/BAA/businessAnalysisNext/ npm run build` and set the kit's `react_base_path`
to match — serves under the same path the legacy JSP iframe expects.
