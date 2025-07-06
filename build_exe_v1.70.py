#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多平台影片下載器打包腳本 V1.70
此腳本用於打包多平台影片下載器，並自動清理臨時檔案
"""

import os
import sys
import shutil
import glob
import time
import PyInstaller.__main__

def clean_temp_files(directory):
    """清理指定目錄中的臨時檔案"""
    print(f"正在清理臨時檔案: {directory}")
    
    # 要清理的檔案類型
    patterns = [
        "*.toc", "*.pyz", "*.pkg", "warn-*.txt", "xref-*.html",
        "*.manifest", "*.spec", "*.zip"
    ]
    
    # 遍歷並刪除符合模式的檔案
    for pattern in patterns:
        for file_path in glob.glob(os.path.join(directory, pattern)):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"已刪除: {file_path}")
            except Exception as e:
                print(f"無法刪除 {file_path}: {e}")

# 確保當前工作目錄是腳本所在的目錄
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 版本號
VERSION = "1.70"
APP_NAME = f"multi_platform_downloader_v{VERSION}"

# 創建臨時目錄
build_dir = "build_temp"
if not os.path.exists(build_dir):
    os.makedirs(build_dir)

# 清理舊的臨時檔案
clean_temp_files(build_dir)

# 複製版本信息到臨時目錄
shutil.copy("version_info.txt", os.path.join(build_dir, "version_info.txt"))

# 確保ffmpeg目錄存在
ffmpeg_dir = os.path.join(build_dir, "ffmpeg_bin")
if not os.path.exists(ffmpeg_dir):
    os.makedirs(ffmpeg_dir)

# 複製ffmpeg文件
for file in ["ffmpeg.exe", "ffprobe.exe"]:
    src_file = os.path.join("ffmpeg_bin", file)
    if os.path.exists(src_file):
        shutil.copy(src_file, os.path.join(ffmpeg_dir, file))

# 打包開始時間
start_time = time.time()
print(f"開始打包 {APP_NAME}...")

try:
    # 打包參數
    PyInstaller.__main__.run([
        "start_v1.70.py",  # 主腳本
        "--name=%s" % APP_NAME,
        "--onefile",
        "--windowed",
        "--add-data=ffmpeg_bin;ffmpeg_bin",  # 添加ffmpeg
        "--version-file=%s" % os.path.join(build_dir, "version_info.txt"),
        "--distpath=./dist",
        "--workpath=%s" % build_dir,
        "--clean",
    ])
    
    # 打包結束時間
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n打包完成！耗時: {duration:.2f} 秒")
    print(f"執行檔位於: dist/{APP_NAME}.exe")
    
    # 打包後清理臨時檔案
    print("\n正在清理打包產生的臨時檔案...")
    app_temp_dir = os.path.join(build_dir, APP_NAME)
    if os.path.exists(app_temp_dir):
        clean_temp_files(app_temp_dir)
    
except Exception as e:
    print(f"\n打包過程中發生錯誤: {e}")
    sys.exit(1) 