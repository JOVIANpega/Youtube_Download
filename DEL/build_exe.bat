@echo off
chcp 65001 >nul

setlocal EnableExtensions EnableDelayedExpansion

echo ========================================
echo YouTube 下載器 - EXE 打包腳本
echo ========================================

REM Ensure running from repo root
pushd "%~dp0" >nul

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] Python 未安裝或未加入 PATH
    pause
    exit /b 1
)

echo [信息] 檢查 PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 安裝 PyInstaller...
    python -m pip install --upgrade pyinstaller
    if %errorlevel% neq 0 (
        echo [錯誤] PyInstaller 安裝失敗
        pause
        exit /b 1
    )
)

REM Read version from version_info.py
for /f "usebackq tokens=*" %%v in (`python - <<PY
from version_info import VERSION
print(VERSION)
PY`) do set APP_VERSION=%%v
if not defined APP_VERSION set APP_VERSION=2.5.0

set SPEC=YouTube_Downloader_v1.3.spec
if not exist "%SPEC%" (
  echo [錯誤] 找不到 spec 檔: %SPEC%
  pause
  exit /b 1
)

echo [信息] 清理舊的打包檔案...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [信息] 開始打包 (版本 %APP_VERSION%) ...
pyinstaller --clean --noconfirm "%SPEC%"
if %errorlevel% neq 0 (
  echo [錯誤] 打包失敗
  pause
  exit /b 1
)

echo.
echo ========================================
echo [完成] 打包成功！
echo [位置] dist\ 目錄
echo ========================================

popd >nul

endlocal
