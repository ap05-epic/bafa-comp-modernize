<!--
OPTIONAL build conventions for the React app. Copy into:
  app/.github/copilot-instructions.md
so GitHub Copilot CLI applies them automatically during /bafa-build.
Keep it short — these are always-on, every-request instructions.
-->

# Build conventions — app/ (BAFA Comp)

When modernizing a BAA screen to React in this repo:

- **Match existing patterns.** Trace one implemented feature (component → state → `api/`
  axios client → `.module.less`) and mirror its structure, naming, and imports. Do not
  introduce new conventions, state libraries, or UI kits.
- **Reuse shared components and utilities.** Never hand-code what the component library
  or `utils/`/`services/` already provide.
- **Honor the parity contract.** Expose the exact `data-testid`s and consume the exact
  data shape defined in the modernization kit's `CONTRACT.md`. The deterministic verify
  kit asserts these — they are not optional.
- **Match legacy labels and visuals.** Use the exact labels and CSS values from
  `output/spec.md` (sourced from the running legacy app + JSP/CSS). No invented copy,
  columns, or states; evidence over guessing.
- **Handle the three states** every screen needs: data present, no-data, and backend
  error (mirror the legacy error semantics).
- **Close the loop.** After building, run the verify kit
  (`run_parity.py --screen <name>`) and fix against its report until all journeys pass —
  the report is the source of truth, not a visual guess.
