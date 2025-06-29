#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube 下載器構建腳本 V1.45
自動下載 FFmpeg 功能版本
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def is_tool_available(name):
    """檢查指定的命令行工具是否可用"""
    try:
        subprocess.run([name, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except:
        return False

def install_pyinstaller():
    """安裝 PyInstaller"""
    print("安裝 PyInstaller...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)

def install_dependencies():
    """安裝依賴套件"""
    print("安裝依賴套件...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)

def build_exe():
    """構建可執行檔"""
    print("開始構建可執行檔...")
    
    # 確定圖標路徑
    icon_path = ""
    if os.path.exists("icon.ico"):
        icon_path = "icon.ico"
    elif os.path.exists("icon.png"):
        icon_path = "icon.png"
    
    # 構建命令
    cmd = [
        'pyinstaller',
        '--noconfirm',
        '--onedir',
        '--windowed',
        '--clean',
        '--name', 'YouTube下載器_V1.45',
        '--add-data', 'VERSION;.',
        '--add-data', 'user_preferences.json;.',
    ]
    
    # 添加圖標
    if icon_path:
        cmd.extend(['--icon', icon_path])
    
    # 添加主程式
    cmd.append('src/main_pyside.py')
    
    # 執行構建命令
    subprocess.run(cmd, check=True)
    
    print("構建完成！")

def copy_additional_files():
    """複製額外文件到 dist 目錄"""
    print("複製額外文件...")
    
    dist_dir = Path("dist/YouTube下載器_V1.45")
    os.makedirs(dist_dir, exist_ok=True)
    
    # 複製版本文件
    shutil.copy2("VERSION", dist_dir)
    
    # 複製用戶偏好設定文件
    if os.path.exists("user_preferences.json"):
        shutil.copy2("user_preferences.json", dist_dir)
    
    # 複製說明文件
    for doc_file in ["README.md", "使用說明.md", "執行說明.md", "RELEASE_NOTES_V1.45.md"]:
        if os.path.exists(doc_file):
            shutil.copy2(doc_file, dist_dir)
    
    # 創建 ffmpeg_bin 目錄
    os.makedirs(dist_dir / "ffmpeg_bin", exist_ok=True)
    
    print("文件複製完成！")

def create_zip():
    """創建 ZIP 壓縮檔"""
    print("創建 ZIP 壓縮檔...")
    
    dist_dir = Path("dist/YouTube下載器_V1.45")
    output_zip = f"YouTube下載器_V1.45_{platform.system()}.zip"
    
    # 檢查操作系統
    if platform.system() == "Windows":
        # Windows 使用 PowerShell 的 Compress-Archive
        try:
            subprocess.run([
                'powershell', '-Command',
                f'Compress-Archive -Path "{dist_dir}/*" -DestinationPath "{output_zip}" -Force'
            ], check=True)
            print(f"ZIP 壓縮檔已創建: {output_zip}")
        except:
            print("無法創建 ZIP 壓縮檔，請手動壓縮 dist 目錄")
    else:
        # Linux/macOS 使用 zip 命令
        try:
            subprocess.run(['zip', '-r', output_zip, dist_dir.name], cwd='dist', check=True)
            print(f"ZIP 壓縮檔已創建: {output_zip}")
        except:
            print("無法創建 ZIP 壓縮檔，請手動壓縮 dist 目錄")

def main():
    """主函數"""
    print("YouTube 下載器構建腳本 V1.45")
    print("============================")
    
    # 檢查 PyInstaller
    if not is_tool_available('pyinstaller'):
        install_pyinstaller()
    
    # 安裝依賴套件
    install_dependencies()
    
    # 構建可執行檔
    build_exe()
    
    # 複製額外文件
    copy_additional_files()
    
    # 創建 ZIP 壓縮檔
    create_zip()
    
    print("構建過程完成！")
    print(f"可執行檔位於: dist/YouTube下載器_V1.45/YouTube下載器_V1.45{'.exe' if platform.system() == 'Windows' else ''}")

if __name__ == "__main__":
    main() 