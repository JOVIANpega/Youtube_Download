#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷腳本
逐步檢查每個模組的導入問題
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_file_exists():
    """檢查檔案是否存在"""
    print("📁 檢查檔案存在性...")
    
    required_files = [
        'main.py',
        'constants.py', 
        'version_info.py',
        'logging_config.py',
        'ui_download.py',
        'ui_external.py', 
        'ui_history.py',
        'simple_main.py',
        'utils/validators.py',
        'utils/ui_fonts.py',
        'utils/path_utils.py',
        'services/settings.py',
        'services/history_store.py',
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 檔案不存在")
            missing.append(file)
    
    if missing:
        print(f"\n❌ 缺少檔案: {missing}")
        return False
    else:
        print(f"\n✅ 所有必要檔案都存在")
        return True

def check_basic_imports():
    """檢查基本導入"""
    print("\n🔍 檢查基本模組導入...")
    
    modules = [
        'constants',
        'version_info', 
        'logging_config',
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            return False
    
    return True

def check_utils_imports():
    """檢查工具模組導入"""
    print("\n🛠️ 檢查工具模組導入...")
    
    utils_modules = [
        'utils.validators',
        'utils.path_utils',
        'utils.ui_fonts',
    ]
    
    for module in utils_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def check_services_imports():
    """檢查服務模組導入"""
    print("\n🔧 檢查服務模組導入...")
    
    services_modules = [
        'services.settings',
        'services.history_store',
    ]
    
    for module in services_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def check_ui_imports():
    """檢查UI模組導入"""
    print("\n🎨 檢查UI模組導入...")
    
    ui_modules = [
        'ui_download',
        'ui_external', 
        'ui_history',
    ]
    
    for module in ui_modules:
        try:
            print(f"正在導入 {module}...")
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def check_main_import():
    """檢查主程式導入"""
    print("\n🚀 檢查主程式導入...")
    
    try:
        print("正在導入 simple_main...")
        import simple_main
        print("✅ simple_main 導入成功")
        
        print("正在導入 main...")
        import main
        print("✅ main 導入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 主程式導入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_gui():
    """測試簡化GUI"""
    print("\n🖥️ 測試簡化GUI...")
    
    try:
        import tkinter as tk
        print("✅ Tkinter 可用")
        
        import simple_main
        print("✅ simple_main 導入成功")
        
        app = simple_main.SimpleApp()
        print("✅ 簡化應用程式創建成功")
        
        # 快速關閉
        app.root.after(50, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("✅ 簡化GUI測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 簡化GUI測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主診斷函數"""
    print("🔍 YouTube 下載器 - 診斷模式")
    print("=" * 50)
    
    steps = [
        ("檔案存在性檢查", check_file_exists),
        ("基本模組導入", check_basic_imports),
        ("工具模組導入", check_utils_imports),
        ("服務模組導入", check_services_imports),
        ("UI模組導入", check_ui_imports),
        ("主程式導入", check_main_import),
        ("簡化GUI測試", test_simple_gui),
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        
        try:
            result = step_func()
            results.append((step_name, result))
            
            if result:
                print(f"✅ {step_name} - 通過")
            else:
                print(f"❌ {step_name} - 失敗")
                break  # 如果某步失敗，停止後續測試
                
        except Exception as e:
            print(f"💥 {step_name} - 異常: {e}")
            results.append((step_name, False))
            break
    
    # 診斷報告
    print(f"\n{'='*50}")
    print("📋 診斷報告")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for step_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{step_name:20} : {status}")
    
    print(f"\n📊 診斷結果: {passed}/{total} 步驟通過")
    
    if passed == total:
        print("🎉 所有診斷通過！應用程式完全正常！")
        print("\n🚀 可以安全啟動:")
        print("  python start.py")
        print("  python main.py")
        
    elif passed >= 6:  # 至少前6步通過
        print("✅ 核心功能正常！基本可用！")
        print("\n🚀 建議啟動方式:")
        print("  python simple_main.py  # 簡化版")
        print("  python start.py        # 智能選擇")
        
    else:
        print("⚠️ 發現問題，需要修復")
        print("\n🔧 可能的解決方案:")
        
        if passed < 2:
            print("  - 檢查檔案完整性")
            print("  - 確認所有檔案都已創建")
        elif passed < 4:
            print("  - 檢查模組導入路徑")
            print("  - 確認 Python 環境正常")
        else:
            print("  - 檢查 Tkinter 安裝")
            print("  - 嘗試重新啟動")
    
    return passed >= 6

if __name__ == "__main__":
    try:
        success = main()
        
        print(f"\n{'='*50}")
        if success:
            print("🎯 診斷完成！應用程式可以使用！")
        else:
            print("🔧 診斷發現問題，需要修復")
            
    except Exception as e:
        print(f"\n💥 診斷過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按 Enter 鍵退出...")