#!/usr/bin/env python3
"""snap.py -- screenshot a URL to a PNG using the Playwright chromium YOU installed
(`python -m playwright install chromium`).

Use this to capture the ORIGINAL app's baselines. It launches the default bundled
chromium with NO shared config -- so it works even when the team's webapp-snapshot /
playwright-cli skill is pointed at a missing Chrome binary in this pod.

  python snap.py http://127.0.0.1:8080/BAA/jsp/login.jsp screenshots/login.png
  python snap.py http://127.0.0.1:8080/BAA/<screen>     screenshots/<screen>.png --auth auth_state.json --wait "#faComp"

Options: --viewport WxH (default 1366x768), --full-page, --auth <storage_state.json>,
--wait <css selector to wait for>, --timeout <ms>.
"""
from __future__ import annotations

import argparse
import os
import sys


def main():
    ap = argparse.ArgumentParser(description="Screenshot a URL with the installed Playwright chromium")
    ap.add_argument("url")
    ap.add_argument("out")
    ap.add_argument("--auth", help="Playwright storage_state json (for post-login screens)")
    ap.add_argument("--viewport", default="1366x768")
    ap.add_argument("--full-page", action="store_true")
    ap.add_argument("--wait", help="css selector to wait for before the screenshot")
    ap.add_argument("--timeout", type=int, default=45000)
    args = ap.parse_args()

    try:
        vw, vh = (int(x) for x in args.viewport.lower().split("x"))
    except Exception:
        print(f"ERROR: bad --viewport {args.viewport!r} (use WIDTHxHEIGHT)", file=sys.stderr)
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("ERROR: playwright missing -> pip install playwright && python -m playwright install chromium", file=sys.stderr)
        return 3

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()  # default bundled chromium; ignores the team's shared config
        ctx = browser.new_context(
            viewport={"width": vw, "height": vh},
            storage_state=args.auth if (args.auth and os.path.exists(args.auth)) else None,
        )
        page = ctx.new_page()
        page.goto(args.url, wait_until="networkidle", timeout=args.timeout)
        if args.wait:
            try:
                page.wait_for_selector(args.wait, timeout=15000)
            except Exception as exc:
                print(f"WARN: --wait {args.wait!r} not found ({exc}); capturing anyway", file=sys.stderr)
        page.screenshot(path=args.out, full_page=args.full_page)
        ctx.close()
        browser.close()

    print(f"saved {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
