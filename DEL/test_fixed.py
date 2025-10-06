#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復版應用程式
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🧪 測試修復版應用程式")
    print("=" * 40)
    
    # 1. 基本檢查
    print("1. 檢查基本環境...")
    
    version = sys.version_info
    print(f"   Python: {version.major}.{version.minor}.{version.micro}")
    
    try:
        import tkinter as tk
        print("   ✅ Tkinter 可用")
    except ImportError:
        print("   ❌ Tkinter 不可用")
        return False
    
    # 2. 檢查基本模組
    print("\n2. 檢查基本模組...")
    
    try:
        import constants
        print(f"   ✅ constants: {constants.APP_TITLE}")
    except Exception as e:
        print(f"   ❌ constants: {e}")
        return False
    
    try:
        from utils.validators import URLValidator
        print("   ✅ utils.validators")
    except Exception as e:
        print(f"   ❌ utils.validators: {e}")
        return False
    
    try:
        from utils.ui_fonts import FontManager
        print("   ✅ utils.ui_fonts")
    except Exception as e:
        print(f"   ❌ utils.ui_fonts: {e}")
        return False
    
    try:
        from services.settings import SettingsManager
        print("   ✅ services.settings")
    except Exception as e:
        print(f"   ❌ services.settings: {e}")
        return False
    
    # 3. 檢查簡化UI模組
    print("\n3. 檢查簡化UI模組...")
    
    try:
        from ui_download_simple import DownloadTabSimple
        print("   ✅ ui_download_simple")
    except Exception as e:
        print(f"   ❌ ui_download_simple: {e}")
        return False
    
    try:
        from ui_external import ExternalTab
        print("   ✅ ui_external")
    except Exception as e:
        print(f"   ❌ ui_external: {e}")
        return False
    
    # 4. 測試修復版主程式
    print("\n4. 測試修復版主程式...")
    
    try:
        import main_fixed
        print("   ✅ main_fixed 導入成功")
        
        print("   正在創建應用程式...")
        app = main_fixed.MainApplicationFixed()
        print("   ✅ 應用程式創建成功")
        
        # 快速測試
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("   ✅ 應用程式測試完成")
        
    except Exception as e:
        print(f"   ❌ 修復版主程式測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. 總結
    print("\n📊 測試結果:")
    print("✅ 所有測試通過！")
    print("\n🚀 可以使用:")
    print("  python main_fixed.py    # 修復版（推薦）")
    print("  python simple_main.py   # 簡化版")
    print("  python start.py         # 智能啟動")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎯 修復版測試成功！")
        else:
            print("\n🔧 測試失敗")
    except Exception as e:
        print(f"\n💥 測試異常: {e}")
    
    input("\n按 Enter 鍵退出...")