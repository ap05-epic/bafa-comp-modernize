# Spec — <Screen Name> (legacy → React)

> Filled by `bafa-map` for ONE screen. Keep it concrete; `bafa-build` reads it
> top-to-bottom. Replace every `<…>`. Cite source files and saved screenshots.

## 1. Identity
- **Screen**: <e.g. Compensation summary widget>
- **Legacy JSP(s)**: <jsp/fa_compensation.jsp + fragments>
- **Struts action(s) / class**: <ajaxCompensationAction → AjaxCompensationAction>
- **Reached at runtime by**: <login → Quick Search AB10 → FA Summary shell → #faComp>
- **Legacy container selector**: <#faComp>

## 2. Data path (where every value comes from)
- **Action → builder → DAO → SP**: <AjaxCompensationAction → SummaryBuilder.getFASummaryCompBox → ScheduleCDAOImpl.getFASummaryCompInfo → BAAXD550 (FA_GET_OVERALL=3)>
- **Source tier**: <DB2 / mainframe via stored proc>
- **New REST/BFF endpoint to serve it**: <GET /BAA/api/fa-compensation/{fa}> returning the `CONTRACT.md` §1 shape
- **Field → value map**: <Production/Comp NNA/CL/MTG × Daily/MTD/YTD>

## 3. Visible states (capture + describe EACH)
For each: screenshot ref, exact labels, structure, and the controlling condition.

### 3a. Happy (data present)
- Screenshot: `output/screenshots/<file>.png`
- Labels: <Compensation, Schedule C, Daily, MTD, YTD, Production, Comp NNA, CL/MTG>
- Structure: <rows × period columns; as-of footer (green) "mth/yr">
- Notes: <conditional rows: Award QNR Points / QNR 10M / QNR 1M / Grid Watch>

### 3b. No-data / invalid
- Screenshot: `output/screenshots/<file>.png`
- Behaviour: <box shows no-data message; table hidden>

### 3c. Backend / service error
- Screenshot: `output/screenshots/<file>.png`
- Behaviour: <error rendering; legacy text "Business Analysis Application Error" / "Error Message:"; compensation error tag>

## 4. Visual details (for parity)
- Fonts / sizes: <…>
- Colors: <…>   Borders / spacing: <…>   Widths: <…>
- Paste legacy CSS values worth matching:
```less
<.cw3 { … }>
```

## 5. Contract mapping (must satisfy CONTRACT.md)
| Contract testid | Renders | Legacy evidence |
|---|---|---|
| comp-widget | root box | <#faComp> |
| comp-title | "Compensation" | <…> |
| comp-row-production / -compnna / -clmtg | the 3 rows | <…> |
| comp-cell-<key>-daily/mtd/ytd | value cells | <…> |
| comp-error | no-data + error panel | <…> |
| comp-asof | as-of footer | <…> |

## 6. Files to create (React)
- Component: `business-analysis-next-ui/src/components/<…>/<…>.tsx`
- Styles: `…/<…>.module.less`
- API client: `…/api/<…>.ts`
- BFF endpoint (if new): `BAA/src/main/java/.../api/controller/<…>.java`

## 7. Success criteria (what VERIFY will check)
- [ ] Happy: `comp-widget` + 3 rows visible; values in cells; labels present
- [ ] No-data: `comp-error` visible; rows hidden
- [ ] Backend error: `comp-error` visible with "Business Analysis Application Error"
- [ ] Visual diff vs `output/baseline/widget_legacy.png` ≤ 2.5% @ 1366×768
