@echo off
echo ========================================
echo    Project Startup Script
echo ========================================
echo.

:: Check Java version
echo Checking Java version...
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo Java is not installed. Please install Java 17 or higher.
    pause
    exit /b 1
)

:: Check Node.js version
echo Checking Node.js version...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js.
    pause
    exit /b 1
)

:: Check Python version
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo All required programs are installed.
echo.

:: Save current directory
set ORIGINAL_DIR=%CD%

echo ========================================
echo    Starting Services...
echo ========================================
echo.

:: 1. Start FastAPI server (background)
echo [1/3] Starting FastAPI server... (Port: 8000)
cd /d "%ORIGINAL_DIR%\py"
if not exist "venv39\Scripts\activate.bat" (
    echo Python virtual environment not found. Creating...
    python -m venv venv39
)
call venv39\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
start "FastAPI Server" cmd /k "cd /d %ORIGINAL_DIR%\py && call venv39\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

:: 2. Start Spring Boot server (background)
echo [2/3] Starting Spring Boot server... (Port: 8080)
cd /d "%ORIGINAL_DIR%\bookSpring"
start "Spring Boot Server" cmd /k "cd /d %ORIGINAL_DIR%\bookSpring && gradlew bootRun"
timeout /t 5 /nobreak >nul

:: 3. Start React development server (background)
echo [3/3] Starting React development server... (Port: 3000)
cd /d "%ORIGINAL_DIR%\frontend"
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install >nul 2>&1
)
start "React Development Server" cmd /k "cd /d %ORIGINAL_DIR%\frontend && npm start"
timeout /t 3 /nobreak >nul

:: Return to original directory
cd /d "%ORIGINAL_DIR%"

echo.
echo ========================================
echo    All services have been started!
echo ========================================
echo.
echo Service URLs:
echo - React Frontend: http://localhost:3000
echo - Spring Boot API: http://localhost:8080
echo - FastAPI: http://localhost:8000
echo - FastAPI Docs: http://localhost:8000/docs
echo.
echo All servers are running in background.
echo To stop servers, close each terminal window or press Ctrl+C.
echo.
pause 