@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON=py -3"
) else (
    set "PYTHON=python"
)

%PYTHON% -m pip install --upgrade pip
if errorlevel 1 exit /b %errorlevel%

%PYTHON% -m pip install -e ".[ui,ocr,argos]"
if errorlevel 1 exit /b %errorlevel%

echo Dependencies installed.
