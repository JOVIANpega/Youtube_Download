#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全版主程式
避免所有可能的依賴問題
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 導入安全的模組
from constants import APP_TITLE, WINDOW_SIZE, MIN_WINDOW_SIZE
import version_info

class SafeMainApplication:
    """安全版主應用程式"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        """設置主視窗"""
        self.root.title(f"{APP_TITLE} v{version_info.VERSION} (安全版)")
        self.root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.root.minsize(*MIN_WINDOW_SIZE)
        
    def setup_ui(self):
        """設置用戶介面"""
        # 創建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 標題
        title_label = ttk.Label(main_frame, text=f"{APP_TITLE} (安全版)", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 說明文字
        info_text = """
這是安全版本，避免了所有複雜依賴問題。

✅ 可用功能：
• 基本GUI界面測試
• 環境檢查
• 設定驗證

🔧 要獲得完整功能，請：
1. 安裝依賴：pip install yt-dlp
2. 使用完整版：python main.py
3. 或使用修復版：python main_fixed.py
        """
        
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # 按鈕框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 測試按鈕
        test_btn = ttk.Button(button_frame, text="測試基本功能", 
                             command=self.test_basic)
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 檢查依賴按鈕
        deps_btn = ttk.Button(button_frame, text="檢查依賴", 
                             command=self.check_deps)
        deps_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 關閉按鈕
        close_btn = ttk.Button(button_frame, text="關閉", 
                              command=self.root.quit)
        close_btn.pack(side=tk.RIGHT)
        
        # 狀態標籤
        self.status_var = tk.StringVar(value="安全版就緒")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X)
        
    def test_basic(self):
        """測試基本功能"""
        try:
            # 測試基本模組
            import constants
            import version_info
            
            self.status_var.set("✅ 基本功能測試通過")
            messagebox.showinfo("測試結果", 
                              f"✅ 基本功能正常\n"
                              f"應用標題: {constants.APP_TITLE}\n"
                              f"版本: {version_info.VERSION}\n"
                              f"視窗大小: {constants.WINDOW_SIZE}")
        except Exception as e:
            self.status_var.set(f"❌ 測試失敗: {e}")
            messagebox.showerror("測試失敗", f"基本功能測試失敗:\n{e}")
    
    def check_deps(self):
        """檢查依賴"""
        deps = {
            'yt_dlp': '下載核心功能',
            'requests': 'HTTP請求功能',
        }
        
        available = []
        missing = []
        
        for dep, desc in deps.items():
            try:
                __import__(dep)
                available.append(f"✅ {dep} - {desc}")
            except ImportError:
                missing.append(f"❌ {dep} - {desc}")
        
        result = "依賴檢查結果:\n\n"
        if available:
            result += "已安裝:\n" + "\n".join(available) + "\n\n"
        if missing:
            result += "未安裝:\n" + "\n".join(missing) + "\n\n"
            result += "安裝指令:\npip install yt-dlp requests"
        
        messagebox.showinfo("依賴檢查", result)
        
    def run(self):
        """運行應用程式"""
        self.root.mainloop()

def main():
    """主函數"""
    try:
        print("🚀 啟動安全版 YouTube 下載器...")
        app = SafeMainApplication()
        app.run()
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()