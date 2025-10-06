@echo off
chcp 65001 >nul
echo ========================================
echo YouTube 下載器 - 快速打包
echo ========================================
echo [提示] 這個腳本適用於快速重複打包
echo [注意] 不會清理舊檔案，自動開啟結果資料夾
echo.

:: 檢查是否已安裝 pyinstaller
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 請先運行 build_exe.bat 安裝 PyInstaller
    pause
    exit /b 1
)

:: 檢查是否有 icon
if exist "assets\icon.ico" (
    pyinstaller --onefile --noconsole --icon=assets\icon.ico main.py
) else (
    pyinstaller --onefile --noconsole main.py
)

if %errorlevel% equ 0 (
    echo [完成] 打包成功！
    explorer "dist"
) else (
    echo [錯誤] 打包失敗
)

pause
