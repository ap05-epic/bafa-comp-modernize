"""Deterministic report rendering for the BAFA Comp parity kit.

No Playwright / network imports here on purpose, so selftest.py can exercise
report rendering offline (and so the report layer stays dependency-free).
"""
from __future__ import annotations

import html
import json


def aggregate(results):
    """results: list of journey result dicts -> summary dict."""
    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "all_passed": total > 0 and passed == total,
    }


def render_json(screen_name, results, generated_at="(stamped at write time)"):
    payload = {
        "screen": screen_name,
        "generatedAt": generated_at,
        "summary": aggregate(results),
        "journeys": results,
    }
    return json.dumps(payload, indent=2)


def render_html(screen_name, results):
    summary = aggregate(results)
    sections = []
    for r in results:
        ok = r.get("passed")
        badge = "PASS" if ok else "FOLLOW-UP"
        color = "#0a7a55" if ok else "#c0392b"
        asserts_html = "".join(
            "<li style='color:{c}'>{mark} {detail}</li>".format(
                c="#0a7a55" if a["passed"] else "#c0392b",
                mark="&#10003;" if a["passed"] else "&#10007;",
                detail=html.escape(str(a.get("detail", ""))),
            )
            for a in r.get("asserts", [])
        )
        shot = r.get("screenshot")
        shot_html = (
            "<div><img src='{s}' style='max-width:680px;border:1px solid #ccc;margin-top:8px'/></div>".format(
                s=html.escape(shot)
            )
            if shot
            else ""
        )
        pixel = r.get("pixel")
        pixel_html = ""
        if pixel and "error" not in pixel:
            pixel_html = (
                "<p>Visual diff vs legacy baseline: <b>{d}%</b> "
                "(threshold {t}% &mdash; {state})</p>".format(
                    d=pixel.get("diff_percent"),
                    t=pixel.get("threshold_percent", "-"),
                    state="within" if pixel.get("within_threshold") else "OVER (review)",
                )
            )
        elif pixel and "error" in pixel:
            pixel_html = "<p>Visual diff: {}</p>".format(html.escape(str(pixel["error"])))
        nav = (
            "<p style='color:#c0392b'>Navigation error: {}</p>".format(html.escape(str(r["navError"])))
            if r.get("navError")
            else ""
        )
        sections.append(
            "<section style='margin:18px 0;padding:14px;border:1px solid #ddd;border-radius:8px'>"
            "<h3 style='margin:0 0 8px'>{title} "
            "<span style='background:{color};color:#fff;padding:2px 10px;border-radius:11px;font-size:12px'>{badge}</span>"
            "</h3>{nav}<ul style='margin:6px 0'>{asserts}</ul>{pixel}{shot}</section>".format(
                title=html.escape(str(r.get("title", r.get("id", "?")))),
                color=color,
                badge=badge,
                nav=nav,
                asserts=asserts_html,
                pixel=pixel_html,
                shot=shot_html,
            )
        )
    head = (
        "<h1 style='margin-bottom:4px'>BAFA Comp parity &mdash; {screen}</h1>"
        "<p style='color:#555'><b>{passed}/{total}</b> journeys match legacy expectations "
        "(green = matches legacy, red = needs follow-up).</p>".format(
            screen=html.escape(screen_name), passed=summary["passed"], total=summary["total"]
        )
    )
    return (
        "<!doctype html><meta charset='utf-8'><title>BAFA Comp parity &mdash; {s}</title>"
        "<body style='font-family:Segoe UI,Arial,sans-serif;max-width:880px;margin:24px auto;color:#222'>"
        "{head}{body}</body>".format(s=html.escape(screen_name), head=head, body="".join(sections))
    )
