@echo off
chcp 65001 >nul
setlocal

:: Clear host Python environment variables to prevent interference
set PYTHONPATH=
set PYTHONHOME=
set PYTHONUTF8=1

:: Prioritize portable Git and Python for this process only
set "PATH=%~dp0Git\cmd;%~dp0Python;%PATH%"

echo Trigger sourcerepo GitHub fan-out sync.
echo Repeatable/idempotent: safe to run multiple times.
echo Target repos with no changes are skipped by the workflow.
echo.
echo Choose action:
echo   1. Exit only      - do not trigger anything
echo   2. Run now        - trigger and show the GitHub Actions URL
echo   3. Run + watch    - trigger and wait until it finishes
echo   4. Active only    - trigger but skip archived repos
echo.
echo Press Enter for option 1.
set /p MODE="Action number? "

if "%MODE%"=="" set "MODE=1"
if "%MODE%"=="1" (
  echo No source sync triggered.
  set "RESULT=0"
  goto DONE
)

set "SYNC_ARGS="
if "%MODE%"=="3" set "SYNC_ARGS=-Watch"
if "%MODE%"=="4" set "SYNC_ARGS=-NoArchived"

if not "%MODE%"=="2" if not "%MODE%"=="3" if not "%MODE%"=="4" (
  echo No source sync triggered.
  set "RESULT=0"
  goto DONE
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sourcerepo\tools\workspace\run_source_sync.ps1" %SYNC_ARGS%
set "RESULT=%ERRORLEVEL%"

:DONE
echo.
if not "%NO_PAUSE%"=="1" pause
endlocal & exit /b %RESULT%
