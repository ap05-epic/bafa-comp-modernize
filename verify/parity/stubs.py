"""Playwright route() stubs that feed the React app fixture data instead of the
real backend. This is what makes the parity run deterministic and offline: no
/BAA/api backend, no EISL compensation service, no DB2/mainframe needed.

A journey declares which logical endpoints to stub and with what:
  "stubs": {
    "token": "auth_token.json",
    "report_meta": "report_meta_data.json",
    "report_customization": "report_customization_metadata.json",
    "reports": "reports_happy.json",   # or "__500__" to simulate a backend failure
    "log": "__ok__"
  }
Each logical name maps to a URL glob (DEFAULT_ROUTES, overridable per-screen via
the screen's "routes" object). The value is a fixture filename or a sentinel.
"""
from __future__ import annotations

import json
import os

# logical name -> URL glob. Playwright globs: ** matches across "/".
DEFAULT_ROUTES = {
    "token": "**/auth/token",
    "log": "**/log/logdetails",
    "report_meta": "**/report-meta-data/**",
    "report_customization": "**/report-customization-metadata/**",
    "reports": "**/reports/**",
}

SENTINELS = {"__500__", "__404__", "__abort__", "__ok__"}


def _load_fixture(fixtures_dir, name):
    with open(os.path.join(fixtures_dir, name), "r", encoding="utf-8") as fh:
        return fh.read()


def _make_handler(value, fixtures_dir):
    def handler(route):
        try:
            if value == "__500__":
                route.fulfill(
                    status=500,
                    content_type="application/json",
                    body=json.dumps({"message": "Simulated backend failure"}),
                )
            elif value == "__404__":
                route.fulfill(status=404, content_type="application/json", body="{}")
            elif value == "__abort__":
                route.abort()
            elif value == "__ok__":
                route.fulfill(status=200, content_type="application/json", body="{}")
            else:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=_load_fixture(fixtures_dir, value),
                )
        except Exception:
            # A stub must never crash the run; fall back to the real network.
            try:
                route.continue_()
            except Exception:
                pass

    return handler


def register_stubs(page, journey, fixtures_dir, routes=None):
    """Register page.route handlers for each logical stub the journey declares.
    Returns the list of (logical, glob, value) registered, for the report."""
    effective = {**DEFAULT_ROUTES, **(routes or {})}
    registered = []
    for logical, value in journey.get("stubs", {}).items():
        glob = effective.get(logical)
        if not glob:
            continue
        page.route(glob, _make_handler(value, fixtures_dir))
        registered.append((logical, glob, value))
    return registered


def validate_stub_value(value):
    """Pure validation for selftest: a stub value is a sentinel or a *.json name."""
    if value in SENTINELS:
        return []
    if isinstance(value, str) and value.endswith(".json"):
        return []
    return [f"stub value must be a sentinel or a .json fixture name, got {value!r}"]
