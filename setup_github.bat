@echo off
REM ============================================
REM GITHUB SETUP SCRIPT (Windows)
REM FreeFire Level Up Bot - GitHub & Railway Setup
REM ============================================

echo ==========================================
echo GITHUB SETUP SCRIPT
echo FreeFire Level Up Bot Setup
echo ==========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed
    echo Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git is installed!
echo.

REM Ask for GitHub username
set /p github_username="Enter your GitHub username: "

if "%github_username%"=="" (
    echo ERROR: GitHub username is required
    pause
    exit /b 1
)

echo.
echo Setting up Git repository...
echo.

REM Initialize git
git init
echo [OK] Git initialized

REM Add all files
git add .
echo [OK] Files staged

REM Configure git if not configured
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    set /p git_name="Enter your name for Git: "
    git config --global user.name "%git_name%"
)

git config user.email >nul 2>&1
if %errorlevel% neq 0 (
    set /p git_email="Enter your email for Git: "
    git config --global user.email "%git_email%"
)

REM Commit
git commit -m "Initial commit - FreeFire Level Up Bot"
echo [OK] Files committed

REM Add remote
git remote add origin https://github.com/%github_username%/toxic-bot.git
echo [OK] Remote added

REM Rename branch to main
git branch -M main
echo [OK] Branch renamed to main

echo.
echo ==========================================
echo SETUP COMPLETED!
echo ==========================================
echo.
echo Next steps:
echo 1. Create a new repository on GitHub:
echo    https://github.com/new
echo    - Name: toxic-bot
echo    - Make it PRIVATE
echo.
echo 2. Push to GitHub:
echo    git push -u origin main
echo.
echo 3. Go to Railway.app and deploy:
echo    https://railway.app/new
echo    - Select your toxic-bot repository
echo    - Click Deploy
echo.
pause
