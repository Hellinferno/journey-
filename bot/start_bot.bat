@echo off
echo Starting Micro-CFO Telegram Bot...
echo.

:: Check for virtual environment
if exist venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo Virtual environment not found. Using system Python...
)

:: Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo Checking dependencies...
    pip install -r requirements.txt
)

echo.
echo Launching bot...
python bot.py
pause
