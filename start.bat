@echo off
SETLOCAL EnableDelayedExpansion
title JARVIS AI OS Bootloader

echo ===================================================
echo               JARVIS AI OS BOOTLOADER              
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

:: Check if .env exists, if not copy from .env.example
if not exist .env (
    echo [INFO] .env file not found. Creating from .env.example...
    copy .env.example .env >nul
)

:: Setup Virtual Environment
if not exist .venv (
    echo [INFO] Creating Python Virtual Environment (.venv)...
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate Virtual Environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install Requirements
echo [INFO] Checking/Installing dependencies...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

:: Start Application
echo [INFO] Starting JARVIS AI OS...
echo ===================================================
echo.
python -m jarvis.main

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] JARVIS terminated with exit code %errorlevel%.
)

echo.
echo Press any key to exit.
pause >nul
deactivate
