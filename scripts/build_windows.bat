@echo off
echo 🚀 Building MarketTradeAlertLight for Windows...

:: Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

:: Clean previous builds
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist MarketTradeAlertLight.spec del MarketTradeAlertLight.spec

:: Run PyInstaller
:: Note: ; is the separator for Windows --add-data
pyinstaller app.py ^
    --name=MarketTradeAlertLight ^
    --onefile ^
    --console ^
    --add-data "templates;templates" ^
    --clean

echo.
echo ✅ Build complete!
echo The executable is located at: dist\MarketTradeAlertLight.exe
pause
