"""Writes v3/fingerprint.json: the SHA-256 of each Version 3 app file.

The "Check this copy" button in section 9 compares a copy's files with this
list on the live site. A copy whose files were changed anywhere else (a thumb
drive, a share drive, an email attachment) shows as NOT matching.

conditions-data.js is left out on purpose: the NOAA data in it changes every
hour, so it would never match. It holds only weather numbers, not app logic.

Usage (from the repo root):  python3 tools/make-fingerprint.py
The fingerprint workflow runs this on every push to main that changes v3/.
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V3 = os.path.join(ROOT, "v3")
# The files that make up the app. Keep in step with COPY_FILES and VERIFY_FILES in v3/index.html.
FILES = ["index.html", "data-sheet.js", "sw.js", "manifest.webmanifest", "icon.svg", "icon-192.png", "icon-512.png"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def main():
    files = {name: sha256(os.path.join(V3, name)) for name in FILES}
    # One short code for the whole app: the hash of the per-file list, in a fixed order.
    combined = hashlib.sha256("".join(f"{n}:{files[n]}\n" for n in FILES).encode()).hexdigest()
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        commit = ""
    out = {
        "app": "SUROB MSI Calculator, Version 3",
        "made": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": commit,
        "combined": combined,
        "files": files,
    }
    path = os.path.join(V3, "fingerprint.json")
    old = None
    if os.path.exists(path):
        with open(path) as f:
            old = json.load(f)
    # Rewrite only when a file changed, so the date shows when the app last changed.
    if old and old.get("files") == files:
        print("Fingerprint unchanged:", combined[:12])
        return 0
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("Fingerprint written:", combined[:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
