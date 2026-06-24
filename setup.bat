@echo off

where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found in PATH.
        echo Please run: py -3 main.py  or  python3 main.py
        pause
        exit /b 1
    ) else (
        set PYTHON=py -3
    )
) else (
    set PYTHON=python
)

echo Python found. Creating virtual environment...
%PYTHON% -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create venv.
    pause
    exit /b 1
)

echo Activating venv...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)

echo Done! Starting app...
python main.py
pause
