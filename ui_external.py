#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部下載器頁面
三個連結、複製/開啟
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from utils.ui_fonts import FontManager

class ExternalTab:
    """外部下載器頁面"""
    
    def __init__(self, parent, font_manager):
        self.parent = parent
        self.font_manager = font_manager
        self.frame = ttk.Frame(parent)
        self.url_var = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        """設置用戶介面"""
        # 主容器
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 標題
        title_label = ttk.Label(main_frame, text="外部下載器", 
                               font=self.font_manager.get_font('large'))
        title_label.pack(pady=(0, 20))
        
        # 網址輸入區
        url_frame = ttk.LabelFrame(main_frame, text="視訊網址", padding=10)
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        url_row = ttk.Frame(url_frame)
        url_row.pack(fill=tk.X)
        
        self.url_entry = ttk.Entry(url_row, textvariable=self.url_var)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        paste_btn = ttk.Button(url_row, text="貼上", command=self.paste_url, width=8)
        paste_btn.pack(side=tk.LEFT, padx=2)
        
        clear_btn = ttk.Button(url_row, text="清空", command=self.clear_url, width=8)
        clear_btn.pack(side=tk.LEFT)
        
        # 外部工具區
        tools_frame = ttk.LabelFrame(main_frame, text="推薦下載網站", padding=10)
        tools_frame.pack(fill=tk.X)
        
        sites = [
            ("SaveFrom.net", "https://savefrom.net/"),
            ("Y2mate.com", "https://y2mate.com/"),
            ("SnapTube", "https://www.snaptubeapp.com/")
        ]
        
        for name, url in sites:
            site_frame = ttk.Frame(tools_frame)
            site_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(site_frame, text=name, width=15).pack(side=tk.LEFT)
            
            open_btn = ttk.Button(site_frame, text="開啟網站", 
                                 command=lambda u=url: webbrowser.open(u))
            open_btn.pack(side=tk.LEFT, padx=5)
            
            search_btn = ttk.Button(site_frame, text="帶網址開啟", 
                                   command=lambda u=url: self.open_with_url(u))
            search_btn.pack(side=tk.LEFT)
            
            self.font_manager.register_widget(open_btn)
            self.font_manager.register_widget(search_btn)
        
        # 註冊字體
        self.font_manager.register_widget(title_label, 'large')
        self.font_manager.register_widget(self.url_entry)
        self.font_manager.register_widget(paste_btn)
        self.font_manager.register_widget(clear_btn)
        
    def paste_url(self):
        """貼上 URL"""
        try:
            self.url_var.set(self.frame.clipboard_get().strip())
        except Exception:
            pass
            
    def clear_url(self):
        """清空 URL"""
        self.url_var.set("")
        
    def open_with_url(self, base_url):
        """帶網址開啟外部網站"""
        video_url = self.url_var.get().strip()
        if not video_url:
            messagebox.showwarning("警告", "請先輸入或貼上視訊網址")
            return
            
        # 某些網站支持通過 URL 參數傳遞網址
        if "savefrom.net" in base_url:
            target = f"https://en.savefrom.net/1-youtube-video-downloader-356/?url={video_url}"
        elif "y2mate.com" in base_url:
            # y2mate 好像不支持直接 params，只能跳轉到主頁
            target = base_url
            self.frame.clipboard_clear()
            self.frame.clipboard_append(video_url)
            messagebox.showinfo("提示", "已將網址複製到剪貼簿，請在網站中貼上。")
        else:
            target = base_url
            
        webbrowser.open(target)