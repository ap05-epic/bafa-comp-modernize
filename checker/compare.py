#!/usr/bin/env python3
"""compare.py -- the 1:1 visual checker.

Diffs a NEW React screen against the ORIGINAL screenshot (the thing it must match).
The conversion loop runs this every iteration to decide "is it 1:1 yet?". No app launching,
no stubs -- just: capture the new screen, pixel-diff it against the original, say PASS/FAIL.

Usage:
  # capture the new screen from its URL and diff vs the original screenshot:
  python compare.py --baseline screenshots/login.png --url http://localhost:5173/login

  # diff two screenshots you already have:
  python compare.py --baseline screenshots/login.png --candidate /tmp/new-login.png

  # also capture the ORIGINAL live (needs the saved auth_state for the legacy app):
  python compare.py --baseline-url http://localhost:8080/BAA/login --url http://localhost:5173/login --auth auth_state.json

Prints  "DIFF x.xx%  PASS|FAIL",  writes a highlighted diff image (--out) and
compare-result.json, and exits 0 (PASS, <= threshold) or 1 (FAIL).

Deps:  pip install playwright pillow   &&   python -m playwright install chromium
"""
from __future__ import annotations

import argparse
import json
import os
import sys


def capture(url, out_path, viewport, full_page, auth=None):
    from playwright.sync_api import sync_playwright

    w, h = viewport
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": w, "height": h},
            storage_state=auth if (auth and os.path.exists(auth)) else None,
        )
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle", timeout=45000)
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        page.screenshot(path=out_path, full_page=full_page)
        ctx.close()
        browser.close()


def diff_images(a_path, b_path, out_path, tolerance):
    from PIL import Image, ImageChops

    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    size_mismatch = a.size != b.size
    if size_mismatch:
        b = b.resize(a.size)
    d = ImageChops.difference(a, b)
    mask = d.convert("L").point(lambda v: 255 if v > tolerance else 0)
    changed = mask.histogram()[255]
    total = a.size[0] * a.size[1]
    pct = (changed / total * 100.0) if total else 0.0
    if out_path:
        d.point(lambda v: min(255, v * 6)).save(out_path)
    return pct, size_mismatch


def main():
    ap = argparse.ArgumentParser(description="1:1 visual checker (new React screen vs original screenshot)")
    ap.add_argument("--baseline", help="original screenshot (png) to match")
    ap.add_argument("--baseline-url", help="capture the ORIGINAL live instead of --baseline")
    ap.add_argument("--candidate", help="new screenshot (png)")
    ap.add_argument("--url", help="capture the NEW screen from this URL")
    ap.add_argument("--auth", help="Playwright storage_state json (for the legacy app login)")
    ap.add_argument("--out", default="diff.png", help="where to write the highlighted diff image")
    ap.add_argument("--threshold", type=float, default=1.5, help="max %% pixels different to count as 1:1 (default 1.5)")
    ap.add_argument("--tolerance", type=int, default=12, help="per-pixel luma tolerance (default 12)")
    ap.add_argument("--viewport", default="1366x768")
    ap.add_argument("--full-page", action="store_true")
    args = ap.parse_args()

    try:
        vw, vh = (int(x) for x in args.viewport.lower().split("x"))
    except Exception:
        print(f"ERROR: bad --viewport {args.viewport!r} (use WIDTHxHEIGHT)", file=sys.stderr)
        return 2

    # check deps early with a clear message
    try:
        import PIL  # noqa: F401
    except Exception:
        print("ERROR: Pillow missing -> pip install pillow", file=sys.stderr)
        return 3

    # resolve the baseline (original) image
    baseline = args.baseline
    if args.baseline_url:
        baseline = "_baseline_capture.png"
        try:
            capture(args.baseline_url, baseline, (vw, vh), args.full_page, args.auth)
        except Exception as exc:
            print(f"ERROR capturing baseline-url: {exc}", file=sys.stderr)
            return 3
    if not baseline or not os.path.exists(baseline):
        print("ERROR: need --baseline <png> or --baseline-url <url>", file=sys.stderr)
        return 2

    # resolve the candidate (new) image
    candidate = args.candidate
    if args.url:
        candidate = "_candidate_capture.png"
        try:
            capture(args.url, candidate, (vw, vh), args.full_page)
        except Exception as exc:
            print(f"ERROR capturing --url (is the new app running?): {exc}", file=sys.stderr)
            return 3
    if not candidate or not os.path.exists(candidate):
        print("ERROR: need --candidate <png> or --url <url>", file=sys.stderr)
        return 2

    try:
        pct, size_mismatch = diff_images(baseline, candidate, args.out, args.tolerance)
    except Exception as exc:
        print(f"ERROR diffing: {exc}", file=sys.stderr)
        return 3

    ok = pct <= args.threshold
    with open("compare-result.json", "w", encoding="utf-8") as fh:
        json.dump(
            {
                "diff_percent": round(pct, 3),
                "threshold": args.threshold,
                "pass": ok,
                "size_mismatch": size_mismatch,
                "baseline": baseline,
                "candidate": candidate,
                "diff_image": args.out,
            },
            fh,
            indent=2,
        )

    verdict = "PASS (1:1)" if ok else "FAIL"
    extra = "   [SIZE MISMATCH -- capture both at the same viewport]" if size_mismatch else ""
    print(f"DIFF {pct:.2f}%  {verdict}  (threshold {args.threshold}%){extra}")
    print(f"diff image: {args.out}   result: compare-result.json")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
