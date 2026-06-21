#!/usr/bin/env python3
"""Offline self-test for the parity kit -- NO browser, NO network, NO React app.

Validates that the kit is internally consistent before you carry it to the pod:
  - every fixture is valid JSON with the keys the React app reads
  - every screen config is well-formed (journeys, asserts, stub values)
  - the image-diff utility works (if Pillow is present)
  - the report renderer produces JSON + HTML without crashing

Run:  python selftest.py     (exit 0 = all good)
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import assertions as A  # noqa: E402
import imgdiff as imgdiff_mod  # noqa: E402
import report as report_mod  # noqa: E402
import stubs as stubs_mod  # noqa: E402

problems = []
checks = 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        problems.append(msg)


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ---- 1. fixtures parse + have the keys the React app reads ----------------------
fixtures_dir = os.path.join(VERIFY_DIR, "fixtures")
REQUIRED_FIXTURE_KEYS = {
    "auth_token.json": lambda d: "apiAuthentication" in d
    and {"accessToken", "tokenType"} <= set(d["apiAuthentication"]),
    "report_meta_data.json": lambda d: isinstance(d.get("reportMetaData"), list),
    "report_customization_metadata.json": lambda d: isinstance(d.get("reportCustomizationMetaData"), list),
    "reports_happy.json": lambda d: isinstance(d.get("records"), list) and len(d["records"]) >= 1,
    "reports_nodata.json": lambda d: isinstance(d.get("records"), list) and len(d["records"]) == 0,
}
for name, ok in REQUIRED_FIXTURE_KEYS.items():
    path = os.path.join(fixtures_dir, name)
    check(os.path.exists(path), f"missing fixture: {name}")
    if os.path.exists(path):
        try:
            data = load(path)
            check(ok(data), f"fixture {name} missing expected keys/shape")
        except Exception as exc:
            check(False, f"fixture {name} is not valid JSON: {exc}")

# ---- 2. screen configs are well-formed -----------------------------------------
screens_dir = os.path.join(VERIFY_DIR, "screens")
screen_files = [f for f in os.listdir(screens_dir) if f.endswith(".json")] if os.path.isdir(screens_dir) else []
check(len(screen_files) >= 1, "no screen configs found under screens/")
for sf in screen_files:
    try:
        screen = load(os.path.join(screens_dir, sf))
    except Exception as exc:
        check(False, f"screen {sf} is not valid JSON: {exc}")
        continue
    check(bool(screen.get("target", {}).get("url")), f"screen {sf}: missing target.url")
    check(isinstance(screen.get("journeys"), list) and screen["journeys"], f"screen {sf}: no journeys")
    ids = set()
    for j in screen.get("journeys", []):
        jid = j.get("id")
        check(bool(jid), f"screen {sf}: a journey has no id")
        check(jid not in ids, f"screen {sf}: duplicate journey id {jid!r}")
        ids.add(jid)
        check(isinstance(j.get("asserts"), list) and j["asserts"], f"screen {sf}/{jid}: no asserts")
        for a in j.get("asserts", []):
            errs = A.validate_assert(a)
            check(not errs, f"screen {sf}/{jid}: bad assert {a} -> {errs}")
        for logical, value in j.get("stubs", {}).items():
            errs = stubs_mod.validate_stub_value(value)
            check(not errs, f"screen {sf}/{jid}: stub {logical} -> {errs}")
            if value not in stubs_mod.SENTINELS:
                check(
                    os.path.exists(os.path.join(fixtures_dir, value)),
                    f"screen {sf}/{jid}: stub {logical} points at missing fixture {value}",
                )

# ---- 3. image diff utility ------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    res = imgdiff_mod.selftest(tmp)
    if "skipped" in res:
        print("NOTE: imgdiff self-test skipped (Pillow not installed -- pixel diff is optional/soft).")
    else:
        check(res.get("ok"), f"imgdiff self-test failed: {res}")

# ---- 4. report renderer ---------------------------------------------------------
fake = [
    {"id": "happy", "title": "Happy path", "passed": True,
     "asserts": [{"assert": {}, "passed": True, "detail": "ok"}], "screenshot": "screenshots/x.png", "pixel": None},
    {"id": "backend_error", "title": "Backend error", "passed": False, "navError": None,
     "asserts": [{"assert": {}, "passed": False, "detail": "boom"}], "screenshot": None, "pixel": None},
]
try:
    j = report_mod.render_json("dashboard", fake)
    h = report_mod.render_html("dashboard", fake)
    check("dashboard" in j and "Backend error" in h, "report renderer output missing expected content")
    check(report_mod.aggregate(fake)["passed"] == 1, "report aggregate miscounted")
except Exception as exc:
    check(False, f"report renderer crashed: {exc}")

# ---- summary --------------------------------------------------------------------
if problems:
    print(f"\nSELFTEST FAILED -- {len(problems)} problem(s) of {checks} checks:")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)
print(f"SELFTEST OK -- {checks} checks passed.")
sys.exit(0)
