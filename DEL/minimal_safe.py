#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小安全版 YouTube 下載器
絕對無依賴問題的版本
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

class MinimalSafeApp:
    """最小安全應用程式"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        """設置視窗"""
        self.root.title("YouTube 下載器 - 最小安全版")
        self.root.geometry("500x400")
        self.root.minsize(400, 300)
        
    def setup_ui(self):
        """設置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 標題
        title = ttk.Label(main_frame, text="YouTube 下載器", 
                         font=('Arial', 18, 'bold'))
        title.pack(pady=(0, 20))
        
        # 狀態信息
        status_text = """
🎉 應用程式運行正常！

✅ 基本功能：
• GUI 界面正常
• Python 環境正常
• Tkinter 可用

🔧 下一步：
1. 測試基本功能
2. 檢查依賴狀態
3. 安裝完整功能
        """
        
        status_label = ttk.Label(main_frame, text=status_text, 
                               justify=tk.LEFT, font=('Arial', 10))
        status_label.pack(pady=(0, 20))
        
        # 按鈕區域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 測試按鈕
        test_btn = ttk.Button(btn_frame, text="測試基本功能", 
                             command=self.test_function)
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 檢查依賴按鈕
        deps_btn = ttk.Button(btn_frame, text="檢查依賴", 
                             command=self.check_dependencies)
        deps_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 關閉按鈕
        close_btn = ttk.Button(btn_frame, text="關閉", 
                              command=self.root.quit)
        close_btn.pack(side=tk.RIGHT)
        
        # 狀態列
        self.status_var = tk.StringVar(value="最小安全版就緒")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def test_function(self):
        """測試基本功能"""
        try:
            # 測試 Python 版本
            version = sys.version_info
            python_version = f"{version.major}.{version.minor}.{version.micro}"
            
            # 測試 Tkinter
            test_window = tk.Toplevel(self.root)
            test_window.title("測試視窗")
            test_window.geometry("300x200")
            
            ttk.Label(test_window, text="✅ Tkinter 功能正常").pack(pady=20)
            ttk.Button(test_window, text="關閉", 
                      command=test_window.destroy).pack(pady=10)
            
            self.status_var.set("✅ 基本功能測試通過")
            
            messagebox.showinfo("測試結果", 
                              f"✅ 基本功能正常\n\n"
                              f"Python 版本: {python_version}\n"
                              f"Tkinter: 可用\n"
                              f"GUI: 正常")
                              
        except Exception as e:
            self.status_var.set(f"❌ 測試失敗: {e}")
            messagebox.showerror("測試失敗", f"基本功能測試失敗:\n{e}")
    
    def check_dependencies(self):
        """檢查依賴"""
        deps_info = []
        
        # 檢查 Python 版本
        version = sys.version_info
        if version.major >= 3 and version.minor >= 7:
            deps_info.append("✅ Python 版本符合要求")
        else:
            deps_info.append("❌ Python 版本過低")
        
        # 檢查可選依賴
        optional_deps = {
            'yt_dlp': '視頻下載核心',
            'requests': 'HTTP 請求功能'
        }
        
        for dep, desc in optional_deps.items():
            try:
                __import__(dep)
                deps_info.append(f"✅ {dep} - {desc}")
            except ImportError:
                deps_info.append(f"❌ {dep} - {desc} (未安裝)")
        
        # 顯示結果
        result = "依賴檢查結果:\n\n" + "\n".join(deps_info)
        result += "\n\n💡 安裝完整功能:\npip install yt-dlp requests"
        
        messagebox.showinfo("依賴檢查", result)
        self.status_var.set("依賴檢查完成")
        
    def run(self):
        """運行應用程式"""
        self.root.mainloop()

def main():
    """主函數"""
    try:
        print("🚀 啟動最小安全版 YouTube 下載器...")
        app = MinimalSafeApp()
        print("✅ 應用程式創建成功")
        app.run()
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        input("按 Enter 鍵退出...")

if __name__ == "__main__":
    main()