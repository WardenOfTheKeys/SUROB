# SUROB MSI Calculator: handover

Last updated: 4 Nov 2026, 2050 EST. Written for picking this up in Claude Code.

## Start here (paste into Claude Code)

> Read HANDOVER.md in this repo. I'm continuing Version 3 of the SUROB MSI calculator on the `v3-merged` branch (PR #2). Don't edit the root `index.html` (Version 2) or anything in `working-overview/` or `surob-msi-calculator(2).zip`; those belong to other people or are the live version. Run the smoke test before and after any change.

Setup:

```
git clone https://github.com/WardenOfTheKeys/SUROB.git
cd SUROB
git checkout v3-merged
```

## Ground rules

- **Do not edit** root `index.html`. It is Version 2, the live page at https://wardenofthekeys.github.io/SUROB/.
- **Do not edit** `working-overview/` or `surob-msi-calculator(2).zip`. That is H4CK3R-M4N's build, and he worked on it all day 4 Nov. Review notes go in PR comments, not code changes.
- All Version 3 work happens in `v3/` on branch `v3-merged`.
- The calculator never makes the GO / NO-GO call. A person records it in section 8. Keep it that way.
- No names, unit data or operational observations in samples or tests.

## Repo state

| Branch / PR | What | Status |
|---|---|---|
| `main` | Version 2 (root `index.html`), README, his zip | Live on Pages |
| `working-overview` / [PR #1](https://github.com/WardenOfTheKeys/SUROB/pull/1) | His zip unpacked byte-for-byte into `working-overview/`, plus README section | Open, not merged |
| `v3-merged` / [PR #2](https://github.com/WardenOfTheKeys/SUROB/pull/2) | Version 3 in `v3/`, README section, this handover, smoke test | Open, mergeable, not merged |

`https://wardenofthekeys.github.io/SUROB/v3/` returns 404 until PR #2 is merged. Pages serves only `main`. The two PRs don't touch the same files and can merge in either order.

## Layout of v3/

```
v3/
  index.html            whole app: HTML, CSS, JS in one file (~990 lines)
  conditions-data.js    packaged NOAA week: window.SUROB_CONDITIONS = {...}
  manifest.webmanifest  install manifest (copied from root)
  icon.svg, icon-192.png, icon-512.png
tools/
  v3-smoke-test.py      Playwright smoke test (13 checks)
```

It runs on Pages, from a local server, or by opening `index.html` directly (file://). There's no build step and no libraries.

## Where things are in v3/index.html

| Lines (approx.) | What |
|---|---|
| 10 | Content-Security-Policy: `self` + `server.arcgisonline.com` images only |
| 88–105 | New CSS: overview, map, sparkline |
| 124–147 | Overview card (MSI, craft chips, decision), Beach picker, map container |
| 149–160 | NOAA conditions card |
| 348–358 | MSI tables and `craftLimits`, unchanged from V2 |
| 360 | `SCENARIOS` A, B, C (C is his MSI 3.2 sample) |
| 402–456 | `REGIONS` (beaches), `ST` (stations), `LINKS` (beach to buoy/wind/visibility, with `seaward` bearing) |
| 467 | `windKts()`: **NWS airfield km/h → kts; NDBC/CO-OPS m/s → kts** |
| 469 | `binsFromHs()`: builds 100 counts so the highest 33 average the significant height (his method) |
| 479 | `noaaWindow()`: 2-hour window → worksheet patch + source note |
| 503 | `noaaFill()`: applies the patch and clears sample-only fields |
| 517 | `renderNoaa()`: status, data age warning, 7-day chart, window slider |
| 537–578 | Beach picker and the no-library satellite map (Esri tiles, pin, shoreline line, zoom, drag) |
| 629 | `renderCraft()`: NO DATA when no count; returns chips for the overview |
| 668 | `renderDecision()`: fingerprint of inputs; any change flags re-confirm (ignores `noaaWin` slider) |
| 685 | `calculate()`: the MSI math (from V2) + overview, source line, BPT call, audit |
| 858+ | localStorage under key `surob-msi-v3`; restore re-fills the beach list before setting the beach |

## What Version 3 changed vs. the two parents

From his build: overview, beach picker, map check, NOAA week fill + chart, sample C.
From Version 2: the full A–H worksheet, verification block, BPT call, print, advisory check, human decision record, CSP.

Fixes and decisions (all in PR #2's description):

1. **NO DATA until a wave count exists.** His build showed GO for every craft at MSI 0.0.
2. **NWS wind units.** Every KNFG/KNZY/KNCA/KNGU/KNTU/PHNG `windMs` value in `conditions-week.json` is a multiple of 3.6, so it is km/h. His code multiplied by 1.943844 (m/s → kts), which overstates airfield wind about 3.6×. CO-OPS values (1612480, 8638999) are m/s. The field name `windMs` is misleading for NWS rows. **His fetch code (`/api/conditions`, not in this repo) is the real place to fix it.**
3. **NOAA ESTIMATE label** in the overview, BPT call (`SOURCE:` line) and audit. The 100-wave count from a buoy is not a surf-zone count.
4. **Sample values are cleared** (breaker type, drift, GOLF, secondary) when filling from NOAA after loading a sample. Hand entries are kept.
5. **Map is off until "Show satellite map".** No outside request happens before that.
6. **Default beach:** Fort Story Atlantic (Cape Henry region first).
7. **Banner:** "Beach pins and NOAA reports are public data" replaces V2's "synthetic data only." Revisit if the hackathon rules require synthetic data only.

## Testing

```
pip install playwright && playwright install chromium
python3 -m http.server 8765 --directory v3 &
python3 tools/v3-smoke-test.py http://127.0.0.1:8765
```

Expected result: 13 PASS, 0 failures. Known-good values: sample A = 4.0, B = 16.8, C = 3.2 (C matches his build).

**Not yet verified:** the satellite imagery. The build sandbox had no internet, so tiles never loaded there. Open the map on a phone and confirm each pin and orange shoreline line sits on the sand.

## Open items / next steps

1. **Merge PR #2** so `/v3/` goes live. Then check the map on a phone, then share the link.
2. **Review with H4CK3R-M4N:** the km/h finding, and his binning method (`binsFromHs`) against the paper worksheet.
3. **Refresh NOAA data:** `python3 tools/refresh-conditions.py` rebuilds `v3/conditions-data.js` (7 days of NDBC / NWS / CO-OPS history plus a 5-day NWS gridpoint forecast for every beach). Standard library only. Its rows match his export exactly; NWS `windMs` stays km/h like his export. `.github/workflows/refresh-conditions.yml` runs it every 3 hours once it is on `main`, and each run commits to `main` (live site). Run it by hand from the Actions tab with "Run workflow".
4. **Ask him to commit his Next.js source.** Only the compiled build is in the repo. His build also needs `basePath: '/SUROB/working-overview'` to run from Pages.
5. **Decide which version is primary** for the team (V2 root vs V3) before Fleethacker, and update the root README link.
6. MSI correction tables still need checking against the official source publication (carried over from V2's Status note).

## Branch v3-estimate-and-scan (4 Nov, late)

- **Overview, now:** NOAA estimated MSI from the newest buoy window (A + C + E + H; D, F, secondary = 0). Never written to the worksheet unless "Use in worksheet" is tapped.
- **Overview, picture:** estimated MSI for the last 7 days (buoy) and next 5 days (NWS forecast, 2 km seaward of the pin), same tables as the worksheet. Craft limit reference lines, observed worksheet MSI as a dot. When online the page fetches the newest forecast for that grid square (CSP `connect-src https://api.weather.gov`); offline it uses the packaged copy.
- **Cross-check:** for a hand or scanned count, compares with the NOAA estimate nearest the DTG (within 6 h). CHECK note at MSI gap ≥ 1.5, ALPHA vs buoy height ≥ 50 %, or wind ≥ 10 kts. Advisory, changes nothing.
- **Read a handwritten sheet:** parses text from phone text recognition (finished report or raw worksheet). Never imports GO / NO-GO or names.
- **NWS swell direction:** some offices (AKQ, HFO) fill it with a single 0 lasting days. Values held over 24 h are treated as missing and the latest buoy direction is used.
- Smoke test: 27 checks. It blocks api.weather.gov so the result does not depend on the network.

## Offline, custom beaches, voice (5 Nov, early)

- **Offline:** `v3/sw.js` caches the app's own files (page, packaged data, manifest, icons). Network first with a 4 s wait, then the saved copy. Esri and api.weather.gov are never cached. Bump `CACHE` in `sw.js` when the file list changes. The status shows "works offline" once it is installed.
- **Custom beaches:** stored under `surob-msi-v3-beaches` in localStorage. Linked to the nearest packaged buoy and met station within 150 km. Its NWS grid is looked up once (2 km seaward) and remembered. Not read by `tools/refresh-conditions.py`, so no packaged forecast.
- **Voice:** no speech-recognition API (Chrome's sends audio to Google and fails offline). The Sailor uses the keyboard's own dictation into the heights box; `spokenToDigits()` turns words into heights and the box updates the counts live. It never overwrites tapped counts without Apply. Spoken readback uses `speechSynthesis` (device voices).
- Smoke test: 39 checks, including opening with no network.

## MGRS, spoken reports, clean call (5 Nov)

- **Custom beach location:** one box takes MGRS, deg-min-sec or decimal (`parseLocation()`). MGRS both ways (`toMgrs()` / `fromMgrs()`, WGS 84, Norway and Svalbard zones) matches the `mgrs` Python library at 10 points worldwide. Every beach shows its MGRS.
- **Beach direction:** no longer asked. The beach always faces the nearest packaged buoy (`bearingTo()`); there is no manual option, and a facing saved by an earlier version is ignored.
- **Speak a report:** `wordsToNumbers()` turns dictated number words into digits ("eleven hundred", "three and a half", "point five") before `parseSheet()`. "Read call aloud" was removed; the spoken count every 10 waves stays.
- **Call text:** only SITE, DTG, OBSERVER, ALPHA–HOTEL, MSI and DECISION. No EXERCISE, SOURCE, SAMPLE or MSI math lines (those stay in the verification block). No classification or training-aid banner; Fleethacker Rule 4 requires staying unclassified, not marking it.
- Smoke test: 43 checks.

## Counting pad (5 Nov)

- Section 1 is one pad: breaker type buttons (sticky, tap again to clear) and height buttons 0.5–5 ft, plus 5.5–10 behind "Bigger waves". `padWave()` adds to the height row and the picked breaker count; `tapHistory` entries can hold both ids, so Undo takes back both. The per-height and P/S/X steppers moved into "Check or edit the totals".
- Voice box: a breaker word after a height belongs to that wave ("two spilling", "three p").
- Below 33 waves the craft chips show NO DATA, the overview MSI shows "—" and there is no cross-check, so nothing reads as passing mid-count.
- Section 2 is timing only (C). Smoke test: 46 checks.
- Decision authority (V2 and V3): only BPTC (Beach Party Team Commander) or SRM (Senior Ramp Marshal).
- Map: `MAP_STYLES` = satellite (World_Imagery), hybrid (imagery + Reference/World_Transportation + Reference/World_Boundaries_and_Places), regular (World_Street_Map), all from server.arcgisonline.com, so the security policy is unchanged. The choice is kept in the hidden `mapStyle` input. Beach marker is the `gator()` SVG; the orange shoreline line is unchanged. Smoke test: 51 checks.

## Session history (4 Nov evening)

- Chrome flagged his zip as "Virus detected". This was a false positive: the zip holds `open-calculator.bat/.sh`, which only run `python -m http.server 43124`.
- Unpacked the zip unchanged → PR #1.
- Reviewed his build. Found: GO with no data, conflict with V2's human-control rule, outside requests with no CSP, the wind unit bug, and only compiled code in the repo.
- Built Version 3 → PR #2, tested headless, added this handover and the smoke test.

## Offline copy and README (5 Nov)

- **Download offline copy (.zip)** (V3 section 9): builds a stored zip in the browser from the app's own files (`makeZip()`, no library), plus OPEN-ME.txt. Works offline from the saved copy. The unzipped `index.html` runs from disk; the button is hidden there. The security policy's `connect-src` now includes `'self'` so the page can read its own files.
- README: no developer section; the overview prototype is listed as the team's first build. Smoke test: 58 checks, including the zip, the unzipped copy and an offline download.


## Data sheet PDF (5 Nov)

- Section 5 has **Fill data sheet (PDF)** and **Blank data sheet (PDF)**. The team's 2-page fillable sheet (292 fields) is packaged as base64 in `v3/data-sheet.js`, loaded on first tap, cached by `sw.js` (`surob-v3-2`) and included in the offline zip, so it works offline and from disk.
- `fillPdf()` writes an incremental update (the original bytes are kept): each filled field gets `/V` and its own appearance stream, ticked boxes get `/AS /Yes`. Checked with pypdf (field values) and PDFium (Chrome's engine) rendering.
- ALPHA, MSI and the highest-33 rows stay blank below 33 waves. The 100-wave table is filled only when every wave was tapped on the pad (order and breaker type known). Tide table is left blank. Highest-33 rows are filled only when there are 4 or fewer heights.
- **Tables:** the sheet as received printed correction tables that differed from the app's in 112 cells (surging table shifted one column, spilling 70 % row shifted, spilling 10 % at 3.5 ft printed -2.0, period rows 16/15/12/8, wind rows 26-30, 22-25, 16-20, 11-15, and row labels 22-25 / 6-10). The team chose the app's tables, so the packaged sheet's page 1 was rewritten to match them (incremental update of the page content; fields unchanged). The app's tables still need checking against the official publication.
- Smoke test: 64 checks (pypdf optional for the field and table checks).

## Tabs, Mic, Info, units (5 Nov, afternoon)

- **Tabs:** Overview (overview + NOAA cards) and Worksheet (everything else). Last tab is remembered (`surob-msi-v3-tab`). A link to a section on the other tab switches first. Print shows every section. `?all` shows every section with no tabs; the smoke test uses it.
- **Mic** (pad and report box): opens and focuses the box so the phone keyboard's own dictation does the listening (works on every browser, offline when the language is downloaded). A first version used the browser's speech recognition; it did not collect on the team's phones, so it was removed.
- **Info:** breaker type and wave height panels on the pad, with drawings made for this app and text summarised from NTTP 3-59.3M / MCRP 2-10.3 Appendix D (Apr 2024). His reference images and PDF were not copied (unknown image source; the PDF's file information has a personal name).
- **Units** moved into the fields (`data-unit`, wrapped by `initUnits()`).
- Smoke test: 74 checks, including a stand-in speech engine.
