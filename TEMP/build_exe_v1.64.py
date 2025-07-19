#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import PyInstaller.__main__

# 確保當前工作目錄是腳本所在的目錄
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 版本號
VERSION = "1.64"
APP_NAME = f"youtube_downloader_v{VERSION}"

# 創建臨時目錄
build_dir = "build_temp"
if not os.path.exists(build_dir):
    os.makedirs(build_dir)

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

# 打包參數
PyInstaller.__main__.run([
    "src/tabbed_gui_demo.py",  # 主腳本
    "--name=%s" % APP_NAME,
    "--onefile",
    "--windowed",
    "--add-data=ffmpeg_bin;ffmpeg_bin",  # 添加ffmpeg
    "--version-file=%s" % os.path.join(build_dir, "version_info.txt"),
    "--distpath=./dist",
    "--workpath=%s" % build_dir,
    "--clean",
])

print(f"\n打包完成！執行檔位於 dist/{APP_NAME}.exe") 