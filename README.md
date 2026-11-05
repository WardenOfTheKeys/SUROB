# SUROB MSI Calculator

Field calculator for the SUROB worksheet (A–H). It gives the Modified Surf Index, an **advisory** craft limit check and a **human decision record**.

> **UNCLASSIFIED · TRAINING AID.** Not validated for operational use.
> Do not enter names, unit data or operational observations.
> The calculator never makes the GO / NO-GO call. A person does.

## Open it

| Version | Link | What it is |
|---|---|---|
| **Version 3** (current) | https://wardenofthekeys.github.io/SUROB/v3/ | Version 2 plus the working overview features, NOAA history and forecast, and the handwritten sheet reader |
| Version 2 | https://wardenofthekeys.github.io/SUROB/ | Worksheet-only calculator with synthetic samples |
| Working overview (H4CK3R-M4N) | see [below](#working-overview-by-h4ck3r-m4n) | The original overview build, kept as uploaded |

Works in any current browser on a phone, tablet or computer. To add it to a home screen: Share → **Add to Home Screen** (iPhone), or ⋮ → **Install app** (Android, Chrome, Edge).

**Works with no connection.** Open Version 3 once while connected. The status at the top then reads **works offline**, and the app, the packaged NOAA week and the forecast open with no signal, afloat or on the beach. When the connection comes back, it picks up the newest version and data by itself.

## Version 3 features

- **Worksheet A–H:** tap counters for the 100-wave count, stopwatch for CHARLIE, breaker tallies, ECHO / FOXTROT / GOLF / HOTEL, a step-by-step verification block, BPT call text, print / PDF.
- **Overview:** MSI, a chip per craft, the decision status, a beach picker and an optional satellite map check.
- **NOAA estimate:** estimated MSI from the newest two hours of buoy and wind reports for the selected beach.
- **Last 7 days and next 5 days:** estimated MSI from NOAA buoy reports and the NWS forecast, with craft limit reference lines and the observed MSI as a dot.
- **Cross-check:** an observed or scanned count is compared with NOAA for the same time. A **CHECK** note appears for an MSI gap of 1.5 or more, ALPHA 50 % off the buoy wave height, or wind 10 kts off. It never changes a value.
- **Read a handwritten sheet:** paste text from the phone's text recognition (iPhone Scan Text / Live Text, Google Lens). Reads a finished ALPHA–HOTEL report or a raw worksheet. It never imports a GO / NO-GO entry or names.
- **Hands-free count:** say each height into the phone keyboard's dictation ("two, two and a half, three") and the counts update as you talk. The app can say the count every 10 waves and read the BPT call aloud, using the phone's own voices.
- **Custom beaches:** add any beach by latitude / longitude (or **Use my location**) and the direction it faces. It links to the nearest packaged NOAA buoy and wind station within 150 km, and gets the live NWS forecast when online. Saved on the device only.

Estimates from NOAA count breaker type, littoral current and secondary wave as 0, and buoys are offshore. They show the trend and help catch a count that looks off. They are not a surf-zone observation.

## Human control

- **Approval point:** only a person records GO, GO with restrictions or NO-GO (section 8). Any input change after that flags it for re-confirmation.
- **Prohibited actions:** the app does not decide or send what you type. A Content-Security-Policy allows only its own files, Esri map pictures after **Show satellite map**, and the NWS forecast service.
- **Monitoring:** input warnings, the verification block, the NOAA cross-check and the re-confirm flag.
- **Escalation:** red warnings, a CHECK note, at-limit or exceeded craft, or any mismatch with the paper worksheet go to the BMU OIC.
- **Shutdown:** close the tab. **Clear form** erases what is saved on the device.

## Working overview by H4CK3R-M4N

`working-overview/` is H4CK3R-M4N's build, unpacked byte-for-byte from his upload `surob-msi-calculator(2).zip`, which is also kept in the repo. Nothing in either has been edited. His overview, beach picker, satellite map check, NOAA week, 7-day chart and sample C are the basis of the Version 3 overview.

Run it on a computer with Python 3: open `working-overview` and double-click `open-calculator.bat` (Windows), or run `./open-calculator.sh` (Mac / Linux). It opens `http://127.0.0.1:43124`. It does not run from the Pages link yet, because the build loads its files from the site root.

## Data and tools

| Source | Used for |
|---|---|
| NOAA NDBC buoys | Wave height, period and direction (history) |
| NWS station observations, NOAA CO-OPS | Wind and visibility (history) |
| NWS gridpoint forecast (api.weather.gov) | Wave and wind forecast |
| Esri World Imagery | Satellite map, only when opened |
| Claude Code (Anthropic Claude Opus 5.5) | Writing and reviewing code |

All data is public. `v3/conditions-data.js` holds the packaged copy so the app works offline. `tools/refresh-conditions.py` rebuilds it, and `.github/workflows/refresh-conditions.yml` runs that every 3 hours. When online, the page also fetches the newest forecast itself.

## Repo layout

| Path | What |
|---|---|
| `v3/` | Version 3 (single `index.html`, `sw.js` offline copy, packaged data, icons) |
| `index.html`, `manifest.webmanifest`, `icon*` | Version 2 |
| `working-overview/`, `surob-msi-calculator(2).zip` | H4CK3R-M4N's build, unchanged |
| `tools/` | Smoke test and data refresher |
| `HANDOVER.md` | Notes for whoever picks this up next |

Test: `python3 -m http.server 8765 --directory v3`, then `python3 tools/v3-smoke-test.py http://127.0.0.1:8765` (needs `pip install playwright`). Expect 0 failures.

## Status

Training aid. The MSI correction tables still need checking against the official source publication. Validate against current command guidance before any use beyond training.
