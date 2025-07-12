#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多平台影片下載器 - 簡易啟動腳本
"""

import os
import sys
import subprocess

# 添加當前目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加src目錄到路徑
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

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