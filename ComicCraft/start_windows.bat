@echo off

echo ==============================
echo ComicCraft AI Comic Generator
echo ==============================

echo.

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...

call .venv\Scripts\activate.bat

echo.

echo Installing dependencies...

python -m pip install --upgrade pip

pip install -r requirements.txt

echo.

echo Starting ComicCraft...

uvicorn app.main:app --reload

pause