@echo off
cd /d "%~dp0"
echo SUROB MSI Calculator: http://127.0.0.1:43124
echo Press Ctrl+C to stop.
start "" http://127.0.0.1:43124
python -m http.server 43124
if errorlevel 1 py -m http.server 43124
