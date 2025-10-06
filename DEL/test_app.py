#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試應用程式
簡單測試主要功能
"""

import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """測試模組導入"""
    print("測試模組導入...")
    
    try:
        import constants
        print("✓ constants 模組導入成功")
    except Exception as e:
        print(f"✗ constants 模組導入失敗: {e}")
        
    try:
        import version_info
        print("✓ version_info 模組導入成功")
    except Exception as e:
        print(f"✗ version_info 模組導入失敗: {e}")
        
    try:
        import logging_config
        print("✓ logging_config 模組導入成功")
    except Exception as e:
        print(f"✗ logging_config 模組導入失敗: {e}")
        
    try:
        from utils.path_utils import get_resource_path, sanitize_filename
        print("✓ utils.path_utils 模組導入成功")
    except Exception as e:
        print(f"✗ utils.path_utils 模組導入失敗: {e}")
        
    try:
        from utils.validators import URLValidator
        print("✓ utils.validators 模組導入成功")
    except Exception as e:
        print(f"✗ utils.validators 模組導入失敗: {e}")
        
    try:
        from services.settings import SettingsManager
        print("✓ services.settings 模組導入成功")
    except Exception as e:
        print(f"✗ services.settings 模組導入失敗: {e}")

def test_url_validation():
    """測試 URL 驗證"""
    print("\n測試 URL 驗證...")
    
    try:
        from utils.validators import URLValidator
        
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.bilibili.com/video/BV1xx411c7mu",
            "invalid_url",
            "",
        ]
        
        for url in test_urls:
            is_valid = URLValidator.is_valid_url(url)
            platform = URLValidator.detect_platform(url)
            print(f"URL: {url[:50]}...")
            print(f"  有效: {is_valid}")
            print(f"  平台: {platform}")
            
    except Exception as e:
        print(f"✗ URL 驗證測試失敗: {e}")

def test_settings():
    """測試設定管理"""
    print("\n測試設定管理...")
    
    try:
        from services.settings import SettingsManager
        
        settings_manager = SettingsManager()
        
        # 載入預設設定
        settings = settings_manager.load_settings()
        print(f"✓ 載入設定成功，共 {len(settings)} 項")
        
        # 測試設定項目
        test_setting = settings.get('font_size', 12)
        print(f"✓ 字體大小: {test_setting}")
        
        # 測試保存設定
        settings_manager.set_setting('test_key', 'test_value')
        print("✓ 設定保存測試成功")
        
    except Exception as e:
        print(f"✗ 設定管理測試失敗: {e}")

def test_history():
    """測試歷史記錄"""
    print("\n測試歷史記錄...")
    
    try:
        from services.history_store import HistoryStore, HistoryEntry
        
        history_store = HistoryStore()
        
        # 載入歷史記錄
        history = history_store.load_history()
        print(f"✓ 載入歷史記錄成功，共 {len(history)} 條")
        
        # 獲取統計資訊
        stats = history_store.get_statistics()
        print(f"✓ 統計資訊: {stats}")
        
    except Exception as e:
        print(f"✗ 歷史記錄測試失敗: {e}")

def test_ffmpeg():
    """測試 FFmpeg"""
    print("\n測試 FFmpeg...")
    
    try:
        from services.ffmpeg_manager import FFmpegManager
        
        ffmpeg_manager = FFmpegManager()
        
        is_available = ffmpeg_manager.is_available()
        print(f"✓ FFmpeg 可用性: {is_available}")
        
        if is_available:
            version = ffmpeg_manager.get_version()
            print(f"✓ FFmpeg 版本: {version}")
            
            # 測試功能
            is_working, message = ffmpeg_manager.test_functionality()
            print(f"✓ FFmpeg 功能測試: {is_working} - {message}")
        else:
            print("ℹ FFmpeg 未安裝或未找到")
            
    except Exception as e:
        print(f"✗ FFmpeg 測試失敗: {e}")

def main():
    """主函數"""
    print("YouTube 下載器 - 功能測試")
    print("=" * 50)
    
    test_imports()
    test_url_validation()
    test_settings()
    test_history()
    test_ffmpeg()
    
    print("\n" + "=" * 50)
    print("測試完成")

if __name__ == "__main__":
    main()