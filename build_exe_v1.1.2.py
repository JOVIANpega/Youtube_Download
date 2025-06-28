#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 影片下載器 V1.1.2 打包腳本
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
            print(f"pip install {package}")
        return False
    
    print("✅ 所有依賴套件都已安裝")
    return True

def create_version_file():
    """創建版本資訊檔案"""
    version_content = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 1, 2, 0),
    prodvers=(1, 1, 2, 0),
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
         StringStruct(u'FileDescription', u'YouTube 影片下載器 V1.1.2'),
         StringStruct(u'FileVersion', u'1.1.2'),
         StringStruct(u'InternalName', u'youtube_downloader'),
         StringStruct(u'LegalCopyright', u'Copyright (c) 2024'),
         StringStruct(u'OriginalFilename', u'YouTube下載器.exe'),
         StringStruct(u'ProductName', u'YouTube 影片下載器'),
         StringStruct(u'ProductVersion', u'1.1.2')])
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
        '--onefile',
        '--windowed',
        '--name=YouTube下載器V1.1.2',
        '--version-file=version_info.txt',
        '--add-data=src/user_preferences.json;.',
        '--add-data=VERSION;.',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=yt_dlp',
        '--hidden-import=ssl',
        '--hidden-import=certifi',
        '--clean',
        'src/main_pyside.py'
    ]
    
    print(f"執行指令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return False

def main():
    """主函數"""
    print("🎯 YouTube 影片下載器 V1.1.2 打包工具")
    print("=" * 50)
    
    # 檢查依賴
    if not check_dependencies():
        print("\n❌ 請先安裝缺少的依賴套件")
        return
    
    # 打包 EXE
    if not build_exe():
        print("\n❌ 打包失敗")
        return
    
    print("\n🎉 打包完成！")
    print("\n📦 生成的檔案:")
    print("  - dist/YouTube下載器V1.1.2.exe (主程式)")
    
    print("\n🆕 V1.1.2 新功能:")
    print("  - 檔案名稱前綴功能")
    print("  - 自定義檔案命名")
    print("  - 前綴設定記憶")
    print("  - 檔案名稱清理優化")
    
    print("\n💡 檔案名稱前綴範例:")
    print("  前綴: PER-")
    print("  原始標題: Amazing Video")
    print("  最終檔案: PER-Amazing_Video.mp4")

if __name__ == "__main__":
    main() 