"""Smoke test for v3/index.html.

Usage (from the repo root):
  pip install playwright && playwright install chromium
  python3 -m http.server 8765 --directory v3 &
  python3 tools/v3-smoke-test.py http://127.0.0.1:8765

Checks sample MSI values, NO DATA before a count, NOAA fill, the decision
re-confirm flag, phone width and console errors. Exits 1 on any failure.
"""
import sys
from playwright.sync_api import sync_playwright

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  ({detail})" if detail else ""))
    if not cond:
        fails.append(name)


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("dialog", lambda d: d.accept())
    pg.goto(base + "/index.html")
    pg.evaluate("localStorage.clear()")
    pg.reload()
    pg.wait_for_timeout(400)
    T = lambda i: pg.inner_text("#" + i)

    check("app ready", "App ready" in T("jsStatus"), T("jsStatus"))
    check("no data before count", "NO DATA" in T("ovTag") and "WITHIN" not in T("ovChips"))

    for k, want in [("A", "4.0"), ("B", "16.8"), ("C", "3.2")]:
        pg.click(f"[data-scenario={k}]")
        pg.wait_for_timeout(100)
        check(f"sample {k} MSI {want}", T("msiBig") == want, T("msiBig"))
    check("sample C: MPFUB exceeds", "MPFUB · EXCEEDS LIMIT" in T("ovChips"))

    pg.select_option("#regionId", "cape-henry")
    pg.select_option("#beachId", "little-creek-north")
    pg.click("#noaaFill")
    pg.wait_for_timeout(150)
    check("NOAA fill marked estimate", "NOAA ESTIMATE" in T("ovSource"))
    check("sample fields cleared on NOAA fill", pg.input_value("#driftFeet") == "0")
    wind = float(pg.input_value("#windSpeed") or 0)
    check("NWS wind in knots (KNGU < 20 kts)", wind < 20, f"{wind} kts")

    pg.select_option("#decRole", "BMU OIC")
    pg.select_option("#decValue", "GO")
    pg.fill("#decInitials", "T1")
    pg.wait_for_timeout(100)
    check("decision recorded", "GO by BMU OIC" in T("ovDecision"))
    pg.fill("#pCount", "30")
    pg.dispatch_event("#pCount", "change")
    check("re-confirm after input change", "RE-CONFIRM" in T("ovDecision"))

    pg.set_viewport_size({"width": 390, "height": 844})
    pg.wait_for_timeout(200)
    w = pg.evaluate("document.documentElement.scrollWidth")
    check("no sideways scroll at 390px", w <= 390, f"{w}px")
    check("no page errors", not errs, "; ".join(errs))
    b.close()

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
