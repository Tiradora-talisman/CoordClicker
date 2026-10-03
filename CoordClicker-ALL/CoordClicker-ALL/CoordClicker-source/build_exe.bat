@echo off
REM Builds CoordClicker.exe. Put this file, coord_clicker.py and icon.ico in the same folder, then double-click it.
REM Needs Python installed (tick "Add Python to PATH" in the installer).

python -m pip install -U pyinstaller keyboard
python -m PyInstaller -F -w -i icon.ico -n CoordClicker coord_clicker.py

echo.
echo Done. Your exe is in the "dist" folder: dist\CoordClicker.exe
pause
