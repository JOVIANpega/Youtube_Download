#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube下載器快速打包腳本 V1.64
此腳本用於快速打包YouTube下載器，不需要安裝PyInstaller
"""

import os
import sys
import subprocess

def main():
    """主函數"""
    print("YouTube下載器 V1.64 快速打包工具")
    print("=" * 40)
    
    # 確保當前工作目錄是腳本所在的目錄
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 檢查是否已安裝PyInstaller
    try:
        subprocess.check_call([sys.executable, "-c", "import PyInstaller"])
    except subprocess.CalledProcessError:
        print("正在安裝PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 執行打包腳本
    print("正在執行打包腳本...")
    subprocess.check_call([sys.executable, "build_exe_v1.64.py"])
    
    print("=" * 40)
    print("打包完成！")
    input("按Enter鍵退出...")

if __name__ == "__main__":
    main() 