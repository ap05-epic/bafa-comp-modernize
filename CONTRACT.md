# CONTRACT — the shared agreement between BUILD and VERIFY

This is the linchpin of the loop. **BUILD makes the React component expose exactly
these hooks; VERIFY asserts exactly these hooks.** Because both sides agree up front,
gpt-5.4 gets a hard, repeatable pass/fail to build and fix against — instead of
eyeballing screenshots. Don't change one side without the other.

> Scope: the **Compensation summary widget** (rebuild of `jsp/fa_compensation.jsp`).
> The already-built dashboard is verified behaviourally and needs no new contract.

## 1. Data shape (the new endpoint + the stub fixtures agree)

The rebuilt widget fetches its data and renders this shape (mirrors the legacy
`BAAXD550` / `FASummaryCompBox`). The new BFF endpoint returns it; the verify stubs
(`verify/fixtures/comp_happy.json`, `comp_nodata.json`) return it; `capture_legacy.py`
writes the *real* AB10 values into `output/baseline/widget_legacy_data.json` in it:

```json
{
  "asOf": "Apr 2026",
  "rows": [
    { "key": "production", "label": "Production", "daily": "12,500", "mtd": "146,200", "ytd": "1,284,900" },
    { "key": "compNNA",    "label": "Comp NNA",   "daily": "...",    "mtd": "...",     "ytd": "..." },
    { "key": "clMtg",      "label": "CL/MTG",     "daily": "...",    "mtd": "...",     "ytd": "..." }
  ]
}
```
Empty `rows` ⇒ the widget shows its **no-data** state.

## 2. DOM contract (`data-testid`s the React widget MUST expose)

| `data-testid` | On | Meaning |
|---|---|---|
| `comp-widget` | root container | the whole Compensation box |
| `comp-title` | the heading | renders the text **"Compensation"** |
| `comp-asof` | footer | the green "as of" period (e.g. `Apr 2026`) |
| `comp-row-production` | a row | the **Production** row |
| `comp-row-compnna` | a row | the **Comp NNA** row |
| `comp-row-clmtg` | a row | the **CL/MTG** row |
| `comp-cell-<key>-daily` / `-mtd` / `-ytd` | each value cell | e.g. `comp-cell-production-ytd` |
| `comp-error` | the error/no-data panel | shown for the no-data **and** backend-error states (hidden on happy) |

Visible labels must match the legacy widget exactly: **Compensation, Schedule C,
Daily, MTD, YTD, Production, Comp NNA, CL/MTG** (legacy source: `jsp/fa_compensation.jsp`).

## 3. Behaviour contract (the 3 paths)

| Path | Trigger | Required result |
|---|---|---|
| **Happy** | endpoint returns rows | `comp-widget` + the three `comp-row-*` visible; values in the `comp-cell-*` cells; `comp-error` hidden |
| **No-data / invalid** | endpoint returns empty `rows` (or 404) | `comp-error` visible; the `comp-row-*` hidden |
| **Backend error** | endpoint 500s / times out | `comp-error` visible, containing **"Business Analysis Application Error"** (mirrors the legacy error semantics: `error.jsp` / the `compensation` error tag) |

## 4. Visual contract

Faithful rebuild ⇒ the widget should visually match the legacy `#faComp` box at
**1366×768**. VERIFY pixel-diffs the React happy state against
`output/baseline/widget_legacy.png` (captured by `capture_legacy.py`). This is a
**soft** signal (target ≤ 2.5% diff) for the deltas log — the hard gate is §2–§3.

---
The matching config is `verify/screens/widget.json`. If you change a `data-testid`
here, change it there too (and re-run `python verify/parity/selftest.py`).
