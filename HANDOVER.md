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
- Unclassified training aid. No names, unit data or operational observations in samples or tests.

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
3. **Refresh NOAA data:** `conditions-data.js` is a 4 Nov snapshot, and the page warns after 24 h. Refresh by exporting `conditions-week.json` from his app, then:
   `python3 -c "import json;d=json.load(open('conditions-week.json'));open('v3/conditions-data.js','w').write('window.SUROB_CONDITIONS='+json.dumps(d,separators=(',',':'))+';\n')"`
   Option: a scheduled GitHub Action that pulls NDBC / CO-OPS / NWS and commits the file daily. Convert NWS km/h there.
4. **Ask him to commit his Next.js source.** Only the compiled build is in the repo. His build also needs `basePath: '/SUROB/working-overview'` to run from Pages.
5. **Decide which version is primary** for the team (V2 root vs V3) before Fleethacker, and update the root README link.
6. MSI correction tables still need checking against the official source publication (carried over from V2's Status note).

## Session history (4 Nov evening)

- Chrome flagged his zip as "Virus detected". This was a false positive: the zip holds `open-calculator.bat/.sh`, which only run `python -m http.server 43124`.
- Unpacked the zip unchanged → PR #1.
- Reviewed his build. Found: GO with no data, conflict with V2's human-control rule, outside requests with no CSP, the wind unit bug, and only compiled code in the repo.
- Built Version 3 → PR #2, tested headless, added this handover and the smoke test.
