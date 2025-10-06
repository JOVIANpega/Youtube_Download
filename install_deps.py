#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安裝依賴腳本
"""

import subprocess
import sys

def install_package(package):
    """安裝套件"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """主函數"""
    print("YouTube 下載器 - 依賴安裝")
    print("=" * 40)
    
    packages = [
        "yt-dlp>=2023.12.30",
        "requests>=2.31.0",
    ]
    
    for package in packages:
        print(f"正在安裝 {package}...")
        if install_package(package):
            print(f"✓ {package} 安裝成功")
        else:
            print(f"✗ {package} 安裝失敗")
            
    print("\n安裝完成！")
    print("現在可以運行: python run.py")

if __name__ == "__main__":
    main()