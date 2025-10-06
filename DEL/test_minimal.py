#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小化測試
測試最基本的功能是否正常
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic():
    """基本測試"""
    print("🔍 基本功能測試")
    
    # 1. 測試 Python 版本
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 版本過低")
        return False
    
    # 2. 測試 Tkinter
    try:
        import tkinter as tk
        print("✅ Tkinter 可用")
    except ImportError:
        print("❌ Tkinter 不可用")
        return False
    
    # 3. 測試基本模組
    try:
        import constants
        print(f"✅ constants: {constants.APP_TITLE}")
    except Exception as e:
        print(f"❌ constants 失敗: {e}")
        return False
    
    try:
        import version_info
        print(f"✅ version_info: {version_info.VERSION}")
    except Exception as e:
        print(f"❌ version_info 失敗: {e}")
        return False
    
    # 4. 測試簡化GUI
    try:
        print("測試簡化GUI...")
        import simple_main
        
        app = simple_main.SimpleApp()
        print("✅ 簡化GUI創建成功")
        
        # 快速關閉
        app.root.after(50, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("✅ 簡化GUI測試完成")
        
    except Exception as e:
        print(f"❌ 簡化GUI失敗: {e}")
        return False
    
    return True

def test_full_app():
    """測試完整應用程式"""
    print("\n🚀 完整應用程式測試")
    
    try:
        print("導入主程式...")
        import main
        print("✅ 主程式導入成功")
        
        print("創建應用程式實例...")
        app = main.MainApplication()
        print("✅ 應用程式創建成功")
        
        # 快速測試
        if hasattr(app, 'root') and hasattr(app, 'notebook'):
            print("✅ 基本組件正常")
        else:
            print("❌ 缺少基本組件")
            return False
        
        # 快速關閉
        app.root.after(50, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("✅ 完整應用程式測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 完整應用程式失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🧪 最小化測試")
    print("=" * 30)
    
    # 基本測試
    if not test_basic():
        print("\n❌ 基本測試失敗")
        return False
    
    print("\n✅ 基本測試通過")
    
    # 完整應用程式測試
    if test_full_app():
        print("\n🎉 所有測試通過！")
        print("\n🚀 可以使用:")
        print("  python start.py")
        print("  python main.py")
        print("  python simple_main.py")
        return True
    else:
        print("\n⚠️ 完整應用程式有問題")
        print("\n🚀 可以使用簡化版:")
        print("  python simple_main.py")
        return False

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n{'='*30}")
        if success:
            print("🎯 測試完成，應用程式可用！")
        else:
            print("🔧 部分功能需要修復")
    except Exception as e:
        print(f"💥 測試失敗: {e}")
    
    input("\n按 Enter 鍵退出...")