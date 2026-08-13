@echo off
chcp 65001 >nul
setlocal

:: Clear host Python environment variables to prevent interference
set PYTHONPATH=
set PYTHONHOME=
set PYTHONUTF8=1

:: Prioritize portable Git and Python for this process only
set "PATH=%~dp0Git\cmd;%~dp0Python;%PATH%"

echo Initiating Zero-Install Context Extraction...
echo.
python "%~dp0sourcerepo\tools\workspace\collect_readmes.py" --workspace "%~dp0"

echo.
if not "%NO_PAUSE%"=="1" pause
endlocal
