#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速功能測試
檢查核心模組是否正常工作
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """測試基本導入"""
    print("🔍 測試模組導入...")
    
    modules = [
        ('constants', '常數定義'),
        ('version_info', '版本資訊'),
        ('logging_config', '日誌配置'),
        ('utils.validators', 'URL驗證器'),
        ('utils.path_utils', '路徑工具'),
        ('utils.ui_fonts', '字體管理'),
        ('services.settings', '設定管理'),
        ('services.history_store', '歷史記錄'),
        ('models.types', '資料模型'),
    ]
    
    passed = 0
    for module, desc in modules:
        try:
            __import__(module)
            print(f"  ✅ {module} ({desc})")
            passed += 1
        except Exception as e:
            print(f"  ❌ {module} ({desc}) - {e}")
    
    print(f"  📊 基本模組: {passed}/{len(modules)} 導入成功")
    return passed == len(modules)

def test_url_validation():
    """測試URL驗證"""
    print("\n🌐 測試URL驗證...")
    
    try:
        from utils.validators import URLValidator
        
        tests = [
            ("https://www.youtube.com/watch?v=test", True, "YouTube"),
            ("https://youtu.be/test", True, "YouTube"),
            ("https://www.bilibili.com/video/BV123", True, "Bilibili"),
            ("invalid", False, None),
        ]
        
        passed = 0
        for url, expected_valid, expected_platform in tests:
            valid = URLValidator.is_valid_url(url)
            platform = URLValidator.detect_platform(url)
            
            if valid == expected_valid and platform == expected_platform:
                print(f"  ✅ {url[:30]}... -> {platform}")
                passed += 1
            else:
                print(f"  ❌ {url[:30]}... -> 預期:{expected_platform}, 實際:{platform}")
        
        print(f"  📊 URL驗證: {passed}/{len(tests)} 通過")
        return passed == len(tests)
        
    except Exception as e:
        print(f"  ❌ URL驗證測試失敗: {e}")
        return False

def test_settings():
    """測試設定管理"""
    print("\n⚙️ 測試設定管理...")
    
    try:
        from services.settings import SettingsManager
        
        manager = SettingsManager()
        settings = manager.load_settings()
        
        required_keys = ['font_size', 'download_path', 'window_geometry']
        missing = [k for k in required_keys if k not in settings]
        
        if not missing:
            print(f"  ✅ 設定載入成功，包含 {len(settings)} 項")
            
            # 測試保存
            manager.set_setting('test_key', 'test_value')
            new_settings = manager.load_settings()
            
            if new_settings.get('test_key') == 'test_value':
                print(f"  ✅ 設定保存功能正常")
                return True
            else:
                print(f"  ❌ 設定保存失敗")
                return False
        else:
            print(f"  ❌ 缺少必要設定: {missing}")
            return False
            
    except Exception as e:
        print(f"  ❌ 設定管理測試失敗: {e}")
        return False

def test_history():
    """測試歷史記錄"""
    print("\n📚 測試歷史記錄...")
    
    try:
        from services.history_store import HistoryStore, HistoryEntry
        
        store = HistoryStore()
        history = store.load_history()
        
        print(f"  ✅ 歷史記錄載入成功，現有 {len(history)} 條")
        
        # 測試統計
        stats = store.get_statistics()
        if 'total_downloads' in stats:
            print(f"  ✅ 統計功能正常: 總下載 {stats['total_downloads']} 個")
            return True
        else:
            print(f"  ❌ 統計功能失敗")
            return False
            
    except Exception as e:
        print(f"  ❌ 歷史記錄測試失敗: {e}")
        return False

def test_gui_basic():
    """測試基本GUI功能"""
    print("\n🖥️ 測試GUI基本功能...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # 創建測試視窗
        root = tk.Tk()
        root.withdraw()  # 隱藏視窗
        
        # 測試字體管理器
        from utils.ui_fonts import FontManager
        font_manager = FontManager(root)
        
        initial_size = font_manager.current_size
        font_manager.increase_font()
        
        if font_manager.current_size > initial_size:
            print(f"  ✅ 字體管理器正常: {initial_size} -> {font_manager.current_size}")
            
            # 測試創建基本控件
            frame = ttk.Frame(root)
            label = ttk.Label(frame, text="測試標籤")
            button = ttk.Button(frame, text="測試按鈕")
            
            print(f"  ✅ 基本控件創建成功")
            
            root.destroy()
            return True
        else:
            print(f"  ❌ 字體管理器功能異常")
            root.destroy()
            return False
            
    except Exception as e:
        print(f"  ❌ GUI基本功能測試失敗: {e}")
        return False

def test_optional_deps():
    """測試可選依賴"""
    print("\n📦 檢查可選依賴...")
    
    deps = {
        'yt-dlp': '下載核心功能',
        'requests': 'FFmpeg自動下載',
    }
    
    available = 0
    for dep, desc in deps.items():
        try:
            __import__(dep.replace('-', '_'))
            print(f"  ✅ {dep} 已安裝 ({desc})")
            available += 1
        except ImportError:
            print(f"  ⚠️ {dep} 未安裝 ({desc})")
    
    print(f"  📊 可選依賴: {available}/{len(deps)} 可用")
    
    if available == len(deps):
        print(f"  🎉 所有功能完全可用")
    elif available > 0:
        print(f"  ✅ 基本功能可用，部分功能受限")
    else:
        print(f"  ⚠️ 僅GUI功能可用，下載功能不可用")
    
    return True  # 不算失敗，因為是可選的

def main():
    """主函數"""
    print("🧪 YouTube 下載器 - 快速功能測試")
    print("=" * 50)
    
    tests = [
        ("基本模組導入", test_imports),
        ("URL驗證功能", test_url_validation),
        ("設定管理功能", test_settings),
        ("歷史記錄功能", test_history),
        ("GUI基本功能", test_gui_basic),
        ("可選依賴檢查", test_optional_deps),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name} 發生異常: {e}")
            results.append((test_name, False))
    
    # 總結
    print(f"\n{'='*50}")
    print("📊 測試結果")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
    
    total = len(results)
    percentage = passed / total * 100
    
    print(f"\n📈 總計: {passed}/{total} 通過 ({percentage:.1f}%)")
    
    if passed == total:
        print("🎉 所有測試通過！應用程式完全可用")
        print("🚀 建議運行: python start.py")
    elif passed >= 4:  # 至少4個核心功能通過
        print("✅ 核心功能正常！應用程式基本可用")
        print("💡 可能需要安裝 yt-dlp 來啟用下載功能")
        print("🚀 可以運行: python simple_main.py 或 python start.py")
    else:
        print("⚠️ 多個核心功能有問題")
        print("🔧 建議檢查 Python 環境和依賴安裝")
    
    return passed >= 4

if __name__ == "__main__":
    try:
        success = main()
        
        print(f"\n{'='*50}")
        if success:
            print("🎯 快速測試完成，應用程式可以使用！")
            
            print("\n🚀 啟動選項:")
            print("  python start.py      # 一鍵啟動（推薦）")
            print("  python main.py       # 完整版")
            print("  python simple_main.py # 簡化版")
        else:
            print("🔧 需要修復問題才能正常使用")
            print("\n🛠️ 建議步驟:")
            print("  1. python check_dependencies.py")
            print("  2. python install_deps.py")
            print("  3. python start.py")
        
    except Exception as e:
        print(f"💥 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按 Enter 鍵退出...")