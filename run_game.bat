@echo off
title Crypt Survivor: Arcane Depths
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo The game exited with an error (exit code: %ERRORLEVEL%).
    if exist "crash_log.txt" (
        echo Details from crash_log.txt:
        echo --------------------------------------------------------
        type crash_log.txt
        echo --------------------------------------------------------
    )
    echo ========================================================
    pause
)
