#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
錯誤診斷腳本
幫助診斷和解決問題
"""

import sys
import os
import traceback

def diagnose_environment():
    """診斷環境"""
    print("🔍 環境診斷")
    print("=" * 40)
    
    # Python 版本
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 版本過低，需要 3.7+")
        return False
    else:
        print("✅ Python 版本符合要求")
    
    # Tkinter 檢查
    try:
        import tkinter as tk
        print("✅ Tkinter 可用")
    except ImportError as e:
        print(f"❌ Tkinter 不可用: {e}")
        return False
    
    # 工作目錄
    print(f"工作目錄: {os.getcwd()}")
    
    # 檢查關鍵檔案
    key_files = [
        'constants.py',
        'version_info.py',
        'minimal_safe.py'
    ]
    
    for file in key_files:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
    
    return True

def test_imports():
    """測試導入"""
    print("\n🔍 測試模組導入")
    print("=" * 40)
    
    # 測試基本模組
    modules = [
        'constants',
        'version_info'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} 導入成功")
        except Exception as e:
            print(f"❌ {module} 導入失敗: {e}")
            traceback.print_exc()

def main():
    """主函數"""
    print("🔧 YouTube 下載器 - 錯誤診斷")
    print("=" * 50)
    
    # 環境診斷
    env_ok = diagnose_environment()
    
    if env_ok:
        # 測試導入
        test_imports()
        
        print("\n🚀 建議嘗試:")
        print("  python minimal_safe.py    # 最小安全版")
        print("  python simple_main.py     # 簡化版")
    else:
        print("\n❌ 環境有問題，請檢查 Python 安裝")
    
    input("\n按 Enter 鍵退出...")

if __name__ == "__main__":
    main()