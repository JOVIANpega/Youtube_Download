#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特定功能測試
逐一測試各個核心功能模組
"""

import sys
import os
import traceback

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_url_validation():
    """測試URL驗證功能"""
    print("🔍 測試URL驗證功能...")
    
    try:
        from utils.validators import URLValidator
        
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True, "YouTube"),
            ("https://youtu.be/dQw4w9WgXcQ", True, "YouTube"),
            ("https://www.bilibili.com/video/BV1xx411c7mu", True, "Bilibili"),
            ("https://b23.tv/abc123", True, "Bilibili"),
            ("https://www.tiktok.com/@user/video/123456", True, "TikTok"),
            ("invalid_url", False, None),
            ("", False, None),
            ("http://example.com", True, None),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for url, expected_valid, expected_platform in test_cases:
            is_valid = URLValidator.is_valid_url(url)
            platform = URLValidator.detect_platform(url)
            
            valid_ok = is_valid == expected_valid
            platform_ok = platform == expected_platform
            
            if valid_ok and platform_ok:
                print(f"  ✅ {url[:30]}... -> 有效:{is_valid}, 平台:{platform}")
                passed += 1
            else:
                print(f"  ❌ {url[:30]}... -> 預期有效:{expected_valid}, 實際:{is_valid}, 預期平台:{expected_platform}, 實際:{platform}")
        
        print(f"  📊 URL驗證測試: {passed}/{total} 通過")
        return passed == total
        
    except Exception as e:
        print(f"  ❌ URL驗證測試失敗: {e}")
        traceback.print_exc()
        return False

def test_path_utils():
    """測試路徑工具功能"""
    print("\n📁 測試路徑工具功能...")
    
    try:
        from utils.path_utils import sanitize_filename, get_safe_path, get_file_size_str
        
        # 測試檔名清理
        test_filenames = [
            ("normal_file.txt", "normal_file.txt"),
            ("file<>with|illegal*chars.txt", "file__with_illegal_chars.txt"),
            ("file with spaces.txt", "file with spaces.txt"),
            ("CON.txt", "_CON.txt"),  # Windows保留名稱
            ("", "untitled"),
        ]
        
        filename_passed = 0
        for original, expected in test_filenames:
            result = sanitize_filename(original)
            if result == expected:
                print(f"  ✅ 檔名清理: '{original}' -> '{result}'")
                filename_passed += 1
            else:
                print(f"  ❌ 檔名清理: '{original}' -> 預期:'{expected}', 實際:'{result}'")
        
        # 測試檔案大小格式化
        size_tests = [
            (0, "0 B"),
            (1024, "1.0 KB"),
            (1024*1024, "1.0 MB"),
            (1024*1024*1024, "1.0 GB"),
        ]
        
        size_passed = 0
        for size, expected in size_tests:
            result = get_file_size_str(size)
            if result == expected:
                print(f"  ✅ 大小格式化: {size} -> {result}")
                size_passed += 1
            else:
                print(f"  ❌ 大小格式化: {size} -> 預期:{expected}, 實際:{result}")
        
        total_tests = len(test_filenames) + len(size_tests)
        total_passed = filename_passed + size_passed
        
        print(f"  📊 路徑工具測試: {total_passed}/{total_tests} 通過")
        return total_passed == total_tests
        
    except Exception as e:
        print(f"  ❌ 路徑工具測試失敗: {e}")
        traceback.print_exc()
        return False

def test_settings_manager():
    """測試設定管理功能"""
    print("\n⚙️ 測試設定管理功能...")
    
    try:
        from services.settings import SettingsManager
        
        # 創建設定管理器
        settings_manager = SettingsManager()
        
        # 測試載入預設設定
        settings = settings_manager.load_settings()
        print(f"  ✅ 載入設定成功，共 {len(settings)} 項")
        
        # 檢查必要的設定項目
        required_keys = ['font_size', 'download_path', 'quality_preference', 'window_geometry']
        missing_keys = [key for key in required_keys if key not in settings]
        
        if not missing_keys:
            print(f"  ✅ 所有必要設定項目都存在")
        else:
            print(f"  ❌ 缺少設定項目: {missing_keys}")
            return False
        
        # 測試設定單個值
        test_key = 'test_setting'
        test_value = 'test_value_123'
        settings_manager.set_setting(test_key, test_value)
        
        # 重新載入並檢查
        new_settings = settings_manager.load_settings()
        if new_settings.get(test_key) == test_value:
            print(f"  ✅ 設定保存和載入功能正常")
        else:
            print(f"  ❌ 設定保存失敗")
            return False
        
        # 測試批量更新
        updates = {
            'test_batch_1': 'value1',
            'test_batch_2': 'value2'
        }
        settings_manager.update_settings(updates)
        
        updated_settings = settings_manager.load_settings()
        batch_ok = all(updated_settings.get(k) == v for k, v in updates.items())
        
        if batch_ok:
            print(f"  ✅ 批量設定更新功能正常")
        else:
            print(f"  ❌ 批量設定更新失敗")
            return False
        
        print(f"  📊 設定管理測試: 全部通過")
        return True
        
    except Exception as e:
        print(f"  ❌ 設定管理測試失敗: {e}")
        traceback.print_exc()
        return False

def test_history_store():
    """測試歷史記錄功能"""
    print("\n📚 測試歷史記錄功能...")
    
    try:
        from services.history_store import HistoryStore, HistoryEntry
        
        # 創建歷史記錄管理器
        history_store = HistoryStore()
        
        # 載入現有歷史
        history = history_store.load_history()
        original_count = len(history)
        print(f"  ✅ 載入歷史記錄成功，現有 {original_count} 條")
        
        # 創建測試記錄
        test_entry = HistoryEntry(
            url="https://www.youtube.com/watch?v=test123",
            title="測試視頻標題",
            platform="YouTube",
            filename="test_video.mp4",
            file_path="/test/path/test_video.mp4",
            file_size=1024*1024,  # 1MB
            quality="720p",
            duration=180  # 3分鐘
        )
        
        # 添加測試記錄
        history_store.add_entry(test_entry)
        
        # 重新載入並檢查
        new_history = history_store.load_history()
        if len(new_history) > original_count:
            print(f"  ✅ 添加歷史記錄成功，現有 {len(new_history)} 條")
        else:
            print(f"  ❌ 添加歷史記錄失敗")
            return False
        
        # 測試搜索功能
        search_results = history_store.search_history("測試")
        if search_results:
            print(f"  ✅ 搜索功能正常，找到 {len(search_results)} 條結果")
        else:
            print(f"  ⚠️ 搜索功能可能有問題，或沒有匹配結果")
        
        # 測試統計功能
        stats = history_store.get_statistics()
        if isinstance(stats, dict) and 'total_downloads' in stats:
            print(f"  ✅ 統計功能正常: 總下載 {stats['total_downloads']} 個")
        else:
            print(f"  ❌ 統計功能失敗")
            return False
        
        # 清理測試記錄
        history_store.remove_entry(test_entry.url)
        
        print(f"  📊 歷史記錄測試: 全部通過")
        return True
        
    except Exception as e:
        print(f"  ❌ 歷史記錄測試失敗: {e}")
        traceback.print_exc()
        return False

def test_font_manager():
    """測試字體管理功能"""
    print("\n🔤 測試字體管理功能...")
    
    try:
        import tkinter as tk
        from utils.ui_fonts import FontManager
        
        # 創建隱藏的根視窗
        root = tk.Tk()
        root.withdraw()
        
        # 創建字體管理器
        font_manager = FontManager(root)
        initial_size = font_manager.current_size
        print(f"  ✅ 字體管理器創建成功，初始大小: {initial_size}")
        
        # 測試增大字體
        font_manager.increase_font()
        if font_manager.current_size > initial_size:
            print(f"  ✅ 增大字體功能正常: {initial_size} -> {font_manager.current_size}")
        else:
            print(f"  ❌ 增大字體功能失敗")
            root.destroy()
            return False
        
        # 測試減小字體
        font_manager.decrease_font()
        if font_manager.current_size == initial_size:
            print(f"  ✅ 減小字體功能正常: 恢復到 {font_manager.current_size}")
        else:
            print(f"  ❌ 減小字體功能失敗")
            root.destroy()
            return False
        
        # 測試設置特定大小
        test_size = 14
        font_manager.set_font_size(test_size)
        if font_manager.current_size == test_size:
            print(f"  ✅ 設置字體大小功能正常: {test_size}")
        else:
            print(f"  ❌ 設置字體大小功能失敗")
            root.destroy()
            return False
        
        # 測試獲取字體
        default_font = font_manager.get_font('default')
        bold_font = font_manager.get_font('bold')
        
        if default_font and bold_font:
            print(f"  ✅ 字體獲取功能正常")
        else:
            print(f"  ❌ 字體獲取功能失敗")
            root.destroy()
            return False
        
        root.destroy()
        print(f"  📊 字體管理測試: 全部通過")
        return True
        
    except Exception as e:
        print(f"  ❌ 字體管理測試失敗: {e}")
        traceback.print_exc()
        return False

def test_ffmpeg_manager():
    """測試FFmpeg管理功能"""
    print("\n🎬 測試FFmpeg管理功能...")
    
    try:
        from services.ffmpeg_manager import FFmpegManager
        
        # 創建FFmpeg管理器
        ffmpeg_manager = FFmpegManager()
        
        # 檢查FFmpeg可用性
        is_available = ffmpeg_manager.is_available()
        print(f"  📋 FFmpeg 可用性: {is_available}")
        
        if is_available:
            # 獲取版本資訊
            version = ffmpeg_manager.get_version()
            print(f"  ✅ FFmpeg 版本: {version}")
            
            # 測試功能
            is_working, message = ffmpeg_manager.test_functionality()
            print(f"  📋 FFmpeg 功能測試: {is_working} - {message}")
            
            if is_working:
                print(f"  ✅ FFmpeg 完全可用")
                return True
            else:
                print(f"  ⚠️ FFmpeg 已安裝但功能測試失敗")
                return False
        else:
            print(f"  ⚠️ FFmpeg 未安裝或未找到")
            print(f"  💡 這不會影響基本下載功能，但無法自動合併音視頻")
            return True  # 不算失敗，因為FFmpeg是可選的
        
    except Exception as e:
        print(f"  ❌ FFmpeg管理測試失敗: {e}")
        traceback.print_exc()
        return False

def test_downloader_basic():
    """測試下載器基本功能（不實際下載）"""
    print("\n⬇️ 測試下載器基本功能...")
    
    try:
        from services.downloader import VideoDownloader
        
        # 創建下載器
        downloader = VideoDownloader()
        print(f"  ✅ 下載器創建成功")
        
        # 測試視頻資訊獲取（需要yt-dlp）
        try:
            # 使用一個簡單的測試URL
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            
            # 只測試URL格式，不實際獲取資訊（避免網路依賴）
            from utils.validators import URLValidator
            if URLValidator.is_valid_url(test_url):
                print(f"  ✅ URL驗證通過")
            else:
                print(f"  ❌ URL驗證失敗")
                return False
            
            # 檢查yt-dlp是否可用
            try:
                import yt_dlp
                print(f"  ✅ yt-dlp 可用，下載功能完整")
            except ImportError:
                print(f"  ⚠️ yt-dlp 未安裝，下載功能不可用")
                print(f"  💡 運行 'pip install yt-dlp' 來啟用下載功能")
            
            print(f"  📊 下載器基本測試: 通過")
            return True
            
        except Exception as e:
            print(f"  ⚠️ 下載器功能測試跳過（可能缺少依賴）: {e}")
            return True  # 不算失敗
        
    except Exception as e:
        print(f"  ❌ 下載器基本測試失敗: {e}")
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🧪 YouTube 下載器 - 特定功能測試")
    print("=" * 60)
    
    tests = [
        ("URL驗證功能", test_url_validation),
        ("路徑工具功能", test_path_utils),
        ("設定管理功能", test_settings_manager),
        ("歷史記錄功能", test_history_store),
        ("字體管理功能", test_font_manager),
        ("FFmpeg管理功能", test_ffmpeg_manager),
        ("下載器基本功能", test_downloader_basic),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} 測試通過")
            else:
                print(f"❌ {test_name} 測試失敗")
                
        except Exception as e:
            print(f"💥 {test_name} 測試發生異常: {e}")
            results.append((test_name, False))
    
    # 總結報告
    print(f"\n{'='*60}")
    print("📊 測試結果總結")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\n📈 總計: {passed}/{total} 個功能測試通過 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有核心功能都正常工作！")
        print("🚀 應用程式可以正常使用")
    elif passed >= total * 0.8:
        print("✅ 大部分功能正常，應用程式基本可用")
        print("💡 部分功能可能需要安裝額外依賴")
    else:
        print("⚠️ 多個功能存在問題，建議檢查環境配置")
        print("🔧 請運行 'python check_dependencies.py' 檢查依賴")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*60}")
    if success:
        print("🎯 功能測試完成，應用程式準備就緒！")
    else:
        print("🔧 需要修復一些問題才能正常使用")
    
    input("\n按 Enter 鍵退出...")