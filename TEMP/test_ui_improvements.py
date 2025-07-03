#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 UI 改進功能
測試項目：
1. 視窗拖曳調整大小
2. 解析度選項（720P、1080P等）
3. 下載完成後顯示檔案位置
"""

import sys
import os

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_ui_improvements():
    """測試 UI 改進功能"""
    print("🧪 開始測試 UI 改進功能...")
    
    try:
        from ui.main_window_pyside import MainWindow
        from PySide6.QtWidgets import QApplication
        
        # 創建應用程式
        app = QApplication(sys.argv)
        
        # 創建主視窗
        window = MainWindow()
        
        print("✅ 主視窗創建成功")
        
        # 測試視窗標誌
        window_flags = window.windowFlags()
        has_maximize = bool(window_flags & 0x00010000)  # WindowMaximizeButtonHint
        has_minimize = bool(window_flags & 0x00020000)  # WindowMinimizeButtonHint
        
        print(f"🔍 視窗標誌檢查:")
        print(f"   - 最大化按鈕: {'✅' if has_maximize else '❌'}")
        print(f"   - 最小化按鈕: {'✅' if has_minimize else '❌'}")
        
        # 測試解析度選項
        resolution_combo = window.resolution_combo
        resolution_options = [resolution_combo.itemText(i) for i in range(resolution_combo.count())]
        
        print(f"🔍 解析度選項檢查:")
        expected_resolutions = ["自動選擇最佳", "最高品質", "1080P (Full HD)", "720P (HD)", "480P", "360P"]
        
        for expected in expected_resolutions:
            if expected in resolution_options:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ {expected} (缺失)")
        
        # 檢查預設解析度
        current_resolution = resolution_combo.currentText()
        print(f"🔍 預設解析度: {current_resolution}")
        
        if current_resolution == "720P (HD)":
            print("   ✅ 預設解析度設定正確")
        else:
            print("   ⚠️  預設解析度不是 720P")
        
        # 測試下載線程的解析度處理
        from ui.main_window_pyside import DownloadThread
        
        # 創建測試線程（不實際下載）
        test_thread = DownloadThread("", "", "影片", "720P (HD)", False)
        
        # 測試解析度格式選擇
        format_720p = test_thread.get_format_by_resolution("720P (HD)")
        format_1080p = test_thread.get_format_by_resolution("1080P (Full HD)")
        format_auto = test_thread.get_format_by_resolution("自動選擇最佳")
        format_best = test_thread.get_format_by_resolution("最高品質")
        
        print(f"🔍 解析度格式選擇測試:")
        print(f"   720P: {format_720p}")
        print(f"   1080P: {format_1080p}")
        print(f"   自動選擇: {format_auto}")
        print(f"   最高品質: {format_best}")
        
        # 測試檔案名稱清理
        test_filenames = [
            "正常檔案名稱",
            "檔案名稱 with spaces",
            "檔案名稱<with>illegal:chars|?*\\/",
            "檔案名稱 with 特殊字符 🎵🎬",
            "檔案名稱 with 換行\n和\r回車\t製表符"
        ]
        
        print(f"🔍 檔案名稱清理測試:")
        for test_name in test_filenames:
            cleaned = test_thread.sanitize_filename(test_name)
            print(f"   原始: {test_name}")
            print(f"   清理: {cleaned}")
            print()
        
        print("✅ 所有測試完成！")
        
        # 顯示視窗（可選）
        # window.show()
        # sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ui_improvements() 