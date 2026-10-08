@echo off
REM run_demo.bat - Start CodeCompass (FastAPI backend + Streamlit frontend)
REM Usage: double-click or run from cmd/PowerShell at the repo root.
REM Requires: ccenv virtual environment or Python on PATH.

setlocal EnableDelayedExpansion

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%ccenv\Scripts\python.exe
set VENV_UVICORN=%SCRIPT_DIR%ccenv\Scripts\uvicorn.exe
set VENV_STREAMLIT=%SCRIPT_DIR%ccenv\Scripts\streamlit.exe

echo.
echo  ========================================
echo    CodeCompass Demo Launcher
echo  ========================================
echo.

REM ── 1. Check for Python environment ──────────────────────────────────
if exist "%VENV_PYTHON%" (
    set "RUN_PY=%VENV_PYTHON%"
    set "RUN_UVICORN=%VENV_UVICORN%"
    set "RUN_STREAMLIT=%VENV_STREAMLIT%"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "RUN_PY=python"
        set "RUN_UVICORN=uvicorn"
        set "RUN_STREAMLIT=streamlit"
    ) else (
        echo  [ERROR] Python was not found on PATH or at: %SCRIPT_DIR%ccenv
        echo  Run:  python -m venv ccenv
        echo        ccenv\Scripts\pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM ── 2. Start the FastAPI backend in a new window ──────────────────────────
REM Fix 1: Export the API key so the FastAPI verify_api_key dependency can read it.
REM        The same value lives in frontend/.streamlit/secrets.toml for the Streamlit side.
set CODECOMPASS_API_KEY=cc-local-dev-2024
echo  [1/3] Starting FastAPI backend on http://localhost:8000 ...
start "CodeCompass Backend" cmd /k "set CODECOMPASS_API_KEY=cc-local-dev-2024 && cd /d %SCRIPT_DIR%backend && %RUN_UVICORN% app.main:app --reload --host 127.0.0.1 --port 8000"

REM ── 3. Wait for the backend health check to pass (max 30 s) ──────────────
echo  [2/3] Waiting for backend to be ready ...
set TRIES=0

:HEALTH_CHECK
set /a TRIES+=1
if %TRIES% GTR 30 goto WAIT_TIMEOUT

"%RUN_PY%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto BACKEND_READY

timeout /t 1 /nobreak >nul
goto HEALTH_CHECK

:WAIT_TIMEOUT
echo  [WARNING] Backend did not respond after 30 s.
echo           The frontend will still launch; backend may still be starting.
goto START_FRONTEND

:BACKEND_READY
echo  [2/3] Backend is online.

REM ── 4. Start the Streamlit frontend ──────────────────────────────────────
:START_FRONTEND
echo  [3/3] Starting Streamlit frontend on http://localhost:8501 ...
start "CodeCompass Frontend" cmd /k "cd /d %SCRIPT_DIR%frontend && %RUN_STREAMLIT% run app.py --server.port 8501"

REM ── 5. Open the browser after a short delay ──────────────────────────────
timeout /t 4 /nobreak >nul
echo.
echo  ========================================
echo    Opening http://localhost:8501 ...
echo  ========================================
echo.
REM start "" "http://localhost:8501"

echo  Both services are running.
echo  Close the two terminal windows to stop them.
echo.
pause
endlocal
