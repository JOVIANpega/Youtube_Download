#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多平台影片下載器 - 啟動腳本
"""

import os
import sys
import subprocess
import importlib.util
import time

# 添加當前目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加src目錄到路徑
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 檢查並安裝必要的套件
required_packages = ["yt-dlp", "PySide6"]

def install_package(package):
    """安裝套件"""
    print(f"正在安裝 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except Exception as e:
        print(f"安裝 {package} 失敗: {str(e)}")
        return False

# 安裝必要的套件
for package in required_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        if not install_package(package):
            print(f"無法安裝 {package}，程式可能無法正常運行")
            time.sleep(3)

# 啟動主程式
try:
    from src.tabbed_gui_demo import main
    main()
except ImportError as e:
    print(f"導入主程式失敗: {str(e)}")
    print("嘗試直接執行主程式...")
    try:
        # 直接執行主程式檔案
        script_path = os.path.join(src_dir, "tabbed_gui_demo.py")
        if os.path.exists(script_path):
            subprocess.call([sys.executable, script_path])
        else:
            print(f"找不到主程式檔案: {script_path}")
    except Exception as e:
        print(f"執行主程式時發生錯誤: {str(e)}")
    
    # 等待用戶輸入，避免視窗立即關閉
    input("按Enter鍵退出...") 