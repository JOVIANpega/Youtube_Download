#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多平台影片下載器 - 簡易打包腳本
"""

import os
import sys
import subprocess
import shutil
import time

# 確保當前目錄是腳本所在目錄
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 版本信息
VERSION = "1.71"
APP_NAME = "多平台影片下載器"

# 安裝必要的套件
def install_package(package):
    print(f"正在安裝 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        return True
    except Exception as e:
        print(f"安裝 {package} 失敗: {str(e)}")
        return False

# 確保PyInstaller已安裝
if install_package("PyInstaller"):
    print("PyInstaller 已安裝")
else:
    print("無法安裝 PyInstaller，打包過程無法繼續")
    sys.exit(1)

# 創建輸出目錄
output_dir = "dist"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 清理舊的打包文件
for file in os.listdir(output_dir):
    file_path = os.path.join(output_dir, file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print(f"無法刪除 {file_path}: {e}")

print(f"開始打包 {APP_NAME} v{VERSION}...")

# 準備PyInstaller基本命令
pyinstaller_base_cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--icon", "assets/icon.ico",
    "--add-data", "assets;assets",
    "--add-data", "ffmpeg_bin;ffmpeg_bin",
    "--add-data", "VERSION;.",
    "--paths", "src"  # 添加src目錄到模塊搜索路徑
]

# 打包無控制台版本
try:
    print("打包無控制台版本...")
    cmd = pyinstaller_base_cmd + [
        "--noconsole",
        "--name", f"YT_Downloader_v{VERSION}",
        "simple_start.py"
    ]
    subprocess.check_call(cmd)
    print("無控制台版本打包完成")
except Exception as e:
    print(f"打包無控制台版本時出錯: {e}")
    import traceback
    traceback.print_exc()

# 打包帶控制台版本
try:
    print("打包帶控制台版本...")
    cmd = pyinstaller_base_cmd + [
        "--name", f"YT_Downloader_Console_v{VERSION}",
        "simple_start.py"
    ]
    subprocess.check_call(cmd)
    print("帶控制台版本打包完成")
except Exception as e:
    print(f"打包帶控制台版本時出錯: {e}")
    import traceback
    traceback.print_exc()

print("打包過程完成")
print(f"輸出文件位於 {os.path.abspath(output_dir)} 目錄")
input("按Enter鍵退出...") 