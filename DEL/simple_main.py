#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版主程式
用於測試基本 GUI 功能
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SimpleApp:
    """簡化版應用程式"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        """設置視窗"""
        self.root.title("YouTube 下載器 - 測試版")
        self.root.geometry("500x400")
        self.root.minsize(450, 350)
        
    def setup_ui(self):
        """設置 UI"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 標題
        title_label = ttk.Label(main_frame, text="YouTube 下載器", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 字體控制
        font_frame = ttk.Frame(main_frame)
        font_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(font_frame, text="字體控制:").pack(side=tk.LEFT)
        ttk.Button(font_frame, text="A-", width=3, 
                  command=self.decrease_font).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(font_frame, text="A+", width=3, 
                  command=self.increase_font).pack(side=tk.LEFT)
        
        # 分頁控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 創建分頁
        self.create_download_tab()
        self.create_external_tab()
        self.create_history_tab()
        
        # 狀態列
        self.status_var = tk.StringVar(value="就緒")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X)
        
    def create_download_tab(self):
        """創建下載分頁"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="下載")
        
        # URL 輸入
        url_frame = ttk.LabelFrame(frame, text="視頻網址", padding=10)
        url_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var)
        url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 按鈕
        btn_frame = ttk.Frame(url_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="貼上", command=self.paste_url).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="清空", command=self.clear_url).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="測試下載", command=self.test_download).pack(side=tk.RIGHT)
        
        # 路徑選擇
        path_frame = ttk.LabelFrame(frame, text="下載設定", padding=10)
        path_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.path_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        path_entry.pack(fill=tk.X)
        
    def create_external_tab(self):
        """創建外部下載器分頁"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="外部下載器")
        
        ttk.Label(frame, text="外部下載器功能", 
                 font=('Arial', 14)).pack(pady=20)
        ttk.Label(frame, text="這裡將顯示外部下載工具連結").pack()
        
    def create_history_tab(self):
        """創建歷史記錄分頁"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="歷史記錄")
        
        ttk.Label(frame, text="歷史記錄功能", 
                 font=('Arial', 14)).pack(pady=20)
        ttk.Label(frame, text="這裡將顯示下載歷史").pack()
        
    def paste_url(self):
        """貼上 URL"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_var.set(clipboard_text)
            self.status_var.set("已貼上網址")
        except:
            self.status_var.set("剪貼板為空")
            
    def clear_url(self):
        """清空 URL"""
        self.url_var.set("")
        self.status_var.set("已清空網址")
        
    def test_download(self):
        """測試下載功能"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("警告", "請輸入網址")
            return
            
        # 簡單的 URL 驗證
        if not (url.startswith('http://') or url.startswith('https://')):
            messagebox.showwarning("警告", "請輸入有效的網址")
            return
            
        messagebox.showinfo("測試", f"測試下載功能\n網址: {url[:50]}...")
        self.status_var.set("測試下載功能")
        
    def increase_font(self):
        """增大字體"""
        self.status_var.set("字體已增大")
        
    def decrease_font(self):
        """減小字體"""
        self.status_var.set("字體已減小")
        
    def run(self):
        """運行應用程式"""
        self.root.mainloop()

def main():
    """主函數"""
    try:
        print("啟動簡化版 YouTube 下載器...")
        app = SimpleApp()
        app.run()
    except Exception as e:
        print(f"啟動失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()