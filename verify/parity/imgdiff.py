"""Pixel diff using Pillow. A *soft* visual signal for faithful-rebuild screens
(e.g. the Compensation widget). It never fails a journey on its own; it reports a
diff % and writes a highlighted diff image for human review.

Pillow is optional. If it is missing, the verify run still works (asserts are the
hard gate); only the visual-diff signal is skipped.
"""
from __future__ import annotations


def available():
    try:
        import PIL  # noqa: F401

        return True
    except Exception:
        return False


def _pil():
    try:
        from PIL import Image, ImageChops

        return Image, ImageChops
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Pillow is required for visual diff: pip install pillow") from exc


def diff_images(path_a, path_b, out_diff_path=None, tolerance=12):
    """Compare two PNGs. `tolerance` is a per-pixel luma delta (0-255) below which a
    pixel is considered unchanged. Returns a dict with diff_percent. Resizes B to A
    if dimensions differ (and flags it)."""
    Image, ImageChops = _pil()
    a = Image.open(path_a).convert("RGB")
    b = Image.open(path_b).convert("RGB")
    size_mismatch = a.size != b.size
    if size_mismatch:
        b = b.resize(a.size)
    diff = ImageChops.difference(a, b)
    gray = diff.convert("L")  # luma of the per-pixel difference
    mask = gray.point(lambda v: 255 if v > tolerance else 0)
    changed = mask.histogram()[255]
    w, h = a.size
    total = w * h
    pct = (changed / total * 100.0) if total else 0.0
    if out_diff_path:
        # amplify the raw difference so reviewers can see where it diverged
        diff.point(lambda v: min(255, v * 6)).save(out_diff_path)
    return {
        "width": w,
        "height": h,
        "diff_pixels": changed,
        "total_pixels": total,
        "diff_percent": round(pct, 4),
        "size_mismatch": size_mismatch,
    }


def selftest(tmp_dir):
    """Offline self-check: identical images -> 0%, a changed block -> > 0%."""
    if not available():
        return {"skipped": "Pillow not installed"}
    import os

    from PIL import Image

    a_path = os.path.join(tmp_dir, "_a.png")
    b_path = os.path.join(tmp_dir, "_b.png")
    same_path = os.path.join(tmp_dir, "_a2.png")
    Image.new("RGB", (40, 40), (10, 20, 30)).save(a_path)
    Image.new("RGB", (40, 40), (10, 20, 30)).save(same_path)
    img = Image.new("RGB", (40, 40), (10, 20, 30))
    for y in range(0, 20):
        for x in range(0, 20):
            img.putpixel((x, y), (255, 255, 255))
    img.save(b_path)
    identical = diff_images(a_path, same_path)
    changed = diff_images(a_path, b_path)
    ok = identical["diff_percent"] == 0.0 and changed["diff_percent"] > 0.0
    return {"ok": ok, "identical": identical["diff_percent"], "changed": changed["diff_percent"]}
