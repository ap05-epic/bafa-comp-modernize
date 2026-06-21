#!/usr/bin/env python3
"""BAFA Comp parity runner -- deterministic React <-> legacy behaviour checks.

Drives the React app through happy / validation / backend-error journeys with
stubbed REST (offline), asserts the on-screen contract, screenshots each state,
and writes output/report-<screen>.{json,html}. NO LLM is involved.

Examples:
  python run_parity.py --screen dashboard          # verify the already-built dashboard (the ticket)
  python run_parity.py --screen widget             # verify the rebuilt Compensation widget (after BUILD)
  python run_parity.py --screen dashboard --only backend_error --headed
  python run_parity.py --screen widget --mode live # use real data + auth_state + legacy pixel baseline

Exit code: 0 if every journey matches expectations, 1 if any needs follow-up.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY_DIR = os.path.dirname(HERE)  # .../verify
sys.path.insert(0, HERE)

import assertions as A  # noqa: E402
import report as report_mod  # noqa: E402
import stubs as stubs_mod  # noqa: E402

try:
    import imgdiff as imgdiff_mod  # noqa: E402
except Exception:
    imgdiff_mod = None


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve_config(args):
    path = args.config or os.path.join(VERIFY_DIR, "config.json")
    if not os.path.exists(path):
        path = os.path.join(VERIFY_DIR, "config.example.json")
    return load_json(path), path


def expand(template, params):
    out = template
    for key, val in params.items():
        out = out.replace("{" + key + "}", str(val))
    return out


def run():
    ap = argparse.ArgumentParser(description="BAFA Comp parity runner")
    ap.add_argument("--screen", required=True, help="screen config name under screens/ (e.g. dashboard, widget)")
    ap.add_argument("--mode", choices=["stub", "live"], default="stub", help="stub = offline fixtures (default); live = real data + auth_state")
    ap.add_argument("--only", help="run only this journey id")
    ap.add_argument("--config", help="path to a config.json")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    args = ap.parse_args()

    cfg, cfg_path = resolve_config(args)
    screen_path = os.path.join(VERIFY_DIR, "screens", args.screen + ".json")
    if not os.path.exists(screen_path):
        print(f"ERROR: no screen config at {screen_path}", file=sys.stderr)
        return 2
    screen = load_json(screen_path)

    fixtures_dir = os.path.join(VERIFY_DIR, cfg.get("fixtures_dir", "fixtures"))
    output_dir = os.path.abspath(os.path.join(VERIFY_DIR, cfg.get("output_dir", "../output")))
    shots_dir = os.path.join(output_dir, "screenshots")
    os.makedirs(shots_dir, exist_ok=True)

    params = dict(cfg)
    params.update(screen.get("params", {}))

    journeys = screen.get("journeys", [])
    if args.only:
        journeys = [j for j in journeys if j.get("id") == args.only]
    if not journeys:
        print("ERROR: no journeys to run (check --only / screen config)", file=sys.stderr)
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print(
            "ERROR: Playwright not installed. In the pod:\n"
            "  pip install -r requirements.txt && python -m playwright install chromium",
            file=sys.stderr,
        )
        return 3

    viewport = cfg.get("viewport", {"width": 1366, "height": 768})
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        ctx_kwargs = {"viewport": viewport}
        if args.mode == "live":
            auth = os.path.join(VERIFY_DIR, cfg.get("auth_state", "auth_state.json"))
            if os.path.exists(auth):
                ctx_kwargs["storage_state"] = auth
            else:
                print(f"NOTE: live mode but no auth_state at {auth}; continuing without it.", file=sys.stderr)
        context = browser.new_context(**ctx_kwargs)

        for journey in journeys:
            jid = journey.get("id", "?")
            page = context.new_page()
            registered = []
            if args.mode == "stub":
                registered = stubs_mod.register_stubs(page, journey, fixtures_dir, screen.get("routes"))

            url = expand(screen["target"]["url"], params)
            nav_error = None
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=int(params.get("nav_timeout_ms", 30000)))
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                ready = screen["target"].get("ready_selector")
                if ready:
                    try:
                        page.wait_for_selector(ready, timeout=int(screen["target"].get("ready_timeout_ms", 15000)))
                    except Exception:
                        pass  # error/no-data states may not render the happy-path container
            except Exception as exc:
                nav_error = f"{type(exc).__name__}: {str(exc)[:160]}"

            assert_results = []
            for a in journey.get("asserts", []):
                passed, detail = A.run_assert(page, a)
                assert_results.append({"assert": a, "passed": passed, "detail": detail})

            shot_name = journey.get("screenshot", f"{args.screen}_{jid}.png")
            shot_path = os.path.join(shots_dir, shot_name)
            try:
                page.screenshot(path=shot_path, full_page=False)
            except Exception:
                shot_path = None

            pixel_result = _maybe_pixel(screen, journey, output_dir, shots_dir, shot_path, args.screen, jid)

            asserts_ok = bool(assert_results) and all(r["passed"] for r in assert_results) and not nav_error
            results.append(
                {
                    "id": jid,
                    "title": journey.get("title", jid),
                    "passed": asserts_ok,  # pixel is a soft signal, never fails the journey
                    "navError": nav_error,
                    "url": url,
                    "stubs": [{"logical": l, "glob": g, "value": v} for (l, g, v) in registered],
                    "asserts": assert_results,
                    "screenshot": (os.path.relpath(shot_path, output_dir).replace(os.sep, "/") if shot_path else None),
                    "pixel": pixel_result,
                }
            )
            page.close()
            mark = "PASS " if asserts_ok else "FOLLOW"
            n_ok = sum(1 for r in assert_results if r["passed"])
            extra = f"  (nav error: {nav_error})" if nav_error else ""
            print(f"[{mark}] {args.screen}/{jid}: {n_ok}/{len(assert_results)} asserts{extra}")

        context.close()
        browser.close()

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f"report-{args.screen}.json"), "w", encoding="utf-8") as fh:
        fh.write(report_mod.render_json(args.screen, results))
    with open(os.path.join(output_dir, f"report-{args.screen}.html"), "w", encoding="utf-8") as fh:
        fh.write(report_mod.render_html(args.screen, results))

    summary = report_mod.aggregate(results)
    print(
        f"\n{args.screen}: {summary['passed']}/{summary['total']} journeys match legacy expectations."
        f"  ->  output/report-{args.screen}.html"
    )
    return 0 if summary["all_passed"] else 1


def _maybe_pixel(screen, journey, output_dir, shots_dir, shot_path, screen_name, jid):
    """Soft visual-diff signal vs a captured legacy baseline (faithful-rebuild screens)."""
    pcfg = screen.get("pixel", {})
    if not (pcfg.get("enabled") and journey.get("pixel_baseline") and imgdiff_mod and shot_path):
        return None
    baseline = os.path.join(output_dir, "baseline", journey["pixel_baseline"])
    if not os.path.exists(baseline):
        return {"error": f"no legacy baseline at baseline/{journey['pixel_baseline']} (run capture_legacy.py)"}
    diff_out = os.path.join(shots_dir, f"{screen_name}_{jid}_diff.png")
    try:
        res = imgdiff_mod.diff_images(baseline, shot_path, diff_out, tolerance=pcfg.get("tolerance", 12))
        thresh = pcfg.get("max_diff_percent", 2.0)
        res["threshold_percent"] = thresh
        res["within_threshold"] = res["diff_percent"] <= thresh
        return res
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    sys.exit(run())
