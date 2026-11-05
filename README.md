# SUROB MSI Calculator

Phone and laptop calculator for the SUROB worksheet (A–H). It gives the Modified Surf Index, an advisory craft limit check and a record of the decision a person makes.

## Get it

| | |
|---|---|
| **Open it** | https://wardenofthekeys.github.io/SUROB/v3/ in any current browser |
| **Phone or tablet** | Open the link once while connected, then Share → **Add to Home Screen** (iPhone) or ⋮ → **Install app** (Android). It opens with no signal from then on. |
| **Laptop, ship's computer or USB stick** | On the page, tap **Download offline copy (.zip)**. Unzip it and open `index.html`. No install, no account, no internet. Pass the zip around like any file. |

The calculator never makes the GO / NO-GO call. The BPTC or SRM does. Do not enter names, unit data or operational observations.

## What it does

| | |
|---|---|
| **Count** | One pad for each wave: pick how it broke (spilling, plunging, surging; it stays picked), then tap its height. One tap records both. Or tap **Mic** and say them into the keyboard's dictation ("two spilling, three plunging"); the counts fill in as you talk. **Info** shows how to judge breaker type and height. Optional spoken count every 10 waves. |
| **Speak or scan a report** | Say the whole report ("Alpha three and a half, Bravo five, …"), or scan a handwritten sheet with the phone's text recognition. You check every value before it goes in. |
| **Worksheet** | ALPHA to HOTEL, step-by-step verification, the BPT communicator call ready to copy, print or PDF. |
| **Data sheet (PDF)** | The 2-page fillable SUROB / MSI data sheet, blank or filled from the worksheet: MSI calculation, BPT calls, 100-wave table (in tap order, with breaker type), breaker period and highest-33 computation. Every field stays editable. Works offline. |
| **Overview** | Its own tab: MSI, a check result per craft, the decision status, beach picker and a map check (satellite, hybrid or regular) with the beach marked by an alligator. |
| **NOAA picture** | Estimated MSI for the last 7 days (buoys) and the next 5 days (NWS forecast) at the selected beach. |
| **Cross-check** | Flags an observed count that is far off NOAA for the same time (MSI 1.5, ALPHA 50 %, wind 10 kts). It never changes a value. |
| **Any beach** | Add a beach by MGRS or latitude / longitude (deg-min-sec or decimal), or **Use my location**. It links to the nearest NOAA buoy within 150 km. Saved on the device only. |
| **No signal** | The app, the packaged NOAA week and the forecast open offline, from the home screen or from the downloaded copy. The newest version and data load by themselves when connected. |

NOAA estimates count breaker type, littoral current and secondary wave as 0, and buoys are offshore. They show the trend and catch a count that looks wrong. They do not replace the surf observation.

## Human control

- **Approval point:** only the BPTC (Beach Party Team Commander) or SRM (Senior Ramp Marshal) records GO, GO with restrictions or NO-GO. Any input change after that flags it for re-confirmation.
- **Prohibited actions:** the app does not decide or send what you type. Its security policy allows only its own files, Esri map pictures after **Show map**, and the NWS forecast.
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

All data is public. No AI runs inside the app. The NOAA data is packaged with the app so it works offline, and refreshed every 3 hours.

## Versions

| | |
|---|---|
| [Version 3](https://wardenofthekeys.github.io/SUROB/v3/) | Current |
| [Version 2](https://wardenofthekeys.github.io/SUROB/) | Earlier worksheet-only calculator |
| Overview prototype (`working-overview/`) | The team's first overview build: beach picker, map, NOAA week, 7-day chart and sample C. Version 3 grew out of it. |

## Status

The MSI correction tables still need checking against the official source publication. Check results against current command guidance.
