@echo off
echo Starting AI News Application...
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python and try again.
    pause
    exit /b 1
)

REM Check if venv exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment. Please check your Python installation.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)
echo Dependencies installed successfully.

REM Start the Flask application in the background
echo Starting Flask application...
start /B cmd /c "venv\Scripts\python.exe app.py"

REM Wait for the server to start
echo Waiting for server to start...
timeout /t 8 /nobreak > nul

REM Open the browser
echo Opening browser...
start http://localhost:5000

echo.
echo Application is running. Do not close this window if you want to keep the server running.
echo.

REM Keep the terminal window open
cmd /k 