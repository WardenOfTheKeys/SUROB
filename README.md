# SUROB MSI Calculator — Version 2

Field-test calculator for the SUROB worksheet (A–H), with the final Modified Surf Index, an **advisory** craft limit check, and a **human decision record**.

> **UNCLASSIFIED · TRAINING AID · SYNTHETIC DATA ONLY.**
> Do not enter real names, locations, unit data or real observations.
> The calculator never makes the GO / NO-GO call. A person does.

## Open it

https://wardenofthekeys.github.io/SUROB/

Works in any current browser: Chrome, Edge, Firefox, Safari, Samsung Internet. Phone, tablet, or computer. To try it, tap **Load synthetic scenario A** or **B**.

## Put it on your home screen (optional)

| Device / browser | How |
|---|---|
| iPhone / iPad (Safari) | Share → Add to Home Screen |
| iPhone / iPad (Chrome) | Share → Add to Home Screen |
| Android (Chrome) | ⋮ menu → Add to Home screen / Install app |
| Android (Samsung Internet) | ☰ menu → Add page to → Home screen |
| Windows / Mac (Chrome or Edge) | Install icon in the address bar, or menu → Install SUROB MSI |
| Firefox (desktop) | Bookmark it |

Use the web link above. Opening the downloaded .html file in a phone's file preview can block the calculator.

## What it does

- Wave count with tap counters (0–10 ft), giving ALPHA (highest 33 average) and BRAVO (highest wave).
- Stopwatch or clock times for CHARLIE, and breaker-type tallies for DELTA.
- ECHO, FOXTROT, GOLF and HOTEL inputs, with the MSI worksheet breakdown and a step-by-step verification block.
- Advisory limit check for listed craft ("within / at / exceeds limit").
- Required human decision record: it starts as PENDING, and any input change afterwards flags it for re-confirmation.
- BPT communicator call text, and print / save PDF.

## Human control

- **Approval point:** only a named decision authority records GO, GO with restrictions or NO-GO.
- **Prohibited actions:** the app doesn't decide, send data, or contact any other site. A Content-Security-Policy enforces this.
- **Monitoring:** input warnings, the verification block, and the re-confirm flag.
- **Escalation:** red warnings, at-limit or exceeded craft, or any mismatch with the paper worksheet go to the BMU OIC.
- **Shutdown:** close the tab. **Clear form** erases the data saved on the device.

## Tools used

- Claude Code (Anthropic Claude Opus 5.5) to write and review code.
- No external libraries, APIs, datasets or cloud services at runtime.

## Working overview function (in progress)

The `working-overview/` folder is a separate, in-progress build of the calculator with a map overview and a week of packaged NOAA buoy, wind and visibility data (`conditions-week.json`). It is unpacked byte-for-byte from `surob-msi-calculator(2).zip` (uploaded by H4CK3R-M4N). Nothing in it has been edited, and the original zip is still in the repo.

It does **not** replace Version 2 above. The web link still opens Version 2.

**Run it on your computer** (needs Python 3):

| System | How |
|---|---|
| Windows | Open `working-overview`, double-click `open-calculator.bat` |
| Mac / Linux | `cd working-overview && ./open-calculator.sh` |

The script opens `http://127.0.0.1:43124`. Press Ctrl+C in the window to stop it.

Notes:
- It does not open from the GitHub Pages link yet. The build points to its files from the site root (`/_next/...`), so it only runs through the script above.
- The map needs internet for satellite photos. The MSI math works offline.
- Chrome may warn when you download the zip because it holds a `.bat` file. The scripts only start a local Python web server.
- Training aid. Beach pins are approximate.

## Status

Training aid, not validated for operational use. The MSI correction tables still need checking against the official source publication. Validate against current command guidance before any use beyond training.
