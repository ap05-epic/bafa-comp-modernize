#!/usr/bin/env python3
"""Capture the LEGACY Compensation widget as a parity baseline (live mode only).

This is OPTIONAL and best-effort. It is only needed for the `widget` screen's
*visual* pixel baseline and *data* parity reference; the deterministic stub-mode
asserts do not need it.

It uses a saved Playwright auth_state (from webapp-snapshot/scripts/save_auth_state.py
against the BAA QA login) so it can reach the SSO-gated legacy app, navigates to the
FA Summary shell, screenshots the `#faComp` Compensation box, and extracts the
Production / Comp NNA / CL/MTG values by row-text anchoring (the legacy widget has
no stable cell ids).

  python capture_legacy.py --screen widget

Outputs:
  output/baseline/<screen>_legacy.png        (pixel baseline)
  output/baseline/<screen>_legacy_data.json  (data reference)

If the legacy deep-link 500s (BAA is stateful -- synthetic nav often fails where the
real menu path works), capture the box manually with the webapp-snapshot skill instead
and drop the two files into output/baseline/ yourself. See RUNBOOK.md.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY_DIR = os.path.dirname(HERE)

# JS run in the page: find rows under #faComp by label text, read the 2nd-4th cells
# (Daily / MTD / YTD). Best-effort; returns {label: [daily, mtd, ytd]}.
EXTRACT_JS = r"""
() => {
  const root = document.querySelector('#faComp');
  if (!root) return { error: 'no #faComp container found' };
  const labels = ['Production', 'Comp NNA', 'CL/MTG'];
  const out = {};
  const rows = Array.from(root.querySelectorAll('tr'));
  for (const label of labels) {
    const row = rows.find(r => (r.innerText || '').includes(label));
    if (!row) { out[label] = null; continue; }
    const cells = Array.from(row.querySelectorAll('td')).map(td => (td.innerText || '').trim());
    // cell[0] is the label; the next non-empty cells are Daily/MTD/YTD
    out[label] = cells.slice(1).filter(c => c !== '').slice(0, 3);
  }
  return out;
}
"""


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser(description="Capture the legacy Compensation widget baseline")
    ap.add_argument("--screen", default="widget")
    ap.add_argument("--config")
    ap.add_argument("--headed", action="store_true")
    args = ap.parse_args()

    cfg_path = args.config or os.path.join(VERIFY_DIR, "config.json")
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(VERIFY_DIR, "config.example.json")
    cfg = load_json(cfg_path)
    screen = load_json(os.path.join(VERIFY_DIR, "screens", args.screen + ".json"))
    legacy = screen.get("legacy", {})
    if not legacy.get("url"):
        print("ERROR: screen config has no legacy.url to capture from.", file=sys.stderr)
        return 2

    out_base = os.path.abspath(os.path.join(VERIFY_DIR, cfg.get("output_dir", "../output"), "baseline"))
    os.makedirs(out_base, exist_ok=True)
    auth = os.path.join(VERIFY_DIR, cfg.get("auth_state", "auth_state.json"))
    if not os.path.exists(auth):
        print(
            f"ERROR: no auth_state at {auth}.\n"
            "Create it once with the pod's webapp-snapshot skill:\n"
            "  python3 ~/.copilot/skills/webapp-snapshot/scripts/save_auth_state.py \\\n"
            "    --url https://REPLACE-ME-baa-qa-host/BAA/jsp/login.jsp \\\n"
            f"    --output {auth}",
            file=sys.stderr,
        )
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("ERROR: Playwright not installed (pip install playwright && python -m playwright install chromium)", file=sys.stderr)
        return 3

    url = legacy["url"]
    selector = legacy.get("selector", "#faComp")
    viewport = cfg.get("viewport", {"width": 1366, "height": 768})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(viewport=viewport, storage_state=auth)
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        try:
            page.wait_for_selector(selector, timeout=20000)
        except Exception:
            print(
                f"WARNING: '{selector}' not found. BAA is stateful -- a synthetic deep link often 500s.\n"
                "Reach the FA Summary shell via the real menu (login -> Quick Search AB10 -> wait for hydration),\n"
                "or capture the box manually with the webapp-snapshot skill. See RUNBOOK.md.",
                file=sys.stderr,
            )

        png = os.path.join(out_base, f"{args.screen}_legacy.png")
        try:
            page.locator(selector).first.screenshot(path=png)
        except Exception:
            page.screenshot(path=png, full_page=False)

        try:
            data = page.evaluate(EXTRACT_JS)
        except Exception as exc:
            data = {"error": f"extract failed: {exc}"}
        with open(os.path.join(out_base, f"{args.screen}_legacy_data.json"), "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

        context.close()
        browser.close()

    print(f"Saved baseline -> {png}")
    print(f"Saved data     -> {os.path.join(out_base, f'{args.screen}_legacy_data.json')}")
    print("Review both; the data JSON is your reference for React-vs-legacy value parity.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
