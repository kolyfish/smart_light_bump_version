@echo off
chcp 65001 > nul
cd /d "%~dp0.."

echo ==========================================
echo    MarketTradeAlertLight Auto-Installer
echo        (Windows Version)
echo ==========================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: 2. Create Virtual Environment
if not exist "venv" (
    echo [INFO] Creating virtual environment (venv)...
    python -m venv venv
)

:: 3. Install Dependencies
echo [INFO] Installing/Updating dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip > logs\install_log.txt 2>&1
pip install -r requirements.txt >> logs\install_log.txt 2>&1

if %errorlevel% neq 0 (
    echo [ERROR] Installation failed!
    echo Please check install_log.txt for details.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Dependencies installed.
)

:: 4. Run Application
echo [INFO] Starting application...
echo ------------------------------------------
python market_trade_alert_light.py

echo.
echo Application exit.
pause
deactivate
