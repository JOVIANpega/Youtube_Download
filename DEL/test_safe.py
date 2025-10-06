#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試安全版本
確保沒有依賴問題
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_safe_version():
    """測試安全版本"""
    print("🧪 測試安全版本")
    print("=" * 30)
    
    # 1. 測試基本模組
    print("1. 測試基本模組...")
    try:
        import constants
        print(f"   ✅ constants: {constants.APP_TITLE}")
    except Exception as e:
        print(f"   ❌ constants: {e}")
        return False
    
    try:
        import version_info
        print(f"   ✅ version_info: {version_info.VERSION}")
    except Exception as e:
        print(f"   ❌ version_info: {e}")
        return False
    
    # 2. 測試安全版主程式
    print("\n2. 測試安全版主程式...")
    try:
        import main_safe
        print("   ✅ main_safe 導入成功")
        
        # 創建應用程式實例
        app = main_safe.SafeMainApplication()
        print("   ✅ 安全版應用程式創建成功")
        
        # 快速測試
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("   ✅ 安全版測試完成")
        
    except Exception as e:
        print(f"   ❌ 安全版測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 測試修復版主程式
    print("\n3. 測試修復版主程式...")
    try:
        import main_fixed
        print("   ✅ main_fixed 導入成功")
        
        # 創建應用程式實例
        app = main_fixed.MainApplicationFixed()
        print("   ✅ 修復版應用程式創建成功")
        
        # 快速測試
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("   ✅ 修復版測試完成")
        
    except Exception as e:
        print(f"   ❌ 修復版測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """主函數"""
    try:
        success = test_safe_version()
        
        print(f"\n{'='*30}")
        if success:
            print("🎉 所有安全版本測試通過！")
            print("\n🚀 可以安全使用:")
            print("  python main_safe.py      # 安全版（無依賴問題）")
            print("  python main_fixed.py     # 修復版（基本功能）")
            print("  python simple_main.py    # 簡化版（最小功能）")
        else:
            print("❌ 部分測試失敗")
            
    except Exception as e:
        print(f"💥 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按 Enter 鍵退出...")

if __name__ == "__main__":
    main()