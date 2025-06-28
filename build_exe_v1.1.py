#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 影片下載器 V1.1.0 打包腳本
將 Python 程式打包成 Windows EXE 檔案
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """檢查必要的依賴套件"""
    print("🔍 檢查依賴套件...")
    
    required_packages = {
        'PyInstaller': 'PyInstaller',
        'yt-dlp': 'yt_dlp',
        'PySide6': 'PySide6'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} 已安裝")
        except ImportError:
            print(f"❌ {package_name} 未安裝")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n⚠️ 缺少以下套件: {', '.join(missing_packages)}")
        print("請執行以下指令安裝:")
        for package in missing_packages:
            if package == 'PyInstaller':
                print(f"pip install {package}")
            elif package == 'yt-dlp':
                print(f"pip install {package}")
            elif package == 'PySide6':
                print(f"pip install {package}")
        return False
    
    print("✅ 所有依賴套件都已安裝")
    return True

def create_version_file():
    """創建版本資訊檔案"""
    version_content = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 1, 0, 0),
    prodvers=(1, 1, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'YouTube Downloader'),
         StringStruct(u'FileDescription', u'YouTube 影片下載器 V1.1.0'),
         StringStruct(u'FileVersion', u'1.1.0'),
         StringStruct(u'InternalName', u'youtube_downloader'),
         StringStruct(u'LegalCopyright', u'Copyright (c) 2024'),
         StringStruct(u'OriginalFilename', u'YouTube下載器.exe'),
         StringStruct(u'ProductName', u'YouTube 影片下載器'),
         StringStruct(u'ProductVersion', u'1.1.0')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    print("✅ 版本資訊檔案已創建")

def build_exe():
    """打包成 EXE 檔案"""
    print("\n🚀 開始打包...")
    
    # 創建版本資訊檔案
    create_version_file()
    
    # PyInstaller 指令
    cmd = [
        'pyinstaller',
        '--onefile',                    # 單一檔案
        '--windowed',                   # 無控制台視窗
        '--name=YouTube下載器V1.1',     # EXE 檔案名稱
        '--icon=icon.ico',              # 圖示（如果存在）
        '--version-file=version_info.txt',  # 版本資訊
        '--add-data=src/user_preferences.json;.',  # 包含設定檔案
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=yt_dlp',
        '--hidden-import=ssl',
        '--hidden-import=certifi',
        '--clean',                      # 清理暫存檔案
        'src/main_pyside.py'            # 主程式
    ]
    
    # 如果沒有圖示檔案，移除圖示參數
    if not os.path.exists('icon.ico'):
        cmd.remove('--icon=icon.ico')
        print("⚠️ 未找到 icon.ico，將使用預設圖示")
    
    print(f"執行指令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return False

def create_installer():
    """創建安裝腳本"""
    print("\n📦 創建安裝腳本...")
    
    installer_content = """@echo off
echo YouTube 影片下載器 V1.1.0 安裝程式
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
set INSTALL_DIR=C:\\Program Files\\YouTube下載器V1.1
echo 安裝目錄: %INSTALL_DIR%

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM 複製檔案
echo 正在複製檔案...
copy "dist\\YouTube下載器V1.1.exe" "%INSTALL_DIR%\\"
copy "RELEASE_NOTES_V1.1.md" "%INSTALL_DIR%\\"
copy "CHANGELOG.md" "%INSTALL_DIR%\\"
copy "UI_IMPROVEMENTS_V1.1.md" "%INSTALL_DIR%\\"

REM 創建桌面捷徑
echo 正在創建桌面捷徑...
set DESKTOP=%USERPROFILE%\\Desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\\YouTube下載器V1.1.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\YouTube下載器V1.1.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "YouTube 影片下載器 V1.1.0" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

REM 創建開始選單捷徑
echo 正在創建開始選單捷徑...
set START_MENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs
if not exist "%START_MENU%\\YouTube下載器" mkdir "%START_MENU%\\YouTube下載器"

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateStartMenuShortcut.vbs
echo sLinkFile = "%START_MENU%\\YouTube下載器\\YouTube下載器V1.1.lnk" >> CreateStartMenuShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateStartMenuShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\YouTube下載器V1.1.exe" >> CreateStartMenuShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateStartMenuShortcut.vbs
echo oLink.Description = "YouTube 影片下載器 V1.1.0" >> CreateStartMenuShortcut.vbs
echo oLink.Save >> CreateStartMenuShortcut.vbs
cscript //nologo CreateStartMenuShortcut.vbs
del CreateStartMenuShortcut.vbs

echo.
echo ✅ 安裝完成！
echo.
echo 檔案位置: %INSTALL_DIR%
echo 桌面捷徑: %DESKTOP%\\YouTube下載器V1.1.lnk
echo 開始選單: 開始 > 程式集 > YouTube下載器
echo.
echo 按任意鍵退出...
pause >nul
"""
    
    with open('install_v1.1.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("✅ 安裝腳本已創建: install_v1.1.bat")

def create_portable_package():
    """創建便攜版套件"""
    print("\n📁 創建便攜版套件...")
    
    portable_dir = "YouTube下載器V1.1_便攜版"
    
    # 清理舊目錄
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    # 創建新目錄
    os.makedirs(portable_dir)
    
    # 複製檔案
    files_to_copy = [
        ("dist/YouTube下載器V1.1.exe", f"{portable_dir}/YouTube下載器V1.1.exe"),
        ("RELEASE_NOTES_V1.1.md", f"{portable_dir}/發布說明.md"),
        ("CHANGELOG.md", f"{portable_dir}/變更日誌.md"),
        ("UI_IMPROVEMENTS_V1.1.md", f"{portable_dir}/UI改進說明.md"),
        ("使用說明.md", f"{portable_dir}/使用說明.md"),
        ("VERSION", f"{portable_dir}/VERSION")
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✅ 複製: {src} -> {dst}")
        else:
            print(f"⚠️ 檔案不存在: {src}")
    
    # 創建便攜版說明
    portable_readme = f"""# YouTube 影片下載器 V1.1.0 便攜版

## 📋 說明
這是便攜版，無需安裝，直接執行即可使用。

## 🚀 使用方式
1. 雙擊 `YouTube下載器V1.1.exe` 啟動程式
2. 輸入 YouTube 影片網址
3. 點擊「獲取資訊」分析影片
4. 選擇解析度並開始下載

## 📁 檔案說明
- `YouTube下載器V1.1.exe` - 主程式
- `發布說明.md` - 版本發布說明
- `變更日誌.md` - 詳細變更記錄
- `UI改進說明.md` - UI 改進詳細說明
- `使用說明.md` - 使用指南
- `VERSION` - 版本號

## 🔧 系統需求
- Windows 10/11
- 4GB RAM (推薦 8GB)
- 100MB 硬碟空間

## 📞 技術支援
如遇問題，請查看相關說明文件或更新 yt-dlp。

版本: V1.1.0
發布日期: 2024-12-19
"""
    
    with open(f"{portable_dir}/README.md", 'w', encoding='utf-8') as f:
        f.write(portable_readme)
    
    print(f"✅ 便攜版套件已創建: {portable_dir}")

def main():
    """主函數"""
    print("🎯 YouTube 影片下載器 V1.1.0 打包工具")
    print("=" * 50)
    
    # 檢查依賴
    if not check_dependencies():
        print("\n❌ 請先安裝缺少的依賴套件")
        return
    
    # 打包 EXE
    if not build_exe():
        print("\n❌ 打包失敗")
        return
    
    # 創建安裝腳本
    create_installer()
    
    # 創建便攜版套件
    create_portable_package()
    
    print("\n🎉 打包完成！")
    print("\n📦 生成的檔案:")
    print("  - dist/YouTube下載器V1.1.exe (主程式)")
    print("  - install_v1.1.bat (安裝腳本)")
    print("  - YouTube下載器V1.1_便攜版/ (便攜版套件)")
    
    print("\n📋 使用建議:")
    print("  1. 測試 dist/YouTube下載器V1.1.exe 是否正常運行")
    print("  2. 使用 install_v1.1.bat 進行系統安裝")
    print("  3. 或直接使用便攜版套件")
    
    print("\n🔧 清理檔案:")
    print("  - 可刪除 build/ 和 dist/ 目錄中的暫存檔案")
    print("  - 保留 YouTube下載器V1.1.exe 和便攜版套件")

if __name__ == "__main__":
    main() 