@echo off
echo ===================================================
echo A2R Console - PyInstaller Build Script
echo ===================================================
echo.
echo Make sure you have installed pyinstaller:
echo pip install pyinstaller
echo.
echo Also make sure you placed these files in the folder:
echo 1. app.ico
echo 2. pdftotext.exe
echo 3. SumatraPDF.exe
echo (and tesseract folder if needed locally)
echo.
pause

pyinstaller --noconfirm --onedir --windowed --icon "app.ico" ^
    --add-data "pdftotext.exe;." ^
    --add-data "SumatraPDF.exe;." ^
    "main.py"

echo.
echo Build finished! Check the "dist" folder.
pause
