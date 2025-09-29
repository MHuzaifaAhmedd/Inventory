@echo off
title Mona Beauty Store - Inventory Management System
echo Starting Mona Beauty Store Inventory System...
echo.

REM Check if the executable exists
if not exist "MonaBeautyStore_Inventory.exe" (
    echo ERROR: MonaBeautyStore_Inventory.exe not found!
    echo Please make sure the executable is in the same folder as this script.
    pause
    exit /b 1
)

REM Run the application
start "" "MonaBeautyStore_Inventory.exe"

REM Wait a moment and then close this window
timeout /t 3 /nobreak >nul
exit
