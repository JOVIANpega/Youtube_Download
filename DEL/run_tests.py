#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
運行所有測試
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_dependency_check():
    """運行依賴檢查"""
    print("🔍 檢查依賴...")
    try:
        import check_dependencies
        return check_dependencies.main()
    except Exception as e:
        print(f"❌ 依賴檢查失敗: {e}")
        return False

def run_basic_tests():
    """運行基本測試"""
    print("\n🧪 運行基本測試...")
    try:
        import test_basic
        return test_basic.main()
    except Exception as e:
        print(f"❌ 基本測試失敗: {e}")
        return False

def run_simple_gui():
    """運行簡化 GUI 測試"""
    print("\n🖥️  測試簡化 GUI...")
    try:
        import simple_main
        print("✅ 簡化 GUI 可以啟動")
        print("   (視窗將自動關閉)")
        
        # 創建測試實例但不運行主循環
        app = simple_main.SimpleApp()
        app.root.after(100, app.root.quit)  # 100ms 後關閉
        app.root.mainloop()
        app.root.destroy()
        
        return True
    except Exception as e:
        print(f"❌ 簡化 GUI 測試失敗: {e}")
        return False

def test_main_app():
    """測試主應用程式"""
    print("\n🚀 測試主應用程式...")
    try:
        # 只測試導入，不實際運行
        import main
        print("✅ 主應用程式模組可以導入")
        
        # 測試創建應用程式實例
        print("   正在創建應用程式實例...")
        app = main.MainApplication()
        print("✅ 應用程式實例創建成功")
        
        # 快速關閉
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("✅ 主應用程式測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 主應用程式測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("YouTube 下載器 - 完整測試套件")
    print("=" * 50)
    
    tests = [
        ("依賴檢查", run_dependency_check),
        ("基本功能測試", run_basic_tests),
        ("簡化 GUI 測試", run_simple_gui),
        ("主應用程式測試", test_main_app),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} 通過")
            else:
                print(f"❌ {test_name} 失敗")
                
        except Exception as e:
            print(f"💥 {test_name} 發生異常: {e}")
            results.append((test_name, False))
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 測試結果總結")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 個測試通過")
    
    if passed == total:
        print("🎉 所有測試都通過！應用程式可以正常運行。")
        print("\n🚀 啟動方式:")
        print("   完整版: python main.py")
        print("   簡化版: python simple_main.py")
    else:
        print("⚠️  部分測試失敗，可能需要安裝依賴或修復問題。")
        print("\n🔧 建議:")
        print("   1. 運行: python install_deps.py")
        print("   2. 檢查: python check_dependencies.py")
        print("   3. 嘗試: python simple_main.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    
    print(f"\n{'='*50}")
    if success:
        print("🎯 所有測試完成，應用程式準備就緒！")
    else:
        print("🔧 需要修復一些問題才能完全運行。")
    
    input("\n按 Enter 鍵退出...")