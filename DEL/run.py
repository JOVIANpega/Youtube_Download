#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的啟動腳本
"""

import sys
import os

# 添加當前目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_dependencies():
    """檢查依賴"""
    missing_deps = []
    
    try:
        import tkinter
        print("✓ tkinter 可用")
    except ImportError:
        missing_deps.append("tkinter")
        
    try:
        import yt_dlp
        print("✓ yt-dlp 可用")
    except ImportError:
        missing_deps.append("yt-dlp")
        print("✗ yt-dlp 未安裝，請運行: pip install yt-dlp")
        
    try:
        import requests
        print("✓ requests 可用")
    except ImportError:
        missing_deps.append("requests")
        print("✗ requests 未安裝，請運行: pip install requests")
        
    return missing_deps

def main():
    """主函數"""
    print("YouTube 下載器啟動檢查")
    print("=" * 40)
    
    # 檢查依賴
    missing = check_dependencies()
    
    if missing:
        print(f"\n缺少依賴: {', '.join(missing)}")
        print("請先安裝必要的依賴套件")
        return False
        
    print("\n所有依賴檢查通過")
    
    # 嘗試啟動主程式
    try:
        print("正在啟動主程式...")
        import main
        main.main()
        return True
    except Exception as e:
        print(f"啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("按 Enter 鍵退出...")