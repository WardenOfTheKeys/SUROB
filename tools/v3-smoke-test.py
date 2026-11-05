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
    # Service workers are blocked here so page.route() sees every request; the offline check at the end allows them.
    pg = b.new_context(viewport={"width": 1200, "height": 900}, service_workers="block").new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("dialog", lambda d: d.accept())
    # Block the live forecast so the test checks the packaged fallback and does not depend on the network.
    pg.route("https://api.weather.gov/**", lambda r: r.abort())
    pg.goto(base + "/index.html?all")
    pg.evaluate("localStorage.clear()")
    pg.reload()
    pg.wait_for_timeout(400)
    T = lambda i: pg.inner_text("#" + i)

    check("app ready", "App ready" in T("jsStatus"), T("jsStatus"))
    check("no data before count", "NO DATA" in T("ovTag") and "WITHIN" not in T("ovChips"))
    check("overview shows NOAA estimate", "NOAA estimate: MSI" in T("ovEst"), T("ovEst")[:60])
    paths = pg.eval_on_selector_all("#picChart path", "els => els.map(e => e.getAttribute('stroke'))")
    check("history and forecast lines drawn", "#1d4ed8" in paths and "#c2410c" in paths, str(paths))
    check("offline uses packaged forecast", "packaged copy" in T("picSrc"), T("picSrc")[-90:])

    # Counting pad: the breaker type stays picked, one tap records height and type; undo takes back both.
    pg.click("[data-btype=sCount]")
    for _ in range(3):
        pg.click("[data-padh='2']")
    pg.click("[data-btype=pCount]")
    pg.click("[data-padh='3']")
    pad = (T("totalWavesOut"), pg.input_value("#sCount"), pg.input_value("#pCount"), pg.input_value("#h20"), pg.input_value("#h30"))
    check("one tap records height and breaker type", pad == ("4", "3", "1", "3", "1") and "3.0 ft plunging" in T("padLast"), str(pad) + " " + T("padLast"))
    pg.click("#undoTap")
    pad = (T("totalWavesOut"), pg.input_value("#pCount"), pg.input_value("#h30"), T("padS"))
    check("undo takes back height and type", pad == ("3", "0", "0", "3"), str(pad))

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
    est = T("ovEst").split("MSI ")[1].split()[0]
    check("estimate matches worksheet after NOAA fill", est == T("msiBig"), f"estimate {est}, worksheet {T('msiBig')}")

    pg.select_option("#decRole", "BPTC")
    pg.select_option("#decValue", "GO")
    pg.fill("#decInitials", "T1")
    pg.wait_for_timeout(100)
    check("decision recorded", "GO by BPTC" in T("ovDecision"))
    roles = pg.eval_on_selector_all("#decRole option", "o => o.map(x => x.value).filter(Boolean)")
    check("decision authority is BPTC or SRM", roles == ["BPTC", "SRM"], str(roles))
    pg.click("#editCounts summary")
    pg.fill("#pCount", "30")
    pg.dispatch_event("#pCount", "change")
    check("re-confirm after input change", "RE-CONFIRM" in T("ovDecision"))

    def scan(text):
        pg.fill("#scanText", text)
        pg.click("#scanRead")
        pg.click("#scanApply")
        pg.wait_for_timeout(100)

    # Raw worksheet with the same inputs as sample A, written the way text recognition returns it.
    scan("1.0 ft: 15\n1.5 ft = 25\n2.0 - 3O\n2.5 ft 20\n3.0 ft: 10\nTotal seconds 1100\n"
         "P 20 S 70 X 10\nEcho 10 right\nDrift 150 ft in 3 min left\nGolf 2 to 4 lines 150 ft\n"
         "Hotel 12 kts 40 deg onshore right")
    check("scan raw worksheet = sample A MSI 4.0", T("msiBig") == "4.0", T("msiBig"))
    check("scan marked as from sheet", "FROM SHEET" in T("ovSource"))

    # Cross-check against the buoy report nearest the observation; DTG set to the newest packaged report.
    pg.evaluate("""() => { const d = new Date(picCache.hist[picCache.hist.length - 1].t), p = n => String(n).padStart(2, '0');
      $('dtg').value = p(d.getUTCDate()) + p(d.getUTCHours()) + p(d.getUTCMinutes()) + 'Z'; calculate(); }""")
    check("cross-check runs for an observed count", "Cross-check" in T("ovCheck") or "CHECK:" in T("ovCheck"), T("ovCheck")[:80])
    check("observed MSI dot on chart", pg.locator("#picChart circle").count() == 1)
    pg.fill("#windSpeed", "45")
    pg.dispatch_event("#windSpeed", "change")
    check("cross-check flags a wind gap", "CHECK:" in T("ovCheck") and "wind 45 kts" in T("ovCheck"), T("ovCheck")[:100])
    check("cross-check changes no values", pg.input_value("#windSpeed") == "45")

    scan("ALPHA 3.5 ft BRAVO 5 CHARLIE 9 sec DELTA 20% P 70% S 10% X ECHO 10 Right "
         "FOXTROT 0.5 kts Left GOLF 2 to 4 lines 150 ft HOTEL 12 kts at 40 onshore Right DECISION: NO-GO")
    fields = {i: pg.input_value("#" + i) for i in ["pCount", "sCount", "driftFeet", "windSpeed", "windAngle", "golfWidth", "totalSeconds"]}
    check("scan report fields", fields == {"pCount": "20", "sCount": "70", "driftFeet": "50", "windSpeed": "12", "windAngle": "40", "golfWidth": "150", "totalSeconds": "900"}, str(fields))
    check("scan report ALPHA 3.5 rebuilt", T("alphaRawOut") == "3.50" and T("bravoOut") == "5.0", f"{T('alphaRawOut')} / {T('bravoOut')}")
    check("scan never imports a decision", pg.input_value("#decValue") == "" and "not imported" in T("scanOut"))

    pg.click("[data-scenario=A]")
    pg.wait_for_timeout(100)
    scan(T("callOutput"))
    check("BPT call read back within 0.3 of 4.0", abs(float(T("msiBig")) - 4.0) <= 0.3, T("msiBig"))

    # Voice entry: dictated words become heights. Tapped counts are never overwritten while talking.
    pg.click("#voiceBox summary")
    pg.fill("#pasteHeights", "two, two and a half, three point five, half")
    pg.wait_for_timeout(500)
    check("voice keeps tapped counts", "already tapped" in T("pasteMsg") and T("totalWavesOut") != "4", T("pasteMsg"))
    pg.click("#applyPaste")
    pg.wait_for_timeout(100)
    hl = pg.evaluate("getHeightList().sort((a, b) => a - b).join(' ')")
    check("voice words read as heights", hl == "0.5 2 2.5 3.5", hl)
    pg.fill("#pasteHeights", "two, two and a half, three point five, half, for")
    pg.wait_for_timeout(500)
    check("voice updates live after Apply", T("totalWavesOut") == "5", T("pasteMsg"))
    pg.fill("#pasteHeights", "two spilling, three plunging, two and a half s, four surging. one")
    pg.wait_for_timeout(500)
    said_types = (T("totalWavesOut"), pg.input_value("#sCount"), pg.input_value("#pCount"), pg.input_value("#xCount"))
    check("voice records height and breaker type", said_types == ("5", "2", "1", "1"), str(said_types) + " " + T("pasteMsg"))

    # Spoken readback: every 10th wave while counting, silent on big jumps, call text read in words.
    said = pg.evaluate("""() => { const out = []; window.say = t => out.push(t); $('sayCount').checked = true;
      lastSaid = 8; sayCount(9); sayCount(10); lastSaid = 99; sayCount(100); lastSaid = 0; sayCount(100); return out; }""")
    check("count spoken every 10 waves", said == ["10 waves", "100 waves. Count complete."], str(said))

    # A report spoken into the keyboard's dictation, with numbers as words.
    scan("Alpha three and a half feet. Bravo five. Charlie nine seconds. Delta twenty percent plunging seventy percent "
         "spilling ten percent surging. Echo ten degrees right. Foxtrot point five knots left. Golf two to four lines "
         "one hundred fifty feet. Hotel twelve knots at forty degrees onshore right.")
    fields = {i: pg.input_value("#" + i) for i in ["pCount", "sCount", "xCount", "echoAngle", "driftFeet", "golfFrom", "golfTo", "golfWidth", "windSpeed", "windAngle", "totalSeconds"]}
    check("spoken report fills the worksheet", fields == {"pCount": "20", "sCount": "70", "xCount": "10", "echoAngle": "10", "driftFeet": "50", "golfFrom": "2", "golfTo": "4", "golfWidth": "150", "windSpeed": "12", "windAngle": "40", "totalSeconds": "900"} and T("alphaRawOut") == "3.50", str(fields))

    # The communicator call carries no EXERCISE, SOURCE or sample lines; the page has no classification banner.
    call = T("callOutput")
    check("call has no exercise or source lines", not any(w in call.upper() for w in ("EXERCISE", "TRAINING AID", "SOURCE:", "SAMPLE:", "MSI MATH")), call[:80])
    check("no classification banner", "UNCLASSIFIED" not in pg.inner_text("body").upper())

    # Coordinates: MGRS both ways (checked against the mgrs library), deg-min-sec and decimal.
    coords = pg.evaluate("""() => [toMgrs(36.92035, -75.9953), toMgrs(-33.8568, 151.2153),
      ...['18S UJ 23478 06483', '36 55 13 N 075 59 43 W', '36.55.13N 075.59.43W', '36.92035, -75.9953'].map(s => { const p = parseLocation(s); return p.lat.toFixed(4) + ',' + p.lng.toFixed(4) })]""")
    check("MGRS and deg-min-sec read correctly", coords == ["18S VF 11348 86499", "56H LH 34900 52288", "38.8895,-77.0353", "36.9203,-75.9953", "36.9203,-75.9953", "36.9203,-75.9953"], str(coords))

    # Custom beach near Fort Story from deg-min-sec: faces the nearest buoy automatically, saved on the device, deletable.
    pg.click("#customBox summary")
    pg.fill("#cbName", "Test lane")
    pg.fill("#cbLoc", "36 51 00 N 075 58 12 W")
    pg.click("#cbSave")
    pg.wait_for_timeout(200)
    check("custom beach saved and selected", pg.input_value("#regionId") == "custom" and "Test lane" in T("ovPlace"), T("cbMsg")[:80])
    check("custom beach faces the buoy and shows MGRS", "toward buoy 44099" in T("beachNote") and "MGRS 18S" in T("beachNote"), T("beachNote")[-90:])
    # The direction is really used: the link points at the buoy, and NOAA's ECHO angle follows it.
    facing = pg.evaluate("""() => { const b = beach(), l = LINKS[b.id];
      return [l.seaward, Math.round(bearingTo(b.lat, b.lng, l.wave.lat, l.wave.lng)), noaaWindow(l, b, null).patch.echoAngle] }""")
    check("custom beach direction feeds the angles", facing[0] == facing[1] and facing[2] is not None, str(facing))
    old = pg.evaluate("""() => { const b = beach(), list = loadCustom(); list.find(c => c.id === b.id).facing = 180; saveCustom(list);
      installCustom(); return LINKS[b.id].seaward === Math.round(bearingTo(b.lat, b.lng, LINKS[b.id].wave.lat, LINKS[b.id].wave.lng)) }""")
    check("old saved facing is ignored", old is True)
    check("no beach-faces option shown", pg.locator("#cbFacing").count() == 0)
    check("custom beach linked to nearest buoy", "44099" in T("ovEst") or "44087" in T("ovEst"), T("ovEst")[:60])
    pg.reload()
    pg.wait_for_timeout(400)
    check("custom beach kept after reload", "Test lane" in T("ovPlace"), T("ovPlace"))
    pg.click("#cbDelete")
    pg.wait_for_timeout(200)
    check("custom beach deleted", pg.input_value("#regionId") != "custom" and pg.locator("#regionId option[value=custom]").count() == 0)

    # Map: off until asked, alligator markers, and satellite / hybrid / regular styles.
    pg.click("#mapShow")
    pg.wait_for_timeout(100)
    layers = lambda: sorted({s.split("/MapServer")[0].split("/services/")[1] for s in pg.eval_on_selector_all("#map img", "i => i.map(x => x.src)")})
    check("map shows alligator markers", pg.locator("#map svg g").count() >= 1 and pg.locator("#map svg circle[r='8']").count() == 0)
    check("map starts on satellite", layers() == ["World_Imagery"], str(layers()))
    pg.click("[data-mapstyle=hybrid]")
    check("hybrid adds roads and names", layers() == ["Reference/World_Boundaries_and_Places", "Reference/World_Transportation", "World_Imagery"], str(layers()))
    pg.click("[data-mapstyle=street]")
    check("regular map style", layers() == ["World_Street_Map"] and "Esri, HERE" in T("map"), str(layers()))

    # Offline copy: the downloaded zip is valid, and the unzipped index.html runs from disk.
    import tempfile, zipfile, pathlib
    with pg.expect_download() as dl:
        pg.click("#copyDl")
    tmp = pathlib.Path(tempfile.mkdtemp())
    zpath = tmp / "copy.zip"
    dl.value.save_as(zpath)
    with zipfile.ZipFile(zpath) as z:
        names, bad = z.namelist(), z.testzip()
        z.extractall(tmp)
    check("offline copy zip is valid", bad is None and "SUROB-MSI/index.html" in names and "SUROB-MSI/conditions-data.js" in names, str(names))
    disk = pg.context.new_page()
    disk_errs = []
    disk.on("pageerror", lambda e: disk_errs.append(str(e)))
    disk.on("dialog", lambda d: d.accept())
    disk.goto((tmp / "SUROB-MSI" / "index.html").as_uri() + "?all")
    disk.wait_for_timeout(500)
    disk.click("[data-scenario=A]")
    disk.wait_for_timeout(100)
    check("unzipped copy runs from disk", "App ready" in disk.inner_text("#jsStatus") and disk.inner_text("#msiBig") == "4.0" and not disk_errs,
          disk.inner_text("#jsStatus") + " " + disk.inner_text("#msiBig") + " " + "; ".join(disk_errs))
    check("unzipped copy has NOAA data", "NOAA estimate: MSI" in disk.inner_text("#ovEst"), disk.inner_text("#ovEst")[:50])
    with disk.expect_download() as dl3:
        disk.click("#sheetFilled")
    check("unzipped copy fills the data sheet", dl3.value.path().read_bytes().rstrip().endswith(b"%%EOF"), disk.inner_text("#sheetMsg"))
    disk.close()

    # Data sheet PDF: blank copy is the packaged sheet; the filled copy carries the worksheet values in its form fields.
    def sheet_fields(path):
        try:
            import pypdf
        except ImportError:
            return None
        r = pypdf.PdfReader(str(path))
        return {k: v.get("/V") for k, v in (r.get_fields() or {}).items()}, len(r.pages)
    with pg.expect_download() as dl:
        pg.click("#sheetBlank")
    blank = dl.value.path().read_bytes()
    check("blank data sheet", blank.startswith(b"%PDF") and len(blank) > 200000 and dl.value.suggested_filename.endswith(".pdf"), dl.value.suggested_filename)
    try:
        import pypdf, io
        txt = pypdf.PdfReader(io.BytesIO(blank)).pages[0].extract_text()
        check("data sheet tables match the app", "-2.0\n-0.3\n-0.4" not in txt and "21 TO 25" in txt and "5 TO 10" in txt, "")
    except ImportError:
        pass
    pg.click("[data-scenario=A]")
    pg.fill("#dtg", "051430Z NOV 26")
    pg.wait_for_timeout(100)
    with pg.expect_download() as dl:
        pg.click("#sheetFilled")
    fpath = tmp / "sheet-a.pdf"
    dl.value.save_as(fpath)
    got = sheet_fields(fpath)
    if got is None:
        check("filled data sheet (pypdf not installed, file only)", fpath.read_bytes().startswith(blank), "")
    else:
        f, pages = got
        want = {"surob_datetime": "051430Z NOV 26", "msi_result": "4.0", "msi_alpha_ft": "2.5", "bpt_bravo": "3.0", "msi_delta_spill": "70",
                "bpt_golf_width_ft": "150", "msi_wind_onshore": "/Yes", "bpt_foxtrot_left": "/Yes", "bpt_wx_clear": "/Yes", "bpt_wx_unrestricted": "/Yes",
                "sbh_alpha": f["sbh_alpha"], "msi_wind_offshore": "/Off", "wave_001_ht": ""}
        bad = {k: (f.get(k), v) for k, v in want.items() if str(f.get(k)) != v}
        check("filled data sheet carries the worksheet", pages == 2 and not bad and fpath.read_bytes().startswith(blank), str(bad))
    # Every wave tapped on the pad: the 100-wave table is filled in order with its breaker type.
    pg.click("#clearAll")
    pg.click("[data-btype=sCount]")
    for _ in range(20):
        pg.click("[data-padh='2']")
    pg.click("[data-btype=xCount]")
    for _ in range(15):
        pg.click("[data-padh='3']")
    with pg.expect_download() as dl:
        pg.click("#sheetFilled")
    fpath = tmp / "sheet-pad.pdf"
    dl.value.save_as(fpath)
    got = sheet_fields(fpath)
    if got is not None:
        f = got[0]
        row = (f.get("wave_001_ht"), f.get("wave_001_type"), f.get("wave_035_ht"), f.get("wave_035_type"), f.get("wave_036_ht"), f.get("sbh_1_height"), f.get("sbh_1_occurrence"), f.get("sbh_2_occurrence"))
        check("pad waves fill the 100-wave table", row == ("2.0", "S", "3.0", "X", "", "3.0", "15", "18"), str(row))

    pg.set_viewport_size({"width": 390, "height": 844})
    pg.wait_for_timeout(200)
    w = pg.evaluate("document.documentElement.scrollWidth")
    check("no sideways scroll at 390px", w <= 390, f"{w}px")
    check("no page errors", not errs, "; ".join(errs))

    # Tabs, Info, units in fields and the Mic (opens the box for the keyboard's dictation).
    tc = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
    tp = tc.new_page()
    terrs = []
    tp.on("pageerror", lambda e: terrs.append(str(e)))
    tp.route("https://api.weather.gov/**", lambda r: r.abort())
    tp.goto(base + "/index.html")
    tp.wait_for_timeout(400)
    check("opens on the Overview tab", tp.is_visible("#overview") and not tp.is_visible("#countCard") and tp.get_attribute("#tabOverview", "aria-selected") == "true")
    tp.click("#tabWorksheet")
    check("Worksheet tab shows the count", tp.is_visible("#countCard") and not tp.is_visible("#overview"))
    tp.click("#tabOverview")
    tp.click("a.pill[href='#final']")
    check("link to the decision opens the Worksheet tab", tp.is_visible("#final"))
    tp.click("[data-info=infoBreaker]")
    check("Info shows the breaker reference", tp.is_visible("#infoBreaker") and "Surging (X)" in tp.inner_text("#infoBreaker"))
    tp.click("[data-info=infoHeight]")
    check("Info shows the wave height reference", tp.is_visible("#infoHeight") and "trough" in tp.inner_text("#infoHeight"))
    unit = tp.evaluate("getComputedStyle(document.getElementById('windSpeed').parentElement,'::after').content")
    check("units sit inside the fields", unit == '"kts"' and "kts" not in tp.inner_text("label[for=windSpeed]"), unit)
    tp.click("[data-mic=pasteHeights]")
    focused = tp.evaluate("document.activeElement.id")
    check("Mic opens the box for keyboard dictation", focused == "pasteHeights" and tp.evaluate("document.getElementById('voiceBox').open") and "keyboard" in tp.inner_text("[data-miclive=pasteHeights]"), focused)
    tp.keyboard.type("two spilling three plunging")
    tp.wait_for_timeout(700)
    heard = (tp.inner_text("#totalWavesOut"), tp.input_value("#sCount"), tp.input_value("#pCount"))
    check("dictated waves fill the counts", heard == ("2", "1", "1"), str(heard))
    tp.fill("#pasteHeights", "")
    tp.keyboard.type("spilling two, three plunging four. Two and a half")
    tp.wait_for_timeout(700)
    heard = (tp.inner_text("#totalWavesOut"), tp.input_value("#sCount"), tp.input_value("#pCount"), tp.input_value("#h25"))
    check("type said first also works and stays picked", heard == ("4", "2", "2", "1"), str(heard))
    tp.fill("#pasteHeights", "")
    tp.keyboard.type("two spelling, three surgery, two and a half plunge, one spill")
    tp.wait_for_timeout(700)
    heard = (tp.inner_text("#totalWavesOut"), tp.input_value("#sCount"), tp.input_value("#pCount"), tp.input_value("#xCount"))
    check("misheard breaker words still count", heard == ("4", "2", "1", "1"), str(heard))
    sheet = tp.evaluate("(()=>{const r=parseSheet('Delta twenty percent plunge seventy percent spelling ten percent surgery');return [r.f.pCount,r.f.sCount,r.f.xCount].join('/')})()")
    check("misheard words in a spoken report", sheet == "20/70/10", sheet)
    w = tp.evaluate("document.documentElement.scrollWidth")
    check("tabs: no sideways scroll at 390px", w <= 390 and not terrs, f"{w}px " + "; ".join(terrs))
    tc.close()
    rp = b.new_context(service_workers="block").new_page()
    rp.goto(base + "/index.html?all")
    rp.wait_for_timeout(300)
    rp.click("[data-mic=scanText]")
    check("report Mic opens the report box", rp.evaluate("document.activeElement.id") == "scanText" and "Read report" in rp.inner_text("[data-miclive=scanText]"))
    rp.context.close()

    # Offline: one visit with a connection installs the service worker, then the app opens with no network.
    ctx = b.new_context()
    off = ctx.new_page()
    off.goto(base + "/index.html?all")
    ready = False
    for _ in range(30):
        if "works offline" in off.inner_text("#jsStatus"):
            ready = True
            break
        off.wait_for_timeout(500)
    check("offline copy installed", ready, off.inner_text("#jsStatus"))
    ctx.set_offline(True)
    off.reload()
    off.wait_for_timeout(800)
    check("opens with no network", "App ready" in off.inner_text("#jsStatus"), off.inner_text("#jsStatus"))
    off.click("[data-scenario=A]")
    off.wait_for_timeout(100)
    check("offline sample A MSI 4.0", off.inner_text("#msiBig") == "4.0", off.inner_text("#msiBig"))
    try:
        with off.expect_download(timeout=10000) as dl2:
            off.click("#copyDl")
        got = dl2.value.path().stat().st_size > 100000
    except Exception:
        got = False
    check("offline copy downloads with no network", got, off.inner_text("#copyMsg"))
    try:
        with off.expect_download(timeout=10000) as dl4:
            off.click("#sheetFilled")
        got = dl4.value.path().read_bytes().startswith(b"%PDF")
    except Exception:
        got = False
    check("data sheet fills with no network", got, off.inner_text("#sheetMsg"))
    b.close()

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
