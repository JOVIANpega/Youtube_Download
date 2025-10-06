#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本功能測試
測試核心模組是否能正常導入和運行
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """測試基本導入"""
    print("=== 測試基本模組導入 ===")
    
    # 測試常數模組
    try:
        import constants
        print("✓ constants 導入成功")
        print(f"  APP_TITLE: {constants.APP_TITLE}")
        print(f"  WINDOW_SIZE: {constants.WINDOW_SIZE}")
    except Exception as e:
        print(f"✗ constants 導入失敗: {e}")
        return False
        
    # 測試版本資訊
    try:
        import version_info
        print("✓ version_info 導入成功")
        print(f"  VERSION: {version_info.VERSION}")
    except Exception as e:
        print(f"✗ version_info 導入失敗: {e}")
        return False
        
    # 測試日誌配置
    try:
        import logging_config
        logger = logging_config.setup_logging()
        print("✓ logging_config 導入成功")
        logger.info("測試日誌訊息")
    except Exception as e:
        print(f"✗ logging_config 導入失敗: {e}")
        return False
        
    return True

def test_utils():
    """測試工具模組"""
    print("\n=== 測試工具模組 ===")
    
    # 測試路徑工具
    try:
        from utils.path_utils import get_resource_path, sanitize_filename
        test_path = get_resource_path("test.txt")
        clean_name = sanitize_filename("test<>file.txt")
        print("✓ utils.path_utils 導入成功")
        print(f"  測試路徑: {test_path}")
        print(f"  清理檔名: {clean_name}")
    except Exception as e:
        print(f"✗ utils.path_utils 導入失敗: {e}")
        return False
        
    # 測試驗證器
    try:
        from utils.validators import URLValidator
        test_url = "https://www.youtube.com/watch?v=test"
        is_valid = URLValidator.is_valid_url(test_url)
        platform = URLValidator.detect_platform(test_url)
        print("✓ utils.validators 導入成功")
        print(f"  URL 有效性: {is_valid}")
        print(f"  檢測平台: {platform}")
    except Exception as e:
        print(f"✗ utils.validators 導入失敗: {e}")
        return False
        
    return True

def test_services():
    """測試服務模組"""
    print("\n=== 測試服務模組 ===")
    
    # 測試設定管理
    try:
        from services.settings import SettingsManager
        settings_manager = SettingsManager()
        settings = settings_manager.load_settings()
        print("✓ services.settings 導入成功")
        print(f"  設定項目數: {len(settings)}")
    except Exception as e:
        print(f"✗ services.settings 導入失敗: {e}")
        return False
        
    # 測試歷史記錄
    try:
        from services.history_store import HistoryStore
        history_store = HistoryStore()
        history = history_store.load_history()
        print("✓ services.history_store 導入成功")
        print(f"  歷史記錄數: {len(history)}")
    except Exception as e:
        print(f"✗ services.history_store 導入失敗: {e}")
        return False
        
    return True

def test_tkinter():
    """測試 Tkinter"""
    print("\n=== 測試 Tkinter ===")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # 創建測試視窗
        root = tk.Tk()
        root.title("測試視窗")
        root.geometry("300x200")
        
        # 添加一些控件
        label = ttk.Label(root, text="測試標籤")
        label.pack(pady=10)
        
        button = ttk.Button(root, text="測試按鈕", command=root.quit)
        button.pack(pady=10)
        
        print("✓ Tkinter 可用")
        print("  測試視窗已創建（將自動關閉）")
        
        # 自動關閉視窗
        root.after(1000, root.quit)  # 1秒後關閉
        root.mainloop()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Tkinter 測試失敗: {e}")
        return False

def test_font_manager():
    """測試字體管理器"""
    print("\n=== 測試字體管理器 ===")
    
    try:
        import tkinter as tk
        from utils.ui_fonts import FontManager
        
        root = tk.Tk()
        root.withdraw()  # 隱藏視窗
        
        font_manager = FontManager(root)
        print("✓ FontManager 創建成功")
        print(f"  當前字體大小: {font_manager.current_size}")
        
        # 測試字體調整
        font_manager.increase_font()
        print(f"  增大後字體大小: {font_manager.current_size}")
        
        font_manager.decrease_font()
        print(f"  減小後字體大小: {font_manager.current_size}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ FontManager 測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("YouTube 下載器 - 基本功能測試")
    print("=" * 50)
    
    all_passed = True
    
    # 依序測試各個模組
    tests = [
        test_basic_imports,
        test_utils,
        test_services,
        test_tkinter,
        test_font_manager,
    ]
    
    for test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"✗ 測試 {test_func.__name__} 時發生異常: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有基本測試通過！")
        print("可以嘗試運行主程式: python main.py")
    else:
        print("✗ 部分測試失敗，需要修復問題")
    
    return all_passed

if __name__ == "__main__":
    main()