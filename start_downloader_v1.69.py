#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多平台影片下載器 V1.69
支援 YouTube, TikTok, Facebook, Instagram, Bilibili, X(Twitter)
Multi-platform Video Downloader V1.69
マルチプラットフォーム動画ダウンローダー V1.69
멀티 플랫폼 비디오 다운로더 V1.69
"""

import os
import sys
import subprocess
import time
import traceback
import ssl
import urllib.request
import importlib.util
from pathlib import Path

# 設定工作目錄
if getattr(sys, 'frozen', False):
    # 如果是打包後的執行檔
    os.chdir(os.path.dirname(sys.executable))
else:
    # 如果是直接執行 Python 腳本
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 檢查 yt-dlp 是否已安裝
def check_ytdlp():
    try:
        import yt_dlp
        return True
    except ImportError:
        return False

# 安裝 yt-dlp
def install_ytdlp():
    print("正在安裝 yt-dlp...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])

# 主程式
def main():
    # 檢查並安裝 yt-dlp
    if not check_ytdlp():
        install_ytdlp()
    
    print("正在啟動多平台影片下載器 V1.69...")
    
    # 將 src 目錄添加到 Python 路徑
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    sys.path.insert(0, src_path)
    
    # 導入主程式
    try:
        from tabbed_gui_demo import main as start_app
        start_app()
    except Exception as e:
        print(f"啟動失敗: {str(e)}")
        print("堆疊追蹤:")
        traceback.print_exc()
        input("按 Enter 鍵退出...")

if __name__ == "__main__":
    main() 