@echo off
echo YouTube 影片下載器 V1.1.1 安裝程式
echo ====================================

REM 檢查是否以管理員權限執行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 正在以管理員權限安裝...
) else (
    echo 請以管理員權限執行此安裝程式
    pause
    exit /b 1
)

REM 創建安裝目錄
set INSTALL_DIR=C:\Program Files\YouTube下載器V1.1.1
echo 安裝目錄: %INSTALL_DIR%

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM 複製檔案
echo 正在複製檔案...
copy "dist\YouTube下載器V1.1.1.exe" "%INSTALL_DIR%\"
copy "RELEASE_NOTES_V1.1.md" "%INSTALL_DIR%\"
copy "CHANGELOG.md" "%INSTALL_DIR%\"
copy "UI_IMPROVEMENTS_V1.1.md" "%INSTALL_DIR%\"

REM 創建桌面捷徑
echo 正在創建桌面捷徑...
set DESKTOP=%USERPROFILE%\Desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\YouTube下載器V1.1.1.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\YouTube下載器V1.1.1.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "YouTube 影片下載器 V1.1.1" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

REM 創建開始選單捷徑
echo 正在創建開始選單捷徑...
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
if not exist "%START_MENU%\YouTube下載器" mkdir "%START_MENU%\YouTube下載器"

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateStartMenuShortcut.vbs
echo sLinkFile = "%START_MENU%\YouTube下載器\YouTube下載器V1.1.1.lnk" >> CreateStartMenuShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateStartMenuShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\YouTube下載器V1.1.1.exe" >> CreateStartMenuShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateStartMenuShortcut.vbs
echo oLink.Description = "YouTube 影片下載器 V1.1.1" >> CreateStartMenuShortcut.vbs
echo oLink.Save >> CreateStartMenuShortcut.vbs
cscript //nologo CreateStartMenuShortcut.vbs
del CreateStartMenuShortcut.vbs

echo.
echo ✅ 安裝完成！
echo.
echo 檔案位置: %INSTALL_DIR%
echo 桌面捷徑: %DESKTOP%\YouTube下載器V1.1.1.lnk
echo 開始選單: 開始 > 程式集 > YouTube下載器
echo.
echo 新功能:
echo - 下載完成自定義對話框
echo - 一鍵開啟檔案目錄
echo - 可自訂是否顯示提醒視窗
echo.
echo 按任意鍵退出...
pause >nul
