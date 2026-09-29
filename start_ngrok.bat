@echo off
REM ============================================
REM NGROK SETUP - Super Simple Public URL
REM FreeFire Level Up Bot - ngrok Setup
REM ============================================

echo ==========================================
echo NGROK SETUP
echo FreeFire Level Up Bot
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

echo [1/4] Installing Python dependencies...
pip install aiohttp httpx google-play-scraper pycryptodome protobuf protobuf-decoder
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo SUCCESS: Python dependencies installed
echo.

echo [2/4] Checking if ngrok is installed...
ngrok version >nul 2>&1
if %errorlevel% neq 0 (
    echo ngrok not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/b4jDXQlk2_4/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to download ngrok
        pause
        exit /b 1
    )
    powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.'"
    del ngrok.zip
    echo SUCCESS: ngrok installed
) else (
    echo SUCCESS: ngrok already installed
)
echo.

echo [3/4] Starting the bot...
start /B python Main.py
timeout /t 5 /nobreak >nul
echo SUCCESS: Bot started
echo.

echo [4/4] Starting ngrok tunnel...
echo Your public URL will appear below:
echo.
ngrok http 20331
