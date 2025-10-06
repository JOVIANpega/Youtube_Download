@echo off
chcp 65001 >nul
echo ========================================
echo YouTube 下載器 - EXE 除錯打包腳本
echo ========================================

:: 檢查 Python 是否安裝
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] Python 未安裝或未加入 PATH
    pause
    exit /b 1
)

echo [信息] 檢查 Python 環境...
python -c "import sys; print(f'Python {sys.version}')"

:: 檢查 PyInstaller
echo [信息] 檢查 PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 安裝 PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [錯誤] PyInstaller 安裝失敗
        pause
        exit /b 1
    )
    echo [完成] PyInstaller 安裝成功
)

:: 檢查 icon 檔案
if not exist "assets\icon.ico" (
    echo [警告] 找不到 assets\icon.ico，將使用預設圖示
    set ICON_ARGS=
) else (
    echo [信息] 找到圖示檔案 assets\icon.ico
    set ICON_ARGS=--icon=assets\icon.ico
)

:: 檢查主程式
if not exist "main.py" (
    echo [錯誤] 找不到 main.py
    pause
    exit /b 1
)

:: 清理舊的 build 檔案
echo [信息] 清理舊的打包檔案...
if exist "build" rmdir /s /q "build"
if exist "dist_debug" rmdir /s /q "dist_debug"
if exist "main_debug.spec" del "main_debug.spec"

:: 打包命令（包含控制台）
echo.
echo [信息] 開始打包除錯版本...
echo [注意] 除錯版本會顯示控制台視窗，方便查看錯誤信息
echo [信息] 這可能需要幾分鐘時間，請耐心等待...
echo.

pyinstaller --onefile --console %ICON_ARGS% --clean --name "YouTube_Downloader_v1.3_Debug" --distpath "dist_debug" main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [完成] 除錯版本打包成功！
    echo ========================================
    echo [位置] EXE 檔案位於: dist_debug\YouTube_Downloader_v1.3_Debug.exe
    echo.
    
    :: 檢查檔案大小
    for %%i in ("dist_debug\YouTube_Downloader_v1.3_Debug.exe") do echo [大小] %%~zi 位元組 (%%~zi MB)
    echo.
    
    echo [提示] 這個版本包含控制台視窗，可看到程式執行過程和錯誤信息
    echo [提示] 如有問題，請查看控制台輸出的錯誤信息
    echo.
    
    :: 詢問是否開啟資料夾
    set /p choice="是否開啟 dist_debug 資料夾？(Y/N): "
    if /i "%choice%"=="Y" (
        explorer "dist_debug"
    )
) else (
    echo.
    echo ========================================
    echo [錯誤] 除錯版本打包失敗！
    echo ========================================
    echo [建議] 
    echo 1. 檢查 requirements.txt 中的依賴是否已安裝
    echo 2. 手動運行: pip install -r requirements.txt
    echo 3. 檢查 Python 環境是否正常
    echo 4. 嘗試先運行 python main.py 確認程式正常
    echo.
)

echo [完成] 腳本執行結束
pause
