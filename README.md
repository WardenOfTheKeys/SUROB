# SUROB MSI Calculator

Phone and laptop calculator for the SUROB worksheet (A–H). It gives the Modified Surf Index, an advisory craft limit check and a record of the decision a person makes.

**Open it:** https://wardenofthekeys.github.io/SUROB/v3/

Works in any current browser. Open it once while connected and it then works with no signal. To install it: Share → **Add to Home Screen** (iPhone), or ⋮ → **Install app** (Android, Chrome, Edge).

The calculator never makes the GO / NO-GO call. A person does. Do not enter names, unit data or operational observations.

## What it does

| | |
|---|---|
| **Count** | One pad for each wave: pick how it broke (spilling, plunging, surging; it stays picked), then tap its height. One tap records both. Or say them into the phone's dictation ("two spilling, three plunging") and the counts fill in as you talk. Optional spoken count every 10 waves. |
| **Speak or scan a report** | Say the whole report ("Alpha three and a half, Bravo five, …"), or scan a handwritten sheet with the phone's text recognition. You check every value before it goes in. |
| **Worksheet** | ALPHA to HOTEL, step-by-step verification, the BPT communicator call ready to copy, print or PDF. |
| **Overview** | MSI, a check result per craft, the decision status, beach picker and a map check (satellite, hybrid or regular) with the beach marked by an alligator. |
| **NOAA picture** | Estimated MSI for the last 7 days (buoys) and the next 5 days (NWS forecast) at the selected beach. |
| **Cross-check** | Flags an observed count that is far off NOAA for the same time (MSI 1.5, ALPHA 50 %, wind 10 kts). It never changes a value. |
| **Any beach** | Add a beach by MGRS or latitude / longitude (deg-min-sec or decimal), or **Use my location**. It links to the nearest NOAA buoy within 150 km. Saved on the device only. |
| **No signal** | The app, the packaged NOAA week and the forecast open offline. The newest version and data load by themselves when connected. |

NOAA estimates count breaker type, littoral current and secondary wave as 0, and buoys are offshore. They show the trend and catch a count that looks wrong. They do not replace the surf observation.

## Human control

- **Approval point:** only the BPTC (Beach Party Team Commander) or SRM (Senior Ramp Marshal) records GO, GO with restrictions or NO-GO. Any input change after that flags it for re-confirmation.
- **Prohibited actions:** the app does not decide or send what you type. Its security policy allows only its own files, Esri map pictures after **Show satellite map**, and the NWS forecast.
- **Monitoring:** input warnings, the verification block, the NOAA cross-check and the re-confirm flag.
- **Escalation:** red warnings, a CHECK note, at-limit or exceeded craft, or any mismatch with the paper worksheet go to the BPTC or SRM.
- **Shutdown:** close the tab. **Clear form** erases what is saved on the device.

## Data and tools

| Source | Used for |
|---|---|
| NOAA NDBC buoys | Wave height, period and direction (7-day history) |
| NWS station observations, NOAA CO-OPS | Wind and visibility (7-day history) |
| NWS gridpoint forecast (api.weather.gov) | 5-day wave and wind forecast |
| Esri World Imagery | Satellite map, only when opened |
| The phone's own dictation and text recognition (Apple, Google) | Speaking or scanning a report. The app receives only the text. |
| Claude Code (Anthropic Claude Opus 5.5) | Writing and reviewing the code |

All data is public. No AI runs inside the app. `v3/conditions-data.js` is the packaged copy for offline use. `tools/refresh-conditions.py` rebuilds it, and a GitHub Action runs that every 3 hours.

## Versions

| | |
|---|---|
| [Version 3](https://wardenofthekeys.github.io/SUROB/v3/) (`v3/`) | Current |
| [Version 2](https://wardenofthekeys.github.io/SUROB/) (root `index.html`) | Earlier worksheet-only calculator |
| Working overview by H4CK3R-M4N (`working-overview/`, `surob-msi-calculator(2).zip`) | His build, kept exactly as uploaded. His overview, beach picker, map, NOAA week, 7-day chart and sample C are the basis of the Version 3 overview. Run it with Python 3: `open-calculator.bat` (Windows) or `./open-calculator.sh` (Mac / Linux), then open `http://127.0.0.1:43124`. |

## For developers

`tools/v3-smoke-test.py` checks the app end to end (needs `pip install playwright`): `python3 -m http.server 8765 --directory v3`, then `python3 tools/v3-smoke-test.py http://127.0.0.1:8765`. `HANDOVER.md` has the notes for whoever picks this up next.

## Status

The MSI correction tables still need checking against the official source publication. Check results against current command guidance.
