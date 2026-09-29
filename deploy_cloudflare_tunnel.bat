@echo off
REM ============================================
REM CLOUDFLARE TUNNEL DEPLOYMENT SCRIPT
REM FreeFire Level Up Bot - Cloudflare Tunnel Setup
REM ============================================

echo ==========================================
echo CLOUDFLARE TUNNEL DEPLOYMENT SCRIPT
echo FreeFire Level Up Bot Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [1/5] Installing Python dependencies...
pip install aiohttp httpx google-play-scraper pycryptodome protobuf protobuf-decoder
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo SUCCESS: Python dependencies installed
echo.

echo [2/5] Checking if cloudflared is installed...
cloudflared --version >nul 2>&1
if %errorlevel% neq 0 (
    echo cloudflared not found. Installing...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to download cloudflared
        pause
        exit /b 1
    )
    move cloudflared.exe C:\Windows\System32\ >nul 2>&1
    echo SUCCESS: cloudflared installed
) else (
    echo SUCCESS: cloudflared already installed
)
echo.

echo [3/5] Creating startup script...
echo @echo off > start_bot.bat
echo echo Starting FreeFire Level Up Bot... >> start_bot.bat
echo echo. >> start_bot.bat
echo echo Starting Cloudflare Tunnel... >> start_bot.bat
echo start /B cloudflared tunnel run --url http://localhost:20331 toxic-bot >> start_bot.bat
echo timeout /t 3 /nobreak >nul >> start_bot.bat
echo echo. >> start_bot.bat
echo echo Starting Bot... >> start_bot.bat
echo python Main.py >> start_bot.bat
echo pause >> start_bot.bat
echo SUCCESS: Startup script created
echo.

echo [4/5] Creating stop script...
echo @echo off > stop_bot.bat
echo echo Stopping FreeFire Level Up Bot... >> stop_bot.bat
echo taskkill /F /IM python.exe >nul 2>&1 >> stop_bot.bat
echo taskkill /F /IM cloudflared.exe >nul 2>&1 >> stop_bot.bat
echo echo Bot stopped >> stop_bot.bat
echo pause >> stop_bot.bat
echo SUCCESS: Stop script created
echo.

echo ==========================================
echo SETUP COMPLETED!
echo ==========================================
echo.
echo Next steps:
echo 1. Create Cloudflare account: https://dash.cloudflare.com/sign-up
echo 2. Login to Cloudflare and authenticate cloudflared:
echo    cloudflared tunnel login
echo 3. Create tunnel:
echo    cloudflared tunnel create toxic-bot
echo 4. Run the bot:
echo    start_bot.bat
echo.
echo Your bot will be accessible via Cloudflare tunnel URL
echo.
pause
