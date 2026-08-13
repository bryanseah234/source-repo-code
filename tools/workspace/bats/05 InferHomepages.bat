@echo off
chcp 65001 >nul
setlocal

:: Clear host Python environment variables to prevent interference
set PYTHONPATH=
set PYTHONHOME=
set PYTHONUTF8=1

:: Prioritize portable Git and Python for this process only
set "PATH=%~dp0Git\cmd;%~dp0Python;%PATH%"

set "WORKSPACE=%~dp0"
set "SOURCEREPO=%WORKSPACE%sourcerepo"

if not exist "%SOURCEREPO%\tools\workspace\infer_homepages.py" (
  echo Missing sourcerepo homepage tool:
  echo %SOURCEREPO%\tools\workspace\infer_homepages.py
  echo.
  if not "%NO_PAUSE%"=="1" pause
  exit /b 1
)

echo Checking inferred project homepages...
echo Policy:
echo - GitHub Pages: https://hongyime.github.io/REPO/
echo - Custom/Vercel: real deployment URL
echo - No proven deployment: blank
echo.

pushd "%SOURCEREPO%"
python ".\tools\workspace\infer_homepages.py"
if errorlevel 1 (
  popd
  echo.
  echo Dry run failed.
  if not "%NO_PAUSE%"=="1" pause
  exit /b 1
)

echo.
echo Type APPLY to update repos.yml and live GitHub homepage fields.
echo Anything else exits without changes.
set /p CONFIRM="Apply homepage changes? "

if /I "%CONFIRM%"=="APPLY" (
  python ".\tools\workspace\infer_homepages.py" --write --apply-live
  set "RESULT=%ERRORLEVEL%"
) else (
  echo No changes applied.
  set "RESULT=0"
)

popd
echo.
if not "%NO_PAUSE%"=="1" pause
exit /b %RESULT%
