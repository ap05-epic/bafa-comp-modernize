#!/usr/bin/env python3
"""login.py -- log into the legacy app via its username/password FORM (headless) and save
the session to a storage_state file, so snap.py / compare.py can capture post-login screens.

Works for the local Tomcat BAA **form** login (username + password on /BAA/jsp/login.jsp).
It does NOT do browser-SSO -- for the SSO QA host you'd capture state another way.

  python login.py --url http://127.0.0.1:8080/BAA/jsp/login.jsp --user <U> --pass <P> --out auth_state.json

If the form field names differ, read login.jsp and pass selectors:
  --user-sel "input[name=username]"  --pass-sel "input[name=password]"  --submit-sel "input[type=submit]"
"""
from __future__ import annotations

import argparse
import os
import sys


def main():
    ap = argparse.ArgumentParser(description="Form-login the legacy app and save the session")
    ap.add_argument("--url", required=True, help="login page URL")
    ap.add_argument("--user", required=True)
    ap.add_argument("--pass", dest="password", required=True)
    ap.add_argument("--out", default="auth_state.json")
    ap.add_argument("--user-sel", default="input[name=username]")
    ap.add_argument("--pass-sel", default="input[name=password]")
    ap.add_argument("--submit-sel", default="input[type=submit], button[type=submit]")
    ap.add_argument("--timeout", type=int, default=45000)
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("ERROR: playwright missing -> pip install playwright && python -m playwright install chromium", file=sys.stderr)
        return 3

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(args.url, wait_until="networkidle", timeout=args.timeout)
        try:
            page.fill(args.user_sel, args.user, timeout=15000)
            page.fill(args.pass_sel, args.password, timeout=15000)
        except Exception as exc:
            print(f"ERROR: could not fill the login form ({exc}). Read login.jsp and pass --user-sel/--pass-sel.", file=sys.stderr)
            ctx.close()
            browser.close()
            return 2
        try:
            page.click(args.submit_sel, timeout=15000)
        except Exception:
            page.press(args.pass_sel, "Enter")
        try:
            page.wait_for_load_state("networkidle", timeout=args.timeout)
        except Exception:
            pass

        # crude success check: we should no longer be on the login page
        if "login" in (page.url or "").lower():
            print(f"WARN: still on a login URL ({page.url}) -- credentials or selectors may be wrong.", file=sys.stderr)

        ctx.storage_state(path=args.out)
        ctx.close()
        browser.close()

    print(f"saved session -> {args.out}  (use it: snap.py <url> <out.png> --auth {args.out})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
