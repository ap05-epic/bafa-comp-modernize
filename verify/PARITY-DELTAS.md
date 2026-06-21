# BAFA Comp — UI Deltas & Triage (AC4)

Differences between the React UI and the legacy interface, kept **separate from
functional defects**. Each delta is triaged **Accepted** (intended modernization) or
**Follow-up** (needs a fix / product decision). Update after each verify run; attach the
diff image from `output/screenshots/<screen>_<journey>_diff.png` where relevant.

## How to use
- A verify **FOLLOW-UP** that is a real behaviour/data gap → log under Follow-up, raise it.
- A visual difference that is an intended redesign → log under Accepted with the reason.
- Pixel diff over threshold on the widget → inspect the diff image, then Accept or Follow-up.

---

## Screen A — FA Comp Summary dashboard (new design)

| ID | Delta | Type (visual / behaviour / data) | Triage | Notes |
|----|-------|----------------------------------|--------|-------|
| A-D1 | Full-page report is a new AG-Grid design, not a rebuild of a legacy JSP report | visual | **Accepted** | No pre-React full-page report existed; legacy route now iframes this. Parity = behaviour/data, not pixel. |
| A-D2 | Error copy differs from legacy ("technical issue…" vs "Business Analysis Application Error") | behaviour (copy) | <Accepted/Follow-up> | Confirm with product whether legacy wording must be preserved. |
| | | | | |

## Screen B — Compensation widget (faithful rebuild)

| ID | Delta | Type | Triage | Notes |
|----|-------|------|--------|-------|
| B-D1 | <e.g. React modal vs legacy inline panel> | visual | <…> | diff: `output/screenshots/widget_happy_diff.png` |
| | | | | |

---
_Last verify run:_ <screen> — <n/total journeys> — <date> — report: `output/report-<screen>.html`
