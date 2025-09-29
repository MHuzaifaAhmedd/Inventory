@echo off
title Mona Beauty Store - Build Executable
echo ================================================
echo MONA BEAUTY STORE - BUILD EXECUTABLE
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later and try again
    pause
    exit /b 1
)

echo Python found. Starting build process...
echo.

REM Run the production build script
python build_production.py

echo.
echo Build process completed!
echo Check the output above for any errors.
echo.
pause

