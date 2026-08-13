@echo off
chcp 65001 >nul
setlocal

:: Clear host Python environment variables to prevent interference
set PYTHONPATH=
set PYTHONHOME=
set PYTHONUTF8=1

:: Prioritize portable Git and Python for this process only
set "PATH=%~dp0Git\cmd;%~dp0Python;%PATH%"

echo Initiating Safe Repository Push Report...
echo Repeatable/idempotent: safe to run multiple times.
echo This pushes only clean repos that are ahead of GitHub.
echo Current repos stay unchanged. Dirty/behind/diverged repos are skipped.
echo.
set "ONLY_ARG="
if not "%PUSH_ONLY%"=="" set "ONLY_ARG=--only %PUSH_ONLY%"

set "PERSONAL_OWNER="
for /f "delims=" %%U in ('gh api user --jq .login') do set "PERSONAL_OWNER=%%U"
if "%PERSONAL_OWNER%"=="" (
  echo GitHub CLI authentication is required.
  if not "%NO_PAUSE%"=="1" pause
  exit /b 1
)

python "%~dp0sourcerepo\tools\workspace\push_workspace.py" --workspace "%~dp0." --command-timeout 8 --personal-owner "%PERSONAL_OWNER%" %ONLY_ARG%
if errorlevel 1 (
  echo.
  echo Push report failed.
  if not "%NO_PAUSE%"=="1" pause
  exit /b 1
)

echo.
echo Choose push action:
echo   1. Exit only     - do not push anything
echo   2. Push safe     - push all clean ahead-only repos once
echo.
echo Press Enter for option 1.
set /p CONFIRM="Action number? "

if "%CONFIRM%"=="2" (
  python "%~dp0sourcerepo\tools\workspace\push_workspace.py" --workspace "%~dp0." --command-timeout 8 --personal-owner "%PERSONAL_OWNER%" %ONLY_ARG% --push
  set "RESULT=%ERRORLEVEL%"
) else (
  echo No repos pushed.
  set "RESULT=0"
)

echo.
if not "%NO_PAUSE%"=="1" pause
endlocal & exit /b %RESULT%
