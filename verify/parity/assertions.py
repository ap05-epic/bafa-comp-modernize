"""On-screen assertions for the parity runner + an offline spec validator.

`run_assert` takes a Playwright sync `page` but this module imports nothing, so
`validate_assert` is usable in selftest.py without Playwright installed.

Assert types (declared in screens/<name>.json):
  {"type":"visible","selector":".x"}                 element is visible
  {"type":"hidden","selector":".x"}                  element is hidden/absent
  {"type":"text_present","text":"Foo"}               text appears somewhere on the page
  {"type":"text_absent","text":"Foo"}                text does NOT appear
  {"type":"text_contains","selector":".x","text":"Foo"}   element's text contains Foo
  {"type":"text_equals","selector":".x","text":"Foo"}     element's text == Foo (trimmed)
  {"type":"row_count_min","selector":".ag-row","min":2}   >= N matching elements
"""
from __future__ import annotations

VALID_ASSERT_TYPES = {
    "visible",
    "hidden",
    "text_present",
    "text_absent",
    "text_contains",
    "text_equals",
    "row_count_min",
}


def validate_assert(a):
    """Return a list of problems (empty == valid). Pure; no browser needed."""
    errs = []
    if not isinstance(a, dict):
        return ["assert must be an object"]
    t = a.get("type")
    if t not in VALID_ASSERT_TYPES:
        return [f"unknown assert type: {t!r}"]
    if t in ("visible", "hidden", "text_contains", "text_equals", "row_count_min") and not a.get("selector"):
        errs.append(f"{t} requires 'selector'")
    if t in ("text_present", "text_absent", "text_contains", "text_equals") and "text" not in a:
        errs.append(f"{t} requires 'text'")
    if t == "row_count_min" and not isinstance(a.get("min"), int):
        errs.append("row_count_min requires integer 'min'")
    return errs


def run_assert(page, a, timeout=8000):
    """Execute one assert against a live page. Returns (passed: bool, detail: str)."""
    t = a["type"]
    sel = a.get("selector")
    text = a.get("text")
    try:
        if t == "visible":
            page.wait_for_selector(sel, state="visible", timeout=timeout)
            return True, f"visible: {sel}"
        if t == "hidden":
            page.wait_for_selector(sel, state="hidden", timeout=timeout)
            return True, f"hidden: {sel}"
        if t == "text_present":
            page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=timeout)
            return True, f"text present: {text!r}"
        if t == "text_absent":
            cnt = page.get_by_text(text, exact=False).count()
            return cnt == 0, ("text absent" if cnt == 0 else f"text unexpectedly present ({cnt}x)") + f": {text!r}"
        if t == "text_contains":
            page.wait_for_selector(sel, timeout=timeout)
            actual = (page.locator(sel).first.inner_text() or "").strip()
            ok = text in actual
            return ok, f"{sel} {'contains' if ok else 'MISSING'} {text!r} | actual={actual[:140]!r}"
        if t == "text_equals":
            page.wait_for_selector(sel, timeout=timeout)
            actual = (page.locator(sel).first.inner_text() or "").strip()
            ok = actual == text
            return ok, f"{sel} {'==' if ok else '!='} {text!r} | actual={actual[:140]!r}"
        if t == "row_count_min":
            page.wait_for_selector(sel, timeout=timeout)
            cnt = page.locator(sel).count()
            want = int(a["min"])
            return cnt >= want, f"{sel} count={cnt} (min {want})"
    except Exception as exc:  # timeouts, detached nodes, etc. -> a real finding
        return False, f"{t} {sel or text!r} -> {type(exc).__name__}: {str(exc)[:160]}"
    return False, f"unhandled assert type {t}"
