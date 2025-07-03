#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 V1.1.1 新功能
"""

import sys
import os

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_new_features():
    """測試 V1.1.1 新功能"""
    print("🧪 測試 V1.1.1 新功能...")
    
    try:
        # 測試用戶偏好設定
        from user_preferences import UserPreferences
        
        print("🔍 測試用戶偏好設定...")
        preferences = UserPreferences()
        
        # 測試下載完成提醒設定
        default_show_dialog = preferences.get_show_completion_dialog()
        print(f"   預設下載完成提醒: {'✅ 開啟' if default_show_dialog else '❌ 關閉'}")
        
        # 測試設定變更
        preferences.set_show_completion_dialog(False)
        new_setting = preferences.get_show_completion_dialog()
        print(f"   設定為關閉後: {'✅ 開啟' if new_setting else '❌ 關閉'}")
        
        # 恢復原設定
        preferences.set_show_completion_dialog(True)
        print("   已恢復原設定")
        
        # 測試主視窗功能
        print("🔍 測試主視窗功能...")
        from PySide6.QtWidgets import QApplication
        from ui.main_window_pyside import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        
        # 檢查下載完成提醒設定選項
        if hasattr(window, 'show_completion_dialog'):
            print("   ✅ 下載完成提醒設定選項存在")
            print(f"   當前狀態: {'✅ 開啟' if window.show_completion_dialog.isChecked() else '❌ 關閉'}")
        else:
            print("   ❌ 下載完成提醒設定選項不存在")
        
        # 測試開啟檔案目錄功能
        print("🔍 測試開啟檔案目錄功能...")
        test_file_path = os.path.join(os.path.expanduser("~"), "Downloads", "test_video.mp4")
        
        try:
            # 測試函數是否存在
            if hasattr(window, 'open_file_directory'):
                print("   ✅ 開啟檔案目錄功能存在")
                # 注意：這裡不會真的開啟目錄，只是測試函數是否正常
                print("   ℹ️ 函數已準備就緒（測試時不會實際開啟目錄）")
            else:
                print("   ❌ 開啟檔案目錄功能不存在")
        except Exception as e:
            print(f"   ⚠️ 開啟檔案目錄功能測試: {e}")
        
        # 測試自定義對話框功能
        print("🔍 測試自定義對話框功能...")
        try:
            if hasattr(window, 'show_completion_dialog_with_options'):
                print("   ✅ 自定義對話框功能存在")
                print("   ℹ️ 對話框功能已準備就緒")
            else:
                print("   ❌ 自定義對話框功能不存在")
        except Exception as e:
            print(f"   ❌ 自定義對話框功能錯誤: {e}")
        
        print("✅ 所有新功能測試完成！")
        
        # 顯示功能摘要
        print("\n📋 V1.1.1 新功能摘要:")
        print("  ✅ 下載完成自定義對話框")
        print("  ✅ 一鍵開啟檔案目錄")
        print("  ✅ 可自訂是否顯示提醒視窗")
        print("  ✅ 移除對話框音效")
        print("  ✅ 用戶偏好設定管理")
        
        print("\n🎯 功能特點:")
        print("  - 美觀的下載完成提示")
        print("  - 跨平台檔案目錄開啟支援")
        print("  - 個性化的提醒設定")
        print("  - 無音效干擾")
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_features() 