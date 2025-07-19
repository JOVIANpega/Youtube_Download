#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多平台影片下載器 - 構建EXE腳本
版本：1.71
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

# 確保當前目錄是腳本所在目錄
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 版本信息
VERSION = "1.71"
APP_NAME = "多平台影片下載器"

# 構建目錄
BUILD_DIR = "build_temp"
DIST_DIR = os.path.join(BUILD_DIR, "dist")
SPEC_DIR = os.path.join(BUILD_DIR, "spec")

# 確保構建目錄存在
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(SPEC_DIR, exist_ok=True)

# 確保assets目錄存在
if not os.path.exists("assets"):
    os.makedirs("assets", exist_ok=True)
    print("已創建assets目錄")

# 確保assets目錄中有icon.ico文件
if not os.path.exists(os.path.join("assets", "icon.ico")):
    print("警告: assets/icon.ico不存在，將使用默認圖標")
    # 使用默認圖標路徑
    icon_path = ""
else:
    icon_path = "assets/icon.ico"

# 更新版本信息文件
with open(os.path.join(BUILD_DIR, "version_info.txt"), "w", encoding="utf-8") as f:
    f.write(f"Version: {VERSION}\n")
    f.write(f"Build Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

print(f"開始構建 {APP_NAME} v{VERSION}...")

# 檢查必要的套件
required_packages = ["PyInstaller", "PySide6", "yt-dlp"]

def install_package(package):
    """安裝套件"""
    print(f"正在安裝 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        return True
    except Exception as e:
        print(f"安裝 {package} 失敗: {str(e)}")
        return False

# 安裝必要的套件
for package in required_packages:
    try:
        __import__(package.lower().replace("-", "_"))
    except ImportError:
        if not install_package(package):
            print(f"無法安裝 {package}，構建過程可能會失敗")
            time.sleep(3)

# 清理舊的構建文件
print("清理舊的構建文件...")
for dir_to_clean in [DIST_DIR, SPEC_DIR]:
    if os.path.exists(dir_to_clean):
        try:
            shutil.rmtree(dir_to_clean)
            os.makedirs(dir_to_clean, exist_ok=True)
            print(f"已清理 {dir_to_clean}")
        except Exception as e:
            print(f"清理 {dir_to_clean} 失敗: {str(e)}")

# 準備數據文件
data_files = []
# 添加assets目錄（如果存在）
if os.path.exists("assets") and os.listdir("assets"):
    data_files.append(("assets", "assets"))
# 添加ffmpeg_bin目錄（如果存在）
if os.path.exists("ffmpeg_bin"):
    data_files.append(("ffmpeg_bin", "ffmpeg_bin"))
# 添加VERSION文件（如果存在）
if os.path.exists("VERSION"):
    data_files.append(("VERSION", "."))
# 添加版本信息文件
version_info_path = os.path.join(BUILD_DIR, "version_info.txt")
if os.path.exists(version_info_path):
    data_files.append((version_info_path, BUILD_DIR))

# 構建啟動器
print("開始構建啟動器...")
try:
    # 構建命令基本部分
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--distpath", DIST_DIR,
        "--specpath", SPEC_DIR,
    ]
    
    # 添加圖標（如果存在）
    if icon_path:
        pyinstaller_cmd.extend(["--icon", icon_path])
    
    # 添加數據文件
    for src, dst in data_files:
        pyinstaller_cmd.extend(["--add-data", f"{src};{dst}"])
    
    # 添加隱藏導入
    hidden_imports = ["PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets"]
    for imp in hidden_imports:
        pyinstaller_cmd.extend(["--hidden-import", imp])
    
    # 構建簡易版啟動器（無控制台）
    simple_cmd = pyinstaller_cmd.copy()
    simple_cmd.extend([
        "--name", f"start_v{VERSION}",
        "--noconsole",
        "start_v1.71.py"
    ])
    print("執行命令:", " ".join(simple_cmd))
    subprocess.check_call(simple_cmd)
    print("簡易版啟動器構建完成")

    # 構建完整版啟動器（帶控制台）
    full_cmd = pyinstaller_cmd.copy()
    full_cmd.extend([
        "--name", f"start_downloader_v{VERSION}",
        "start_downloader_v1.71.py"
    ])
    print("執行命令:", " ".join(full_cmd))
    subprocess.check_call(full_cmd)
    print("完整版啟動器構建完成")

    print("構建過程完成")
    
    # 創建發布包
    release_dir = f"YT_Downloader_v{VERSION}"
    release_path = os.path.join(BUILD_DIR, release_dir)
    
    # 清理舊的發布目錄
    if os.path.exists(release_path):
        shutil.rmtree(release_path)
    
    # 創建發布目錄結構
    os.makedirs(release_path, exist_ok=True)
    
    # 複製文件到發布目錄
    print(f"正在創建發布包 {release_dir}...")
    
    # 複製EXE文件
    simple_exe = os.path.join(DIST_DIR, f"start_v{VERSION}.exe")
    full_exe = os.path.join(DIST_DIR, f"start_downloader_v{VERSION}.exe")
    
    if os.path.exists(simple_exe):
        shutil.copy(simple_exe, release_path)
    else:
        print(f"警告: 找不到簡易版啟動器 {simple_exe}")
        
    if os.path.exists(full_exe):
        shutil.copy(full_exe, release_path)
    else:
        print(f"警告: 找不到完整版啟動器 {full_exe}")
    
    # 複製文檔
    doc_files = ["README.md", "LICENSE", f"RELEASE_NOTES_V{VERSION}.md"]
    for doc in doc_files:
        if os.path.exists(doc):
            shutil.copy(doc, release_path)
        else:
            print(f"警告: 找不到文檔 {doc}")
    
    # 創建ZIP文件
    print("正在創建ZIP文件...")
    zip_path = os.path.join(BUILD_DIR, f"YT_Downloader_v{VERSION}")
    if os.path.exists(f"{zip_path}.zip"):
        os.remove(f"{zip_path}.zip")
    
    shutil.make_archive(zip_path, 'zip', BUILD_DIR, release_dir)
    
    print(f"發布包已創建: {zip_path}.zip")
    
except Exception as e:
    print(f"構建過程中發生錯誤: {str(e)}")
    import traceback
    traceback.print_exc()

print("構建腳本執行完成")
input("按Enter鍵退出...") 