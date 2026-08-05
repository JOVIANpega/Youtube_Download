@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ========================================
echo YouTube Downloader - EXE Build Tool
echo ========================================

pushd "%~dp0" >nul

set "PYTHON_EXE=%~dp0.pack-venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

REM Check for pyinstaller
"%PYTHON_EXE%" -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Info] PyInstaller not found. Installing...
    "%PYTHON_EXE%" -m pip install -r requirements.txt pyinstaller
)

REM Get Version
for /f "usebackq tokens=*" %%v in (`"%PYTHON_EXE%" -c "from version_info import VERSION; print(VERSION)"`) do set APP_VERSION=%%v
if not defined APP_VERSION set APP_VERSION=Unknown

echo [Status] Version detected: %APP_VERSION%

REM Cleanup old build
echo [Process] Cleaning old build files...
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1

REM Start Build
echo [Execute] Starting PyInstaller...
set SPEC=YouTube_Downloader.spec
"%PYTHON_EXE%" -m PyInstaller --clean --noconfirm "%SPEC%"

if %errorlevel% neq 0 (
    echo.
    echo [Error] Build failed. Please check the errors above.
    pause
    exit /b 1
)

REM Sync files
echo [Sync] Copying config and assets...
if not exist "dist\config" mkdir "dist\config"
copy /Y "config\*" "dist\config\" >nul
if not exist "dist\assets" mkdir "dist\assets"
xcopy /E /I /Y "assets" "dist\assets" >nul

echo.
echo ========================================
echo [Success] Build Complete!
echo [Path] Files are in dist\ directory.
echo ========================================
echo.

popd >nul
endlocal
pause
