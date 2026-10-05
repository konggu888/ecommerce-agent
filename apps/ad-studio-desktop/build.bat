@echo off
setlocal
python -m pip install pyinstaller
pyinstaller --noconsole --onefile --name AdStudio run.py
echo.
echo Build complete: dist\AdStudio.exe
pause
