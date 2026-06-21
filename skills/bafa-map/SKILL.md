---
name: bafa-map
description: MAP one legacy BAA screen for modernization. Analyze a single Struts/JSP screen (source + runtime), capture every visible state/label/selector and its data path, and SAVE a parity-ready spec.md + screenshots. Use for "map the Compensation widget", "analyze fa_compensation.jsp", or any single BAA screen before rebuilding it in React.
---

# bafa-map — map ONE legacy BAA screen, then save the spec

You analyze **one screen at a time** (default: the summary-shell **Compensation
widget**, `BAA/src/main/webapp/jsp/fa_compensation.jsp`). Stay scoped — do not try to
map the whole 169-JSP app. Produce a spec precise enough that `bafa-build` can rebuild
the screen in React without re-discovering anything.

## Inputs
- The legacy webapp: `…/BAX-BusinessAnalysis/BAA/src/main/webapp`
- The target screen (ask the user if unspecified; default = Compensation widget)
- Templates: `templates/spec.template.md`, `templates/status.template.md`
- The build⇄verify contract: `CONTRACT.md` (your spec must support these testids/states)

## Do this
1. **Read the source** for just this screen: the JSP + its included fragments, the
   Struts action(s), the client JS/AJAX, and the service→DAO→stored-proc data path.
   For the Compensation widget that chain is: `AjaxCompensationAction` →
   `SummaryBuilder.getFASummaryCompBox` → `ScheduleCDAOImpl.getFASummaryCompInfo` →
   stored proc `BAAXD550` (FA_GET_OVERALL=3).
2. **Enumerate every user-visible state**: default/happy, no-data, and error. For each,
   record the exact labels, the row/column structure, CSS values (colors/sizes/spacing),
   and which container/selectors render it (e.g. legacy `#faComp`, rows by label text).
3. **Capture runtime evidence** with the `webapp-snapshot` skill against the running
   legacy app (use the saved `auth_state.json`; viewport **1366×768**). Save PNGs to
   `output/screenshots/`. If a deep link 500s, reach the screen via the real menu
   (login → Quick Search `AB10` → wait for hydration → open the FA Summary shell).
4. **Map the data**: list every value the screen shows and where it comes from
   (column/field → service/DAO/SP). Note the new REST/BFF endpoint that should serve it
   and confirm it matches the data shape in `CONTRACT.md` §1.
5. **Write `output/spec.md`** from `templates/spec.template.md` — fill every section:
   states, labels, selectors, CSS, data path, the 3 paths, and the files to create.
   Seed `output/status.md` from `templates/status.template.md`.

## Rules (lean + reliable)
- One screen, fully, then stop. Evidence over inference — never invent a state you
  didn't see in the running app or the source.
- Every screenshot you save must be referenced in `spec.md`.
- Keep the spec concrete and short; `bafa-build` reads it top-to-bottom.

## Done when
`output/spec.md` covers the happy / no-data / error states with exact labels, selectors,
CSS, and the data path; screenshots are saved and referenced; `output/status.md` points
`bafa-build` at the screen. Commit `output/`.
