---
name: bafa-build
description: BUILD one BAA screen in React from a saved spec, matching the existing app's patterns and honoring the build/verify CONTRACT. Use for "build the Compensation widget in React", "modernize this screen from spec.md", after bafa-map has produced output/spec.md.
---

# bafa-build — rebuild ONE screen in React, to the contract

You implement the screen described in `output/spec.md` inside this kit's `app/`
(React 19 + Vite), **exposing the exact `data-testid`s and data shape in `CONTRACT.md`**
so the deterministic verify kit passes. Stay scoped to this one screen.

## Before writing code (mandatory, brief)
1. Read `output/spec.md` (the source of truth) and `CONTRACT.md` (the hooks you must
   expose).
2. **Study `app/` once**: read `app/src/screens/ManagerDashboard.tsx` and
   `CompensationWidget.tsx`; trace component → `app/src/api/client.ts` → `styles.css`.
   Match those conventions (a `screens/` component, the `api/` fetch client + token flow,
   the contract `data-testid`s). **Do not introduce new conventions or heavy libraries.**

## Build
3. Create the React component(s) for the screen following those conventions. Render the
   exact legacy labels from `spec.md` (Compensation, Schedule C, Daily/MTD/YTD,
   Production, Comp NNA, CL/MTG).
4. **Honor `CONTRACT.md`**:
   - root `data-testid="comp-widget"`; rows `comp-row-production|compnna|clmtg`; cells
     `comp-cell-<key>-daily|mtd|ytd`; `comp-title`, `comp-asof`, and `comp-error`.
   - Consume the §1 data shape; wire a BFF/REST endpoint that returns it (reuse the
     existing `api/` pattern; the data ultimately comes from the same `BAAXD550` path).
   - The 3 behaviours in §3: rows on happy; `comp-error` on no-data; `comp-error` with
     "Business Analysis Application Error" on backend 500.
5. Match the visual details from `spec.md` (colors/sizes/spacing) closely enough to pass
   the ≤2.5% pixel check at 1366×768.

## Close the loop (this is the point)
6. Run the verifier — it is your hard pass/fail, not your own judgement:
   `bash verify-app.sh`  (or one screen: `python verify/parity/run_parity.py --screen <name>`).
7. For every **FOLLOW-UP** journey, read the assert detail, fix the component to satisfy
   the contract, and re-run. Repeat until all journeys PASS. Then commit.

## Rules
- Reuse shared components/utilities; never hand-code what the library provides.
- Only build what `spec.md` specifies — no extra features.
- If `spec.md` is missing a visible detail, get it from the legacy evidence (or run
  `bafa-map` again) — don't guess.

## Done when
`run_parity.py --screen widget` reports all journeys **PASS** and the pixel diff is
within threshold (or the residual is logged in `verify/PARITY-DELTAS.md` as accepted).
