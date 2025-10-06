#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試
快速檢查應用程式是否能正常運行
"""

def main():
    print("🧪 YouTube 下載器 - 簡單測試")
    print("=" * 40)
    
    # 1. 檢查 Python 版本
    import sys
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 版本過低")
        return False
    
    # 2. 檢查 Tkinter
    try:
        import tkinter as tk
        print("✅ Tkinter 可用")
    except ImportError:
        print("❌ Tkinter 不可用")
        return False
    
    # 3. 檢查基本模組
    try:
        import constants
        print(f"✅ constants: {constants.APP_TITLE}")
    except Exception as e:
        print(f"❌ constants: {e}")
        return False
    
    # 4. 檢查 URL 驗證
    try:
        from utils.validators import URLValidator
        test_url = "https://www.youtube.com/watch?v=test"
        is_valid = URLValidator.is_valid_url(test_url)
        platform = URLValidator.detect_platform(test_url)
        print(f"✅ URL驗證: {platform}")
    except Exception as e:
        print(f"❌ URL驗證: {e}")
        return False
    
    # 5. 檢查設定管理
    try:
        from services.settings import SettingsManager
        manager = SettingsManager()
        settings = manager.load_settings()
        print(f"✅ 設定管理: {len(settings)} 項")
    except Exception as e:
        print(f"❌ 設定管理: {e}")
        return False
    
    # 6. 檢查字體管理
    try:
        from utils.ui_fonts import FontManager
        root = tk.Tk()
        root.withdraw()
        font_manager = FontManager(root)
        print(f"✅ 字體管理: 大小 {font_manager.current_size}")
        root.destroy()
    except Exception as e:
        print(f"❌ 字體管理: {e}")
        return False
    
    # 7. 測試簡化GUI
    try:
        import simple_main
        app = simple_main.SimpleApp()
        print("✅ 簡化GUI: 創建成功")
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        print("✅ 簡化GUI: 測試完成")
    except Exception as e:
        print(f"❌ 簡化GUI: {e}")
        return False
    
    # 8. 測試完整應用程式
    try:
        import main
        app = main.MainApplication()
        print("✅ 完整應用: 創建成功")
        app.root.after(100, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        print("✅ 完整應用: 測試完成")
    except Exception as e:
        print(f"❌ 完整應用: {e}")
        print("詳細錯誤:")
        import traceback
        traceback.print_exc()
        return False
    
    # 9. 檢查可選依賴
    deps = {'yt_dlp': '下載功能', 'requests': 'HTTP請求'}
    available = 0
    
    for dep, desc in deps.items():
        try:
            __import__(dep)
            print(f"✅ {dep}: 已安裝")
            available += 1
        except ImportError:
            print(f"⚠️ {dep}: 未安裝 ({desc})")
    
    print(f"\n📊 測試結果:")
    print(f"✅ 核心功能: 全部正常")
    print(f"📦 可選依賴: {available}/{len(deps)} 可用")
    
    if available == len(deps):
        print("🎉 所有功能完全可用！")
    else:
        print("💡 基本功能可用，可安裝 yt-dlp 獲得完整功能")
    
    print(f"\n🚀 啟動方式:")
    print(f"  python start.py")
    print(f"  python main.py")
    print(f"  python simple_main.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎯 測試成功！應用程式可以使用！")
        else:
            print("\n🔧 測試失敗，需要檢查問題")
    except Exception as e:
        print(f"\n💥 測試異常: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按 Enter 鍵退出...")