#!/bin/sh
cd "$(dirname "$0")" || exit 1
PORT=43124
URL="http://127.0.0.1:$PORT"
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python 3 is required to open this folder."
  exit 1
fi
(sleep 1
  if command -v open >/dev/null 2>&1; then open "$URL"
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL"
  fi) >/dev/null 2>&1 &
echo "SUROB MSI Calculator: $URL"
echo "Press Ctrl+C to stop."
exec "$PY" -m http.server "$PORT"
