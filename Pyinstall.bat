@echo off
cd /d "%~dp0"
pyinstaller --windowed --onefile main.py
pause
