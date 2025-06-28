#!/usr/bin/env python3
"""
簡單功能測試
Simple functionality test
簡単な機能テスト
간단한 기능 테스트
"""

import sys
import os

def test_imports():
    """測試所有必要的模組是否能正常導入"""
    print("測試模組導入...")
    
    try:
        import PyQt6
        print("✓ PyQt6 導入成功")
    except ImportError as e:
        print(f"✗ PyQt6 導入失敗: {e}")
        return False
    
    try:
        import yt_dlp
        print("✓ yt-dlp 導入成功")
    except ImportError as e:
        print(f"✗ yt-dlp 導入失敗: {e}")
        return False
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ FFmpeg 可用")
        else:
            print("✗ FFmpeg 不可用")
            return False
    except Exception as e:
        print(f"✗ FFmpeg 測試失敗: {e}")
        return False
    
    return True

def test_gui_creation():
    """測試 GUI 是否能正常創建"""
    print("\n測試 GUI 創建...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from src.ui.main_window import MainWindow
        
        # 創建應用程式實例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 創建主視窗
        window = MainWindow()
        print("✓ GUI 創建成功")
        
        # 測試基本屬性
        assert window.url_input is not None
        assert window.format_combo is not None
        assert window.download_button is not None
        print("✓ GUI 組件初始化成功")
        
        return True
        
    except Exception as e:
        print(f"✗ GUI 創建失敗: {e}")
        return False

def test_yt_dlp_basic():
    """測試 yt-dlp 基本功能"""
    print("\n測試 yt-dlp 基本功能...")
    
    try:
        import yt_dlp
        
        # 測試創建 YoutubeDL 實例
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("✓ yt-dlp 實例創建成功")
        
        # 測試格式選擇器
        format_choices = [
            "預設品質",
            "最高品質影片", 
            "僅音訊 (MP3)",
            "僅音訊 (WAV)"
        ]
        
        for choice in format_choices:
            print(f"✓ 格式選項: {choice}")
        
        return True
        
    except Exception as e:
        print(f"✗ yt-dlp 測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("YouTube 下載器簡單測試")
    print("=" * 50)
    
    all_tests_passed = True
    
    # 測試模組導入
    if not test_imports():
        all_tests_passed = False
    
    # 測試 yt-dlp 基本功能
    if not test_yt_dlp_basic():
        all_tests_passed = False
    
    # 測試 GUI 創建
    if not test_gui_creation():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 所有測試通過！")
        print("YouTube 下載器已準備就緒。")
        print("\n使用方法:")
        print("python src/main.py")
    else:
        print("⚠️  部分測試失敗，請檢查安裝。") 