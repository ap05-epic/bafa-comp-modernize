# MASTER PROMPT — autonomous 1:1 JSP → React conversion loop

Paste everything below the line into **Copilot CLI** (gpt‑5.4) in the pod, after filling in
the CONFIG block. Then let it run — it maps the original app, rebuilds the UI in `new-ui/`,
and loops the checker against the original screenshots until every screen is a 1:1 match.

---

You are converting the legacy **JSP/Struts BAA** application's **UI ONLY** into a **1:1
React replica**. The backend and mainframe stay exactly as they are — the React UI must call
the **same backend endpoints** so the data is identical. Convert from the **original source
code**, and keep the **exact same look** by matching the **original screenshots** with the
checker. Work **autonomously**: do not stop to ask — keep looping until every screen passes.

## CONFIG (edit these to your environment)
- ORIGINAL app (running): `http://127.0.0.1:8080/BAA/`  (login page: `http://127.0.0.1:8080/BAA/jsp/login.jsp`)
  - Use `127.0.0.1` or `localhost` — **NEVER `0.0.0.0`** (that's a bind address, not a destination) and never the `:8000` JPDA debug port. To view in a browser yourself, use the devpod proxy URL `https://<your-devpod-host>/proxy/8080/BAA/jsp/login.jsp`.
- Original source code: `<path to the BAA repo — WEB-INF/struts-config.xml, jsp/, css, js>`
- How to log in to the original (for screenshots): `<creds, or the saved auth_state.json>`
- NEW React app folder: `./new-ui/`  (already a bootable Vite + React 19 app with a backend proxy)
- Checker: `python checker/compare.py`
- Original screenshots (the targets): `./screenshots/`
- Screen list / progress file: `./screens.md`
- 1:1 bar: the checker prints `PASS` (≤ 1.5% pixel diff)

## Tools
- **Screenshot the original with `python checker/snap.py <url> <out.png>`** — it uses the Playwright
  chromium you installed and works even though the team's `webapp-snapshot` / `playwright-cli` skill is
  pointed at a **missing Chrome binary** in this pod. **Do NOT use the team snapshot skill for screenshots
  here — it will fail.** Use `snap.py` (and `compare.py`) instead.
  - Post-login screens need a session: run once
    `python checker/login.py --url http://127.0.0.1:8080/BAA/jsp/login.jsp --user <U> --pass <P> --out auth_state.json`
    (read `login.jsp` for the field names if the defaults don't match), then
    `python checker/snap.py <url> <out.png> --auth auth_state.json`.
- Read the legacy source directly (JSP + fragments + Struts action + JS/CSS) for each screen's structure.
- The new app's dev server: `cd new-ui && npm install && npm run dev` → `http://127.0.0.1:5173` (keep it running).

## THE LOOP — run it for the whole app, non-stop

### Step 1 — MAP (once)
**Start with the LOGIN screen — it needs no auth, so prove the loop there first.** Capture it:
`python checker/snap.py http://127.0.0.1:8080/BAA/jsp/login.jsp screenshots/login.png`.
Then log in for the rest (`python checker/login.py --url http://127.0.0.1:8080/BAA/jsp/login.jsp --user <U> --pass <P> --out auth_state.json`)
and crawl the app through the **real menu** (not synthetic URLs). For every screen and state, save:
- a screenshot with `snap.py` → `screenshots/<screen>.png` (1366×768; add `--auth auth_state.json` for post-login screens),
- the source it comes from (JSP + fragments + Struts action + JS/CSS) and the route/URL → a row in `screens.md`.
Finish with `screens.md` = the ordered checklist, **`login` first** (each `[ ] <screen>`).

### Step 2 — CONVERT each screen, looping until 1:1
For each unchecked screen in `screens.md`:
1. **Read the original code** for that screen — it's the structural source of truth (layout,
   labels, controls, conditional logic, the AJAX/action URLs it calls for data).
2. **Build / refine** the React version in `new-ui/` (add a route + component). Match the
   original's layout, labels, fonts, colors, spacing, and behavior. Get **data from the same
   backend** through the dev proxy (use the same endpoints the legacy source calls).
3. **Run the checker** (start `new-ui` dev server first if needed):
   ```bash
   python checker/compare.py \
     --baseline screenshots/<screen>.png \
     --url http://localhost:5173/<route> \
     --out screenshots/<screen>.diff.png
   ```
4. **Read the verdict.** If it prints `FAIL`: open `screenshots/<screen>.diff.png`, find what
   differs (layout / spacing / color / font / text / missing or extra elements), fix the React
   code, and **go back to step 3**. Repeat until it prints `PASS (1:1)`.
5. Mark the screen `[x]` in `screens.md`, commit, and move to the **next** screen.

### Step 3 — Don't stop
Keep going until **every** screen in `screens.md` is `[x]` and passing. If one screen is
genuinely blocked (can't reach it, missing entitlement), write the precise reason next to it
in `screens.md` and continue with the others — come back later.

**Hard rules on stopping:**
- **Never declare the task complete while any screen is unverified.** A missing baseline or a
  `FAIL` from the checker is NOT "complete" — it's the next thing to fix.
- **If a screenshot fails, it's almost always the team snapshot skill's missing-Chrome config.
  Switch to `python checker/snap.py ...` and continue.** Do not stop because that skill is broken.
- A screen is done ONLY when `compare.py` prints `PASS (1:1)`. Until then, keep looping
  build → check → fix on it.

## Rules
- **UI only.** Never change the backend. Call the same endpoints the legacy app uses (read
  them from the JSP/Struts/JS source).
- **The screenshot is the truth.** The checker (new render vs the original screenshot) is the
  gate — not your own judgment. Keep fixing until it passes; don't mark a screen done on a FAIL.
- **Evidence over guessing.** Every visual decision comes from the original screenshot + the
  original source. Don't invent layout or copy.
- **Autonomous.** Don't pause to ask. Recover from errors and keep going. Inner loop =
  build → check → fix; outer loop = screen by screen.
- **Stack:** React 19 + Vite + TypeScript (already scaffolded in `new-ui/`). Keep it simple so
  it always boots.

**Start now:** MAP the app into `screens.md` + `screenshots/`, then convert screen by screen,
looping the checker until each one is 1:1.
