#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
其他下載分頁 UI
提供常用第三方網頁下載站捷徑，預設強行使用 Edge 瀏覽器開啟
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import webbrowser

class OtherDownloadsTab:
    """其他下載分頁類"""
    
    def __init__(self, parent, font_manager):
        self.font_manager = font_manager
        
        # 創建主分頁框架
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # 建立置中的外層容器
        container = ttk.Frame(self.frame)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 建立標籤框架
        self.label_frame = ttk.LabelFrame(container, text="外部網頁下載捷徑 (預設以 Edge 開啟)", padding=15)
        self.label_frame.pack(fill=tk.BOTH, expand=True)
        
        # 說明提示
        self.tip_label = ttk.Label(
            self.label_frame, 
            text="如果您遇到某些平台（如抖音、IG、FB Reels）因防爬蟲限制而下載失敗，\n"
                 "建議直接點擊下方按鈕，使用 Microsoft Edge 開啟第三方下載網站進行抓取：",
            justify=tk.LEFT,
            wraplength=450
        )
        self.tip_label.pack(fill=tk.X, pady=(0, 20))
        self.font_manager.register_widget(self.tip_label)
        
        # 捷徑清單定義
        shortcuts = [
            ("TikTokio 下載器 (TikTok)", "https://tiktokio.com/zh_tw/"),
            ("SnapAny 下載器 (Bilibili/抖音)", "https://snapany.com/zh-Hant/bilibili"),
            ("Threadster 下載器 (Threads)", "https://threadster.app/"),
            ("FDownloader 下載器 (FB Reels)", "https://fdownloader.net/zh-tw/facebook-reels-downloader")
        ]
        
        # 循環建立按鈕
        self.buttons = []
        for name, url in shortcuts:
            btn_frame = ttk.Frame(self.label_frame)
            btn_frame.pack(fill=tk.X, pady=6)
            
            # 使用 lambda 綁定參數
            btn = ttk.Button(
                btn_frame, 
                text=name, 
                command=lambda u=url: self.open_in_edge(u),
                width=35
            )
            btn.pack(side=tk.LEFT, ipady=4)
            self.font_manager.register_widget(btn)
            self.buttons.append(btn)
            
            # 顯示對應網址
            url_label = ttk.Label(btn_frame, text=url, foreground="#757575", font=('Arial', 9))
            url_label.pack(side=tk.LEFT, padx=(15, 0))
            self.font_manager.register_widget(url_label)
            
    def open_in_edge(self, url):
        """強行調用 Microsoft Edge 開啟 URL"""
        try:
            # 採用 Windows microsoft-edge 協定
            subprocess.Popen(f'start microsoft-edge:{url}', shell=True)
        except Exception:
            # 備用方案：使用系統預設瀏覽器
            webbrowser.open(url)
            
    def on_theme_changed(self, colors):
        """響應主題切換"""
        # 可以依據主題微調標籤顏色等
        pass
