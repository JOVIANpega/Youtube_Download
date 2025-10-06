#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試主應用程式
檢查主程式是否能正常啟動
"""

import sys
import os
import traceback

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_import():
    """測試主程式導入"""
    print("🔍 測試主程式導入...")
    
    try:
        import main
        print("  ✅ main.py 導入成功")
        return True
    except Exception as e:
        print(f"  ❌ main.py 導入失敗: {e}")
        traceback.print_exc()
        return False

def test_ui_imports():
    """測試UI模組導入"""
    print("\n🎨 測試UI模組導入...")
    
    ui_modules = [
        ('ui_download', '下載頁面'),
        ('ui_external', '外部下載器頁面'),
        ('ui_history', '歷史記錄頁面'),
    ]
    
    passed = 0
    for module, desc in ui_modules:
        try:
            __import__(module)
            print(f"  ✅ {module} ({desc})")
            passed += 1
        except Exception as e:
            print(f"  ❌ {module} ({desc}) - {e}")
            # 顯示詳細錯誤
            traceback.print_exc()
    
    print(f"  📊 UI模組: {passed}/{len(ui_modules)} 導入成功")
    return passed == len(ui_modules)

def test_app_creation():
    """測試應用程式創建"""
    print("\n🚀 測試應用程式創建...")
    
    try:
        import main
        
        print("  正在創建應用程式實例...")
        app = main.MainApplication()
        
        print("  ✅ 應用程式實例創建成功")
        
        # 快速測試一些基本屬性
        if hasattr(app, 'root') and hasattr(app, 'notebook'):
            print("  ✅ 基本UI組件存在")
        else:
            print("  ❌ 缺少基本UI組件")
            return False
        
        # 測試字體管理器
        if hasattr(app, 'font_manager'):
            initial_size = app.font_manager.current_size
            print(f"  ✅ 字體管理器正常，當前大小: {initial_size}")
        else:
            print("  ❌ 字體管理器缺失")
            return False
        
        # 測試設定管理器
        if hasattr(app, 'settings_manager'):
            print("  ✅ 設定管理器正常")
        else:
            print("  ❌ 設定管理器缺失")
            return False
        
        # 快速關閉應用程式
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("  ✅ 應用程式測試完成")
        return True
        
    except Exception as e:
        print(f"  ❌ 應用程式創建失敗: {e}")
        traceback.print_exc()
        return False

def test_simple_gui():
    """測試簡化GUI"""
    print("\n🖥️ 測試簡化GUI...")
    
    try:
        import simple_main
        
        print("  正在創建簡化應用程式...")
        app = simple_main.SimpleApp()
        
        print("  ✅ 簡化應用程式創建成功")
        
        # 快速關閉
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("  ✅ 簡化GUI測試完成")
        return True
        
    except Exception as e:
        print(f"  ❌ 簡化GUI測試失敗: {e}")
        traceback.print_exc()
        return False

def test_dependencies():
    """測試依賴狀態"""
    print("\n📦 檢查依賴狀態...")
    
    # 必要依賴
    required = {
        'tkinter': 'GUI框架',
    }
    
    # 可選依賴
    optional = {
        'yt_dlp': '下載核心',
        'requests': 'HTTP請求',
    }
    
    print("  必要依賴:")
    required_ok = True
    for dep, desc in required.items():
        try:
            __import__(dep)
            print(f"    ✅ {dep} ({desc})")
        except ImportError:
            print(f"    ❌ {dep} ({desc}) - 缺失")
            required_ok = False
    
    print("  可選依賴:")
    optional_count = 0
    for dep, desc in optional.items():
        try:
            __import__(dep)
            print(f"    ✅ {dep} ({desc})")
            optional_count += 1
        except ImportError:
            print(f"    ⚠️ {dep} ({desc}) - 未安裝")
    
    print(f"  📊 依賴狀態: 必要 {'✅' if required_ok else '❌'}, 可選 {optional_count}/{len(optional)}")
    
    return required_ok

def main():
    """主函數"""
    print("🧪 YouTube 下載器 - 主程式測試")
    print("=" * 50)
    
    tests = [
        ("依賴檢查", test_dependencies),
        ("主程式導入", test_main_import),
        ("UI模組導入", test_ui_imports),
        ("簡化GUI測試", test_simple_gui),
        ("完整應用程式測試", test_app_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
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
    
    # 總結報告
    print(f"\n{'='*50}")
    print("📊 主程式測試結果")
    print(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    percentage = passed / total * 100
    print(f"\n📈 總計: {passed}/{total} 通過 ({percentage:.1f}%)")
    
    # 給出建議
    if passed == total:
        print("🎉 所有測試通過！主程式完全可用")
        print("\n🚀 推薦啟動方式:")
        print("  python start.py      # 一鍵啟動")
        print("  python main.py       # 直接啟動完整版")
        
    elif passed >= 3:
        print("✅ 核心功能正常！應用程式基本可用")
        print("\n🚀 可用啟動方式:")
        if any(name == "簡化GUI測試" and result for name, result in results):
            print("  python simple_main.py # 簡化版（推薦）")
        if any(name == "完整應用程式測試" and result for name, result in results):
            print("  python main.py       # 完整版")
        print("  python start.py      # 智能選擇")
        
    else:
        print("⚠️ 多個核心功能有問題")
        print("\n🔧 建議修復步驟:")
        print("  1. python check_dependencies.py  # 檢查環境")
        print("  2. python install_deps.py        # 安裝依賴")
        print("  3. python quick_test.py          # 快速測試")
    
    # 特別提示
    if not any(name == "UI模組導入" and result for name, result in results):
        print("\n⚠️ UI模組導入失敗，可能的原因:")
        print("  - 缺少某些依賴模組")
        print("  - 模組間循環導入")
        print("  - 路徑配置問題")
    
    return passed >= 3

if __name__ == "__main__":
    try:
        success = main()
        
        print(f"\n{'='*50}")
        if success:
            print("🎯 主程式測試完成，應用程式可以使用！")
        else:
            print("🔧 主程式存在問題，需要修復")
        
    except Exception as e:
        print(f"💥 測試過程發生嚴重錯誤: {e}")
        traceback.print_exc()
    
    input("\n按 Enter 鍵退出...")