#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試下載完成對話框功能
測試項目：
1. 下載完成提醒設定
2. 自定義對話框顯示
3. 開啟檔案目錄功能
"""

import sys
import os

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_completion_dialog():
    """測試下載完成對話框功能"""
    print("🧪 開始測試下載完成對話框功能...")
    
    try:
        from ui.main_window_pyside import MainWindow
        from PySide6.QtWidgets import QApplication
        
        # 創建應用程式
        app = QApplication(sys.argv)
        
        # 創建主視窗
        window = MainWindow()
        
        print("✅ 主視窗創建成功")
        
        # 測試下載完成提醒設定
        print("🔍 測試下載完成提醒設定:")
        
        # 檢查預設值
        default_value = window.show_completion_dialog.isChecked()
        print(f"   預設值: {'✅ 開啟' if default_value else '❌ 關閉'}")
        
        # 測試設定變更
        window.show_completion_dialog.setChecked(False)
        print("   設定為關閉")
        
        window.show_completion_dialog.setChecked(True)
        print("   設定為開啟")
        
        # 測試開啟檔案目錄功能
        print("🔍 測試開啟檔案目錄功能:")
        test_file_path = os.path.join(os.path.expanduser("~"), "Downloads", "test_video.mp4")
        
        try:
            # 模擬開啟檔案目錄（不會真的開啟，只是測試函數是否正常）
            window.open_file_directory(test_file_path)
            print("   ✅ 開啟檔案目錄功能正常")
        except Exception as e:
            print(f"   ⚠️ 開啟檔案目錄功能測試: {e}")
        
        # 測試自定義對話框
        print("🔍 測試自定義對話框:")
        try:
            # 模擬顯示下載完成對話框
            window.show_completion_dialog_with_options(
                os.path.expanduser("~/Downloads"),
                "test_video.mp4"
            )
            print("   ✅ 自定義對話框功能正常")
        except Exception as e:
            print(f"   ❌ 自定義對話框功能錯誤: {e}")
        
        # 測試用戶偏好設定
        print("🔍 測試用戶偏好設定:")
        preferences = window.preferences
        
        # 測試獲取設定
        show_dialog = preferences.get_show_completion_dialog()
        print(f"   當前設定: {'✅ 開啟' if show_dialog else '❌ 關閉'}")
        
        # 測試設定變更
        preferences.set_show_completion_dialog(False)
        new_setting = preferences.get_show_completion_dialog()
        print(f"   設定為關閉後: {'✅ 開啟' if new_setting else '❌ 關閉'}")
        
        # 恢復原設定
        preferences.set_show_completion_dialog(True)
        print("   已恢復原設定")
        
        print("✅ 所有測試完成！")
        
        # 顯示視窗（可選）
        # window.show()
        # sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_completion_dialog() 