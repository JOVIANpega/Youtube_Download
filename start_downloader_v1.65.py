#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube下載器啟動腳本 V1.65
此腳本用於啟動YouTube下載器，並自動安裝所需依賴
"""

import os
import sys
import subprocess
import importlib.util

def check_module(module_name):
    """檢查模組是否已安裝"""
    return importlib.util.find_spec(module_name) is not None

def install_module(module_name):
    """安裝模組"""
    print(f"正在安裝 {module_name}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

def main():
    """主函數"""
    # 檢查並安裝必要的模組
    required_modules = ["PySide6", "yt-dlp", "requests", "certifi"]
    for module in required_modules:
        if not check_module(module):
            install_module(module)
    
    # 確保當前工作目錄是腳本所在的目錄
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 啟動下載器
    print("正在啟動 YouTube下載器 V1.65...")
    try:
        from src import tabbed_gui_demo
        tabbed_gui_demo.main()
    except Exception as e:
        print(f"啟動失敗: {e}")
        input("按Enter鍵退出...")

if __name__ == "__main__":
    main() 