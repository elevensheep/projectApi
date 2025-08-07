@echo off
echo ========================================
echo    Stop All Services Script
echo ========================================
echo.

echo Stopping all running services...
echo.

:: Stop React development server (Port 3000)
echo [1/3] Stopping React development server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    taskkill /f /pid %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo React server has been stopped.
    ) else (
        echo React server is already stopped or not running.
    )
)

:: Stop Spring Boot server (Port 8080)
echo [2/3] Stopping Spring Boot server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do (
    taskkill /f /pid %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo Spring Boot server has been stopped.
    ) else (
        echo Spring Boot server is already stopped or not running.
    )
)

:: Stop FastAPI server (Port 8000)
echo [3/3] Stopping FastAPI server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo FastAPI server has been stopped.
    ) else (
        echo FastAPI server is already stopped or not running.
    )
)

:: Stop Java processes (Spring Boot related)
echo Cleaning up Java processes...
taskkill /f /im java.exe >nul 2>&1

:: Stop Node.js processes (React related)
echo Cleaning up Node.js processes...
taskkill /f /im node.exe >nul 2>&1

echo.
echo ========================================
echo    All services have been stopped!
echo ========================================
echo.
pause 