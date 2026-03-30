@echo off
title MedScan AI - Launcher
color 0A
cls

echo.
echo  ========================================================
echo    __  __          _ ____                     _    ___
echo   ^|  \/  ^| ___  __^| / ___|  ___ __ _ _ __   / \  ^|_ _^|
echo   ^| ^|\/^| ^|/ _ \/ _` \___ \ / __/ _` ^| '_ \ / _ \  ^| ^|
echo   ^| ^|  ^| ^|  __/ (_^| ^|___) ^| (_^| (_^| ^| ^| ^| ^/ ___ \ ^| ^|
echo   ^|_^|  ^|_^\___^\__,_^|____/ \___\__,_^|_^| ^|_/_/   \_\___^|
echo.
echo  ========================================================
echo.

:: ── Paths ──────────────────────────────────────────────────────────────────
set ROOT=C:\Users\HP\OneDrive\Desktop\health
set BACKEND=%ROOT%\backend
set FRONTEND=%ROOT%\frontend
set VENV=%ROOT%\.venv
set PYTHON=%VENV%\Scripts\python.exe
set PIP=%VENV%\Scripts\pip.exe

:: ── Step 1: Verify virtual environment ─────────────────────────────────────
echo [1/4] Checking virtual environment...
if not exist "%PYTHON%" (
    echo  [ERROR] Virtual environment not found at %VENV%
    echo  Creating a new virtual environment...
    python -m venv "%VENV%"
    if errorlevel 1 (
        echo  [FATAL] Could not create venv. Make sure Python is installed.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
) else (
    echo  [OK] Virtual environment found.
)

:: ── Step 2: Install/verify backend dependencies ────────────────────────────
echo.
echo [2/4] Verifying backend dependencies...
"%PYTHON%" -c "import fastapi, uvicorn, pdfplumber, cv2" 2>nul
if errorlevel 1 (
    echo  [INFO] Installing backend requirements (first-time setup)...
    "%PIP%" install -r "%BACKEND%\requirements.txt" --quiet
    if errorlevel 1 (
        echo  [ERROR] pip install failed. Check your internet connection.
        pause
        exit /b 1
    )
    echo  [OK] Dependencies installed.
) else (
    echo  [OK] All backend dependencies present.
)

:: ── Step 3: Kill any stale processes on port 8000 ──────────────────────────
echo.
echo [3/4] Clearing port 8000 if in use...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo  [INFO] Killing PID %%a on port 8000
    taskkill /PID %%a /F >nul 2>&1
)
echo  [OK] Port 8000 is free.

:: ── Step 4: Launch backend + frontend ─────────────────────────────────────
echo.
echo [4/4] Launching servers...
echo.

:: Start backend in its own window using the venv python
start "MedScan Backend :8000" cmd /k "title MedScan Backend ^& color 0B ^& echo Starting FastAPI backend... ^& cd /d %BACKEND% ^& %PYTHON% -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: Give backend 5 seconds to initialize
echo  Waiting for backend to start (5s)...
timeout /t 5 /nobreak >nul

:: Verify backend actually came up
echo  Verifying backend health...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo  [WARNING] Backend may still be initializing - continuing...
) else (
    echo  [OK] Backend is responding on port 8000.
)

:: Start frontend in its own window
start "MedScan Frontend :5173" cmd /k "title MedScan Frontend ^& color 0E ^& echo Starting React frontend... ^& cd /d %FRONTEND% ^& npm run dev -- --host 0.0.0.0"

echo  Waiting for frontend to start (6s)...
timeout /t 6 /nobreak >nul

:: ── Done ───────────────────────────────────────────────────────────────────
cls
echo.
echo  ========================================================
echo   MedScan AI is LIVE!
echo.
echo   Frontend  ->  http://localhost:5173
echo   Backend   ->  http://localhost:8000
echo   API Docs  ->  http://localhost:8000/docs
echo  ========================================================
echo.
echo  Two terminal windows have opened:
echo    - Yellow window  = Backend  (FastAPI / Uvicorn)
echo    - Blue window    = Not used / monitoring
echo.
echo  Press any key to open the app in your browser...
pause >nul

start "" "http://localhost:5173"
