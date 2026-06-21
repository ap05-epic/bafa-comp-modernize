# BAFA Comp — Parity Checklist (AC1)

The critical user journeys for FA Comp Summary, the expected legacy behaviour, and how
each is verified. Every row is an **automated, repeatable** check in `run_parity.py`
(green = matches legacy, red = follow-up). Run: `python verify/parity/run_parity.py --screen <screen>`.

## Screen A — FA Comp Summary **dashboard** (already React; the ticket)
New metadata-driven AG-Grid report (`business-analysis-next-ui`/ManagerDashboard). It
*replaced* the legacy full-page route (which now just iframes it); there is **no legacy
pixel baseline**, so parity = **same behaviour + same data semantics**, not pixel match.

| # | Journey | Input | Expected (legacy semantics) | Verify assert |
|---|---|---|---|---|
| A1 | **Happy** | valid report selection (AB10, period) | grid renders with metadata-driven columns, title, legend, disclaimer, Export | `.manager-dashboard-container` + `.ag-theme-alpine` visible; "FA Comp Summary Dashboard", "FA ID", "Name", "Export to Excel", "Demonstrative purposes only." present; ≥2 `.ag-row` |
| A2 | **Validation / no-data** | selection with no rows | the no-data message | `.error-message-text` == "There is no data for your selection." |
| A3 | **Backend error** | report service 500 / timeout | a handled technical-issue message, no crash | `.error-message-text` contains "There was a technical issue which prevented the launch of FA Comp Summary Dashboard" |

## Screen B — Compensation **widget** (legacy JSP → React; the full-loop demo)
Faithful rebuild of `jsp/fa_compensation.jsp` ⇒ pixel + data + behaviour parity all
apply. Asserts use the `CONTRACT.md` `data-testid`s. (Run after `bafa-build`.)

| # | Journey | Input | Expected (legacy) | Verify assert |
|---|---|---|---|---|
| B1 | **Happy** | valid FA (AB10) | Compensation box: Production / Comp NNA / CL/MTG × Daily/MTD/YTD, as-of footer | `comp-widget` + 3 `comp-row-*` visible; labels Compensation/Production/Comp NNA/CL/MTG/Daily/MTD/YTD present; pixel ≤2.5% vs `widget_legacy.png` |
| B2 | **No-data / invalid** | empty / invalid context | no-data state, table hidden | `comp-error` visible; `comp-row-production` hidden |
| B3 | **Backend error** | `BAAXD550`/datasource fails | error rendering (compensation error tag / error page) | `comp-error` visible; "Business Analysis Application Error" present |

## Coverage vs the ticket's acceptance criteria
- **AC3 (happy / validation / backend-error):** A1–A3 and B1–B3.
- **Data parity ("results match legacy"):** stub mode proves rendering; `--mode live` +
  `capture_legacy.py` compares real AB10 values (see `output/baseline/widget_legacy_data.json`).
- **UI parity review (AC, "compare screens/labels/nav"):** screenshots in
  `output/screenshots/` + the pixel diff (widget); redesign deltas logged in `PARITY-DELTAS.md`.
- **Rerunnable (AC5):** re-invoke `run_parity.py` any time; fixtures + auth reused.
- **Clear match/follow-up (AC6):** `output/report-<screen>.html` per-journey PASS/FOLLOW-UP.
