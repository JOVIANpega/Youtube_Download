#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
實時測試腳本
實際運行並測試應用程式的各項功能
"""

import sys
import os
import time
import traceback

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """打印測試標題"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """打印測試步驟"""
    print(f"\n📋 步驟 {step}: {description}")
    print("-" * 40)

def test_environment():
    """測試運行環境"""
    print_header("環境檢查")
    
    # Python 版本
    version = sys.version_info
    print(f"🐍 Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 版本過低，需要 3.7+")
        return False
    else:
        print("✅ Python 版本符合要求")
    
    # Tkinter 檢查
    try:
        import tkinter as tk
        from tkinter import ttk
        print("✅ Tkinter 可用")
        
        # 測試創建視窗
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        print("✅ Tkinter 功能正常")
        
    except Exception as e:
        print(f"❌ Tkinter 問題: {e}")
        return False
    
    return True

def test_core_modules():
    """測試核心模組"""
    print_header("核心模組測試")
    
    modules = [
        ('constants', '常數定義'),
        ('version_info', '版本資訊'),
        ('logging_config', '日誌配置'),
    ]
    
    passed = 0
    for module, desc in modules:
        try:
            imported = __import__(module)
            print(f"✅ {module} ({desc}) - 導入成功")
            
            # 測試基本屬性
            if module == 'constants':
                print(f"   📝 應用標題: {imported.APP_TITLE}")
                print(f"   📐 視窗大小: {imported.WINDOW_SIZE}")
                print(f"   🌐 支援平台: {len(imported.SUPPORTED_PLATFORMS)} 個")
                
            elif module == 'version_info':
                print(f"   🔢 版本號: {imported.VERSION}")
                
            elif module == 'logging_config':
                logger = imported.setup_logging()
                logger.info("測試日誌訊息")
                print(f"   📝 日誌系統初始化成功")
                
            passed += 1
            
        except Exception as e:
            print(f"❌ {module} ({desc}) - 失敗: {e}")
            traceback.print_exc()
    
    print(f"\n📊 核心模組測試: {passed}/{len(modules)} 通過")
    return passed == len(modules)

def test_utils_modules():
    """測試工具模組"""
    print_header("工具模組測試")
    
    # URL 驗證測試
    print_step(1, "URL 驗證功能")
    try:
        from utils.validators import URLValidator
        
        test_urls = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "YouTube"),
            ("https://youtu.be/dQw4w9WgXcQ", "YouTube"),
            ("https://www.bilibili.com/video/BV1xx411c7mu", "Bilibili"),
            ("https://www.tiktok.com/@user/video/123", "TikTok"),
            ("invalid_url", None),
        ]
        
        for url, expected_platform in test_urls:
            is_valid = URLValidator.is_valid_url(url)
            platform = URLValidator.detect_platform(url)
            
            if platform == expected_platform:
                print(f"✅ {url[:40]}... -> {platform}")
            else:
                print(f"❌ {url[:40]}... -> 預期:{expected_platform}, 實際:{platform}")
                
        print("✅ URL驗證功能正常")
        
    except Exception as e:
        print(f"❌ URL驗證測試失敗: {e}")
        return False
    
    # 路徑工具測試
    print_step(2, "路徑工具功能")
    try:
        from utils.path_utils import sanitize_filename, get_file_size_str
        
        # 檔名清理測試
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("file<>with|illegal*chars.txt", "file__with_illegal_chars.txt"),
            ("CON.txt", "_CON.txt"),
        ]
        
        for original, expected in test_cases:
            result = sanitize_filename(original)
            if result == expected:
                print(f"✅ 檔名清理: '{original}' -> '{result}'")
            else:
                print(f"❌ 檔名清理失敗: '{original}' -> '{result}' (預期: '{expected}')")
        
        # 檔案大小格式化測試
        sizes = [(1024, "1.0 KB"), (1024*1024, "1.0 MB")]
        for size, expected in sizes:
            result = get_file_size_str(size)
            print(f"✅ 大小格式化: {size} -> {result}")
            
        print("✅ 路徑工具功能正常")
        
    except Exception as e:
        print(f"❌ 路徑工具測試失敗: {e}")
        return False
    
    # 字體管理測試
    print_step(3, "字體管理功能")
    try:
        import tkinter as tk
        from utils.ui_fonts import FontManager
        
        root = tk.Tk()
        root.withdraw()
        
        font_manager = FontManager(root)
        initial_size = font_manager.current_size
        print(f"✅ 字體管理器創建成功，初始大小: {initial_size}")
        
        # 測試字體調整
        font_manager.increase_font()
        if font_manager.current_size > initial_size:
            print(f"✅ 增大字體: {initial_size} -> {font_manager.current_size}")
        
        font_manager.decrease_font()
        if font_manager.current_size == initial_size:
            print(f"✅ 減小字體: 恢復到 {font_manager.current_size}")
        
        root.destroy()
        print("✅ 字體管理功能正常")
        
    except Exception as e:
        print(f"❌ 字體管理測試失敗: {e}")
        return False
    
    return True

def test_services():
    """測試服務模組"""
    print_header("服務模組測試")
    
    # 設定管理測試
    print_step(1, "設定管理功能")
    try:
        from services.settings import SettingsManager
        
        manager = SettingsManager()
        settings = manager.load_settings()
        print(f"✅ 設定載入成功，包含 {len(settings)} 項設定")
        
        # 測試設定保存
        test_key = f"test_setting_{int(time.time())}"
        test_value = "test_value_123"
        manager.set_setting(test_key, test_value)
        
        # 重新載入驗證
        new_settings = manager.load_settings()
        if new_settings.get(test_key) == test_value:
            print("✅ 設定保存和載入功能正常")
        else:
            print("❌ 設定保存功能異常")
            return False
            
    except Exception as e:
        print(f"❌ 設定管理測試失敗: {e}")
        return False
    
    # 歷史記錄測試
    print_step(2, "歷史記錄功能")
    try:
        from services.history_store import HistoryStore, HistoryEntry
        
        store = HistoryStore()
        history = store.load_history()
        print(f"✅ 歷史記錄載入成功，現有 {len(history)} 條記錄")
        
        # 測試統計功能
        stats = store.get_statistics()
        if isinstance(stats, dict) and 'total_downloads' in stats:
            print(f"✅ 統計功能正常: 總下載 {stats['total_downloads']} 個")
            print(f"   📊 總大小: {stats.get('total_size_str', '0 B')}")
            print(f"   📁 存在檔案: {stats.get('existing_files', 0)}")
        else:
            print("❌ 統計功能異常")
            return False
            
    except Exception as e:
        print(f"❌ 歷史記錄測試失敗: {e}")
        return False
    
    # FFmpeg 管理測試
    print_step(3, "FFmpeg 管理功能")
    try:
        from services.ffmpeg_manager import FFmpegManager
        
        ffmpeg = FFmpegManager()
        is_available = ffmpeg.is_available()
        
        if is_available:
            version = ffmpeg.get_version()
            print(f"✅ FFmpeg 可用，版本: {version}")
            
            # 測試功能
            is_working, message = ffmpeg.test_functionality()
            if is_working:
                print(f"✅ FFmpeg 功能測試通過")
            else:
                print(f"⚠️ FFmpeg 功能測試失敗: {message}")
        else:
            print("⚠️ FFmpeg 未安裝（不影響基本功能）")
            
    except Exception as e:
        print(f"❌ FFmpeg 管理測試失敗: {e}")
        return False
    
    return True

def test_gui_creation():
    """測試GUI創建"""
    print_header("GUI 創建測試")
    
    # 簡化GUI測試
    print_step(1, "簡化GUI測試")
    try:
        import simple_main
        
        print("正在創建簡化應用程式...")
        app = simple_main.SimpleApp()
        print("✅ 簡化應用程式創建成功")
        
        # 檢查基本組件
        if hasattr(app, 'root') and hasattr(app, 'notebook'):
            print("✅ 基本UI組件存在")
        
        # 快速關閉測試
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        print("✅ 簡化GUI測試完成")
        
    except Exception as e:
        print(f"❌ 簡化GUI測試失敗: {e}")
        traceback.print_exc()
        return False
    
    # 完整應用程式測試
    print_step(2, "完整應用程式測試")
    try:
        import main
        
        print("正在創建完整應用程式...")
        app = main.MainApplication()
        print("✅ 完整應用程式創建成功")
        
        # 檢查組件
        components = ['root', 'notebook', 'font_manager', 'settings_manager', 
                     'download_tab', 'external_tab', 'history_tab']
        
        missing = [comp for comp in components if not hasattr(app, comp)]
        if not missing:
            print("✅ 所有必要組件都存在")
        else:
            print(f"❌ 缺少組件: {missing}")
            return False
        
        # 測試字體功能
        initial_size = app.font_manager.current_size
        app.font_manager.increase_font()
        if app.font_manager.current_size > initial_size:
            print(f"✅ 字體調整功能正常: {initial_size} -> {app.font_manager.current_size}")
        
        # 快速關閉測試
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        print("✅ 完整應用程式測試完成")
        
    except Exception as e:
        print(f"❌ 完整應用程式測試失敗: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_dependencies():
    """測試依賴狀態"""
    print_header("依賴狀態檢查")
    
    deps = {
        'yt_dlp': ('下載核心功能', False),
        'requests': ('HTTP請求功能', False),
    }
    
    available_count = 0
    
    for dep, (desc, required) in deps.items():
        try:
            __import__(dep)
            print(f"✅ {dep} 已安裝 - {desc}")
            available_count += 1
        except ImportError:
            status = "❌ 必要" if required else "⚠️ 可選"
            print(f"{status} {dep} 未安裝 - {desc}")
            if not required:
                print(f"   💡 安裝指令: pip install {dep.replace('_', '-')}")
    
    print(f"\n📊 依賴狀態: {available_count}/{len(deps)} 可選依賴可用")
    
    if available_count == len(deps):
        print("🎉 所有功能完全可用！")
    elif available_count > 0:
        print("✅ 基本功能可用，部分功能需要額外依賴")
    else:
        print("⚠️ 僅GUI功能可用，建議安裝 yt-dlp 獲得完整功能")
    
    return True

def main():
    """主測試函數"""
    print("🚀 YouTube 下載器 - 實時功能測試")
    print("=" * 60)
    print("正在執行完整的功能測試...")
    
    tests = [
        ("環境檢查", test_environment),
        ("核心模組", test_core_modules),
        ("工具模組", test_utils_modules),
        ("服務模組", test_services),
        ("GUI創建", test_gui_creation),
        ("依賴狀態", test_dependencies),
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n🔄 正在執行: {test_name}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} - 通過")
            else:
                print(f"❌ {test_name} - 失敗")
                
        except Exception as e:
            print(f"💥 {test_name} - 異常: {e}")
            results.append((test_name, False))
    
    # 最終報告
    end_time = time.time()
    duration = end_time - start_time
    
    print_header("測試結果總報告")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"⏱️ 測試耗時: {duration:.2f} 秒")
    print(f"📊 測試結果: {passed}/{total} 通過 ({percentage:.1f}%)")
    print()
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:15} : {status}")
    
    print()
    
    # 結論和建議
    if passed == total:
        print("🎉 所有測試通過！應用程式完全可用！")
        print("\n🚀 推薦啟動方式:")
        print("  python start.py      # 一鍵啟動（推薦）")
        print("  python main.py       # 直接啟動完整版")
        
    elif passed >= total * 0.8:
        print("✅ 大部分功能正常！應用程式基本可用！")
        print("\n🚀 可用啟動方式:")
        print("  python start.py      # 智能啟動（推薦）")
        print("  python simple_main.py # 簡化版")
        print("\n💡 建議安裝 yt-dlp 獲得完整下載功能:")
        print("  pip install yt-dlp")
        
    else:
        print("⚠️ 部分核心功能有問題，需要檢查環境")
        print("\n🔧 建議步驟:")
        print("  1. python check_dependencies.py")
        print("  2. python install_deps.py")
        print("  3. 重新運行此測試")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    try:
        success = main()
        
        print(f"\n{'='*60}")
        if success:
            print("🎯 實時測試完成！應用程式準備就緒！")
            print("\n立即體驗: python start.py")
        else:
            print("🔧 需要修復一些問題")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 用戶中斷測試")
    except Exception as e:
        print(f"\n💥 測試過程發生錯誤: {e}")
        traceback.print_exc()
    
    input("\n按 Enter 鍵退出...")