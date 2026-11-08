# SUROB MSI Calculator

**Open the app:** https://wardenofthekeys.github.io/SUROB/v3/

A SUROB is a surf observation. Before boats and landing craft come to a beach, a Sailor watches 100 waves and writes down how big they are and how they break. Those numbers make the **MSI** (Modified Surf Index). The MSI tells the team which craft can land safely.

This app does that worksheet on a phone or laptop. It does the math, checks each craft's limit, and fills in the paperwork. It works with no signal.

**The app never decides GO or NO-GO.** A person does: the BPTC (Beach Party Team Commander) or the SRM (Senior Ramp Marshal).

Do not type names, unit information or real operation details into the app.

## How to get it

| Where | What to do |
|---|---|
| **Any phone, tablet or computer** | Open the link above in a web browser. |
| **Phone with no signal later** | Open the link once while you have signal. Then add it to your home screen: on iPhone tap Share, then **Add to Home Screen**. On Android tap ⋮, then **Install app**. After that it opens with no signal. |
| **Ship's computer or USB stick** | In the app, tap **Download offline copy (.zip)**. Unzip it and open `index.html`. No install, no account, no internet. |

### Is my copy the official one?

Anyone can edit a copy of a web page, so check any copy you got from someone else. In the app, go to section 9 and tap **Check this copy**. It compares the copy's files with the official list on the live site and says **matches** or **does NOT match**. A copy that does not match may be old or may have been edited: get a fresh one from the link above. It needs a connection. On an unzipped copy, choose all the files in the folder when it asks.

The official list is `v3/fingerprint.json`. It updates itself when the app changes on `main`. The hourly NOAA data is not part of it.

## How to use it

The app has two tabs at the top.

### Overview tab: the quick picture

- **Pick the beach.** A map shows the beach with an alligator marker, so you can check it is the right spot. You can switch between satellite, hybrid and regular map.
- **See an estimate right away.** The app uses NOAA buoy reports to guess the MSI before anyone counts a wave.
- **See the trend.** One chart shows the estimated MSI for the last 7 days and the next 5 days, with lines for the craft limits. Slide the bar under the chart (or tap the chart) to pick a time. Tap **Use in worksheet** to start the worksheet from that time.
- **Get the newest data.** Tap **Refresh NOAA data**. It shows how old the reports are. The app also does this by itself when you come back online, or when the data is more than 3 hours old.
- **Add your own beach.** Type its MGRS grid or its latitude and longitude, or tap **Use my location**. It is saved on your phone only.

### Worksheet tab: the real count

1. **Count each wave.** Tap how it broke (spilling, plunging or surging), then tap its height. The type stays picked, so most waves take one tap.
   - Tap **Info** to see pictures of each breaker type and how to judge wave height.
   - **Recorded waves** shows every wave as you add it, newest on top, with the time. Tap **Remove** to take one out, or **Undo** for the last one.
2. **Or say it.** Tap **Mic**, then tap the microphone on your phone's keyboard and talk: "two spilling, three plunging" or "spilling two, three, plunging four". The count goes up as you talk. It still works if the phone writes "spelling" or "surgery".
3. **Time the waves** with the stopwatch, or type the start and stop times.
4. **Fill in the rest** (angle, current, surf zone, wind). The units (ft, kts, °) are inside each box.
5. **Read the result.** The app shows every step of the math so you can check it against paper.
6. **Send and save.**
   - Copy the **BPT communicator call** (the radio report).
   - Tap **Fill data sheet (PDF)** to get the 2-page SUROB data sheet already filled in, or **Blank data sheet (PDF)** to fill it by hand.
7. **The BPTC or SRM records the decision.** If anything changes after that, the app asks them to confirm again.

**Already have a paper sheet or a spoken report?** Use **Speak, scan or paste a report**. Read the report out loud, or use the phone's camera text scanner on the paper. You check every number before it goes in.

## Safety checks

- The NOAA numbers are only an **estimate**. Buoys sit offshore, not in the surf. The real count always wins.
- If your count is very different from NOAA for the same time, the app shows a **CHECK** note so someone looks again. It never changes your numbers.
- Craft limit results are advice only. Until 33 waves are counted, they say **NO DATA**.

## Who is in control

| | |
|---|---|
| **Who decides** | Only the BPTC or SRM records GO, GO with restrictions or NO-GO. |
| **What the app will not do** | It does not decide, and it does not send what you type anywhere. It only loads its own files, map pictures (after you open the map) and the weather forecast. |
| **What to watch** | Warnings, the step-by-step math, CHECK notes and the "confirm again" flag. |
| **When to ask** | Any red warning, CHECK note, craft at or over its limit, or a number that does not match the paper goes to the BPTC or SRM. |
| **How to stop** | Close the tab. **Clear form** erases what is saved on the phone. |

## Where the data comes from

| Source | What it gives |
|---|---|
| NOAA buoys (NDBC) | Wave height, timing and direction for the last 7 days |
| NOAA and National Weather Service stations | Wind and how far you can see |
| National Weather Service forecast | Waves and wind for the next 5 days |
| Esri | Map pictures, only when you open the map |
| Your phone's keyboard dictation and camera text scanner (Apple or Google) | Turning speech or a paper sheet into text. The app only gets the text. |
| Claude Code (Anthropic) | Helped write and check the code |

All data is public. No AI runs inside the app. The NOAA data is saved inside the app so it works offline, and it updates itself about every hour.

## Versions

| | |
|---|---|
| [Version 3](https://wardenofthekeys.github.io/SUROB/v3/) | The current app. Use this one. |
| [Version 2](https://wardenofthekeys.github.io/SUROB/) | The earlier worksheet-only calculator. |
| Overview builds (`working-overview/` and the `surob-msi-calculator` zip files) | The team's overview app: beach picker, map, NOAA week, wave log and breaker pictures. Version 3 grew out of it. |

## Still to do

The correction tables match the team's SUROB data sheet. They still need a check against the official publication. Always check results against current command guidance.
