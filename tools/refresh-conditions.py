"""Refresh v3/conditions-data.js from public NOAA sources.

Usage (from the repo root):
  python3 tools/refresh-conditions.py

Run by .github/workflows/refresh-conditions.yml every 3 hours.

Pulls, for the stations and beaches defined in v3/index.html:
  waves     NDBC realtime2 text files, last 7 days
  met       NWS station observations and CO-OPS wind, last 7 days
  forecast  NWS gridpoint forecast 2 km seaward of each beach, next 5 days

Row shapes match the working overview export. NWS "windMs" values are km/h,
exactly as in that export; the app converts them by station kind. Forecast
"windKmh" is km/h by name. Standard library only. A source that fails is
listed in "errors" and keeps its previous rows, so one outage never blanks
the file.
"""
import json
import math
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

APP = "v3/index.html"
OUT = "v3/conditions-data.js"
UA = "SUROB-MSI-Calculator (github.com/WardenOfTheKeys/SUROB)"
DAYS = 7
FC_DAYS = 5
FC_STEP_H = 3
SEAWARD_M = (2000, 5000)  # try 2 km out, then 5 km if the grid square has no waves

now = datetime.now(timezone.utc)
since = now - timedelta(days=DAYS)
errors = []


def get(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def ms(dt):
    return int(dt.timestamp() * 1000)


def read_sites():
    """Stations, beaches and beach-to-station links from the app, so there is one list to maintain."""
    html = open(APP, encoding="utf-8").read()
    st_block = html[html.index("const ST={"):html.index("const L=(")]
    stations = {}
    for key, sid, lat, lng, kind in re.findall(r"(\w+):\{id:'([^']+)',name:'[^']+',lat:([-\d.]+),lng:([-\d.]+)(?:,kind:'(\w+)')?\}", st_block):
        stations[key] = {"id": sid, "kind": kind or "ndbc", "lat": float(lat), "lng": float(lng)}
    reg_block = html[html.index("const REGIONS=["):html.index("const ST={")]
    beaches = {bid: (float(lat), float(lng)) for bid, lat, lng in re.findall(r"\{id:'([^']+)',name:'[^']+',lat:([-\d.]+),lng:([-\d.]+)", reg_block)}
    links = {}
    for bid, seaward, wave, wind, vis in re.findall(r"'([^']+)':L\((\d+),'(\w+)','(\w+)','(\w+)'", html):
        links[bid] = {"seaward": int(seaward), "wave": stations[wave], "wind": stations[wind], "vis": stations[vis]}
    if not stations or not beaches or set(links) != set(beaches):
        sys.exit(f"Could not read sites from {APP}: {len(stations)} stations, {len(beaches)} beaches, {len(links)} links")
    return stations, beaches, links


def ndbc_waves(sid):
    lines = get(f"https://www.ndbc.noaa.gov/data/realtime2/{sid}.txt", "text/plain").splitlines()
    cols = lines[0].lstrip("#").split()
    rows = []
    for line in lines[2:]:
        v = dict(zip(cols, line.split()))
        t = datetime(int(v["YY"]), int(v["MM"]), int(v["DD"]), int(v["hh"]), int(v["mm"]), tzinfo=timezone.utc)
        if t < since:
            break  # newest first
        f = lambda k: None if v.get(k, "MM") == "MM" else float(v[k])
        rows.append({"t": ms(t), "hsM": f("WVHT"), "dpd": f("DPD"), "apd": f("APD"), "mwd": f("MWD")})
    return sorted(rows, key=lambda r: r["t"])


def nws_met(sid):
    start = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    feats = json.loads(get(f"https://api.weather.gov/stations/{sid}/observations?start={start}&limit=500", "application/geo+json"))["features"]
    rows = {}
    for ft in feats:
        p = ft["properties"]
        t = ms(datetime.fromisoformat(p["timestamp"]))
        val = lambda k: p.get(k, {}).get("value")
        rows[t] = {"t": t, "windMs": val("windSpeed"), "windDir": val("windDirection"), "gustMs": val("windGust"),
                   "visM": val("visibility"), "weather": p.get("textDescription") or None}
    return sorted(rows.values(), key=lambda r: r["t"])


def coops_met(sid):
    fmt = "%Y%m%d %H:%M"
    url = ("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&application=surob_msi"
           f"&station={sid}&begin_date={since.strftime(fmt)}&end_date={now.strftime(fmt)}"
           "&time_zone=gmt&units=metric&format=json").replace(" ", "%20")
    data = json.loads(get(url)).get("data", [])
    num = lambda s: float(s) if s not in (None, "") else None
    rows = []
    for d in data:
        t = datetime.strptime(d["t"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        if t.minute == 0:  # hourly, like the export
            rows.append({"t": ms(t), "windMs": num(d.get("s")), "windDir": num(d.get("d")), "gustMs": num(d.get("g")), "visM": None, "weather": None})
    return rows


def seaward_point(lat, lng, bearing, m):
    b = math.radians(bearing)
    return lat + m * math.cos(b) / 111320, lng + m * math.sin(b) / (111320 * math.cos(math.radians(lat)))


def iso_hours(d):
    m = re.match(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?)?", d)
    return int(m[1] or 0) * 24 + int(m[2] or 0) + int(m[3] or 0) / 60


def grid_rows(props):
    """Samples the NWS grid every FC_STEP_H hours. Same method as gridRows() in the app."""
    def series(name, max_h=None):
        # Some offices fill swell direction with one 0 lasting days; a value held over max_h is treated as missing.
        out = []
        for v in (props.get(name) or {}).get("values", []):
            s, d = v["validTime"].split("/")
            t0, h = datetime.fromisoformat(s), iso_hours(d)
            if max_h is None or h <= max_h:
                out.append((t0, t0 + timedelta(hours=h), v["value"]))
        return out
    S = {"hsM": series("waveHeight"), "perS": series("wavePeriod"), "swellDir": series("primarySwellDirection", 24),
         "windKmh": series("windSpeed"), "windDir": series("windDirection")}
    step = FC_STEP_H * 3600
    t = datetime.fromtimestamp(math.ceil(now.timestamp() / step) * step, timezone.utc)
    rows = []
    while t < now + timedelta(days=FC_DAYS):
        r = {"t": ms(t)}
        for k, s in S.items():
            r[k] = next((v for t0, t1, v in s if t0 <= t < t1), None)
        if r["hsM"] is not None or r["windKmh"] is not None:
            rows.append(r)
        t += timedelta(seconds=step)
    return rows


def forecast(bid, lat, lng, seaward, prev):
    grid = prev.get("grid")
    tried = [grid] if grid else []
    if not grid:
        for m in SEAWARD_M:
            plat, plng = seaward_point(lat, lng, seaward, m)
            p = json.loads(get(f"https://api.weather.gov/points/{plat:.4f},{plng:.4f}", "application/geo+json"))["properties"]
            tried.append(f"{p['gridId']}/{p['gridX']},{p['gridY']}")
    for g in tried:
        props = json.loads(get(f"https://api.weather.gov/gridpoints/{g}", "application/geo+json"))["properties"]
        rows = grid_rows(props)
        if any(r["hsM"] for r in rows):
            return {"grid": g, "updated": props.get("updateTime"), "rows": rows}
    raise RuntimeError(f"no wave forecast at {', '.join(tried)}")


def main():
    stations, beaches, links = read_sites()
    try:
        s = open(OUT, encoding="utf-8").read()
        prev = json.loads(s[s.index("{"):s.rindex("}") + 1])
    except (OSError, ValueError):
        prev = {}
    waves, met, fc = {}, {}, {}

    for st in {l["wave"]["id"]: l["wave"] for l in links.values()}.values():
        try:
            waves[st["id"]] = ndbc_waves(st["id"])
        except Exception as e:
            errors.append(f"waves {st['id']}: {e}")
            waves[st["id"]] = prev.get("waves", {}).get(st["id"], [])

    for st in {s["id"]: s for l in links.values() for s in (l["wind"], l["vis"])}.values():
        try:
            met[st["id"]] = coops_met(st["id"]) if st["kind"] == "coops" else nws_met(st["id"])
        except Exception as e:
            errors.append(f"met {st['id']}: {e}")
            met[st["id"]] = prev.get("met", {}).get(st["id"], [])

    for bid, (lat, lng) in beaches.items():
        old = prev.get("forecast", {}).get(bid, {})
        try:
            fc[bid] = forecast(bid, lat, lng, links[bid]["seaward"], old)
        except Exception as e:
            errors.append(f"forecast {bid}: {e}")
            if old:
                fc[bid] = old

    data = {"fetchedAt": now.isoformat(timespec="milliseconds").replace("+00:00", "Z"), "waves": waves, "met": met, "forecast": fc, "errors": errors}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("window.SUROB_CONDITIONS=" + json.dumps(data, separators=(",", ":")) + ";\n")
    print(f"{len(waves)} wave stations, {len(met)} met stations, {len(fc)} beach forecasts, {len(errors)} errors")
    for e in errors:
        print("  " + e)


if __name__ == "__main__":
    main()
