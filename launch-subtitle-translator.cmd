@echo off
setlocal

pushd "%~dp0" || exit /b 1

if defined VIRTUAL_ENV if exist "%VIRTUAL_ENV%\Scripts\python.exe" (
    set "PYTHON="%VIRTUAL_ENV%\Scripts\python.exe""
)

if not defined PYTHON (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON=python"
    ) else (
        set "PYTHON=py -3"
    )
)

%PYTHON% -m game_subtitle_translator.main %*
set "EXIT_CODE=%errorlevel%"
popd
exit /b %EXIT_CODE%
