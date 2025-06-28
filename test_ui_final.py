#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終 UI 改進測試
測試項目：
1. 視窗大小設定
2. 動態解析度載入
3. 停止下載功能
4. 版本資訊顯示
5. 錯誤分析功能
6. 移除日韓文
"""

import sys
import os

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_final_ui_improvements():
    """測試最終 UI 改進功能"""
    print("🧪 開始測試最終 UI 改進功能...")
    
    try:
        from ui.main_window_pyside import MainWindow
        from PySide6.QtWidgets import QApplication
        
        # 創建應用程式
        app = QApplication(sys.argv)
        
        # 創建主視窗
        window = MainWindow()
        
        print("✅ 主視窗創建成功")
        
        # 測試視窗標題（移除日韓文）
        title = window.windowTitle()
        print(f"🔍 視窗標題: {title}")
        if "YouTube動画ダウンローダー" not in title and "유튜브 비디오 다운로더" not in title:
            print("   ✅ 已移除日韓文")
        else:
            print("   ❌ 仍包含日韓文")
        
        # 測試視窗大小
        size = window.size()
        print(f"🔍 視窗大小: {size.width()} x {size.height()}")
        if size.width() >= 800 and size.height() >= 600:
            print("   ✅ 視窗大小設定正確")
        else:
            print("   ❌ 視窗大小設定錯誤")
        
        # 測試解析度選項（應該只有基本選項，動態載入）
        resolution_combo = window.resolution_combo
        resolution_options = [resolution_combo.itemText(i) for i in range(resolution_combo.count())]
        
        print(f"🔍 初始解析度選項:")
        expected_basic = ["自動選擇最佳", "最高品質"]
        for expected in expected_basic:
            if expected in resolution_options:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ {expected} (缺失)")
        
        # 測試按鈕
        print(f"🔍 按鈕檢查:")
        print(f"   - 下載按鈕: {'✅' if window.download_button.isEnabled() else '❌'}")
        print(f"   - 停止按鈕: {'✅' if not window.stop_button.isEnabled() else '❌'}")
        
        # 測試版本資訊功能
        print(f"🔍 版本資訊功能:")
        try:
            # 模擬版本資訊顯示
            version_info = window.show_version_info()
            print("   ✅ 版本資訊功能正常")
        except Exception as e:
            print(f"   ❌ 版本資訊功能錯誤: {e}")
        
        # 測試錯誤分析功能
        print(f"🔍 錯誤分析功能:")
        test_errors = [
            "Failed to extract any player response",
            "Video unavailable",
            "Sign in to confirm your age",
            "Network error"
        ]
        
        for error in test_errors:
            analysis = window.analyze_download_error(error)
            if "🔍 錯誤分析:" in analysis:
                print(f"   ✅ 錯誤分析正常: {error[:30]}...")
            else:
                print(f"   ❌ 錯誤分析失敗: {error}")
        
        # 測試停止下載功能
        print(f"🔍 停止下載功能:")
        try:
            window.stop_download()  # 應該不會出錯
            print("   ✅ 停止下載功能正常")
        except Exception as e:
            print(f"   ❌ 停止下載功能錯誤: {e}")
        
        print("✅ 所有測試完成！")
        
        # 顯示視窗（可選）
        # window.show()
        # sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_ui_improvements() 