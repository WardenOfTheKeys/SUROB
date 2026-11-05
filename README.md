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

## Version 3 (merged build, for review)

https://wardenofthekeys.github.io/SUROB/v3/ (works once this branch is merged)

Version 3 is Version 2 plus the features from the team's working overview build. It lives in `v3/`. Version 2 above and the `working-overview` build are unchanged.

**Added from the working overview build**
- Overview at the top: MSI, a chip per craft, and the human decision status.
- Beach picker: Cape Henry and Little Creek, Onslow Beach, Camp Pendleton, Silver Strand and Coronado, Windward Oahu. Cape Henry is the default.
- Satellite map check with the beach pin and shoreline line.
- NOAA conditions: a packaged week of buoy, wind and visibility reports. Fill the worksheet from the newest two hours, or pick a window on the 7-day chart.
- Sample C (MSI 3.2) from the working overview build.

**Kept from Version 2**
- Full A–H worksheet, verification block, BPT call, print / PDF.
- Advisory limit check. A person records GO / NO-GO, and any input change flags the decision for re-confirmation.

**Changed**
- Craft show **NO DATA** until a wave count exists. Nothing reads as passing before data is entered.
- NWS airfield wind is converted from km/h to knots. The working overview build read it as m/s, which made airfield wind about 3.6 times too high.
- A NOAA fill is marked **NOAA ESTIMATE** in the overview, the call and the verification block. The 100-wave count it builds is an estimate from significant height, not a surf-zone count.
- A NOAA fill clears sample values for breaker type, current, surf zone and secondary wave, so sample numbers don't mix with real reports.
- The map loads Esri pictures only after you tap **Show satellite map**. The Content-Security-Policy allows nothing else outside the app's own files. No outside libraries.
- The banner no longer says synthetic data only, because the beaches and NOAA reports are public data. It still says not to enter names, unit data or operational observations.

**Limits**
- The NOAA week is a snapshot (`v3/conditions-data.js`, saved Nov 4, 2026). The page shows its age and warns when it is over a day old. To refresh it, export a new `conditions-week.json` from the working overview app, then from the repo folder run:
  `python3 -c "import json;d=json.load(open('conditions-week.json'));open('v3/conditions-data.js','w').write('window.SUROB_CONDITIONS='+json.dumps(d,separators=(',',':'))+';\n')"`
- Buoys are offshore. Surf on the beach can differ.

## Tools used

- Claude Code (Anthropic Claude Opus 5.5) to write and review code.
- No external libraries, APIs, datasets or cloud services at runtime.

## Status

Training aid, not validated for operational use. The MSI correction tables still need checking against the official source publication. Validate against current command guidance before any use beyond training.
