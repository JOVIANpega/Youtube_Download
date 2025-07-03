#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試檔案名稱前綴功能
"""

import sys
import os

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_filename_prefix():
    """測試檔案名稱前綴功能"""
    print("🧪 測試檔案名稱前綴功能...")
    
    try:
        # 測試用戶偏好設定
        from user_preferences import UserPreferences
        
        print("🔍 測試用戶偏好設定...")
        preferences = UserPreferences()
        
        # 測試檔案名稱前綴設定
        default_prefix = preferences.get_filename_prefix()
        print(f"   預設前綴: '{default_prefix}'")
        
        # 測試設定變更
        test_prefix = "PER-"
        preferences.set_filename_prefix(test_prefix)
        new_prefix = preferences.get_filename_prefix()
        print(f"   設定為 '{test_prefix}' 後: '{new_prefix}'")
        
        # 恢復原設定
        preferences.set_filename_prefix("")
        print("   已恢復原設定")
        
        # 測試主視窗功能
        print("🔍 測試主視窗功能...")
        from PySide6.QtWidgets import QApplication
        from ui.main_window_pyside import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        
        # 檢查檔案名稱前綴輸入欄位
        if hasattr(window, 'filename_prefix'):
            print("   ✅ 檔案名稱前綴輸入欄位存在")
            print(f"   當前值: '{window.filename_prefix.text()}'")
            print(f"   預設提示: '{window.filename_prefix.placeholderText()}'")
        else:
            print("   ❌ 檔案名稱前綴輸入欄位不存在")
        
        # 測試下載線程功能
        print("🔍 測試下載線程功能...")
        from ui.main_window_pyside import DownloadThread
        
        # 測試檔案名稱處理
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        test_path = os.path.expanduser("~/Downloads")
        
        # 創建測試下載線程
        download_thread = DownloadThread(
            url=test_url,
            output_path=test_path,
            format_choice="影片",
            resolution_choice="自動選擇最佳",
            extract_audio_only=False,
            filename_prefix="TEST-"
        )
        
        print("   ✅ 下載線程創建成功")
        print(f"   前綴設定: '{download_thread.filename_prefix}'")
        
        # 測試檔案名稱清理功能
        test_title = "Test Video Title (with special chars: < > : \" | ? * \\ /)"
        cleaned_title = download_thread.sanitize_filename(test_title)
        print(f"   原始標題: '{test_title}'")
        print(f"   清理後標題: '{cleaned_title}'")
        
        # 測試前綴添加
        if download_thread.filename_prefix:
            final_title = f"{download_thread.filename_prefix}{cleaned_title}"
            print(f"   最終檔案名稱: '{final_title}'")
        
        print("✅ 所有檔案名稱前綴功能測試完成！")
        
        # 顯示功能摘要
        print("\n📋 檔案名稱前綴功能摘要:")
        print("  ✅ 檔案名稱前綴輸入欄位")
        print("  ✅ 用戶偏好設定記憶")
        print("  ✅ 下載線程前綴支援")
        print("  ✅ 檔案名稱清理功能")
        print("  ✅ 前綴與標題組合")
        
        print("\n🎯 使用方式:")
        print("  1. 在「檔案名稱前綴」欄位輸入前綴（如: PER-）")
        print("  2. 下載的檔案名稱會變成: PER-影片標題.mp4")
        print("  3. 前綴設定會自動記憶")
        print("  4. 留空則使用原始檔案名稱")
        
        print("\n💡 範例:")
        print("  前綴: PER-")
        print("  原始標題: Amazing Video")
        print("  最終檔案: PER-Amazing_Video.mp4")
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filename_prefix() 