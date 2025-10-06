#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部下載器頁面
三個連結、複製/開啟
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from constants import EXTERNAL_DOWNLOADERS, UI_TEXT
from utils.validators import URLValidator
from logging_config import get_logger

logger = get_logger(__name__)

class ExternalTab:
    """外部下載器頁面"""
    
    def __init__(self, parent, font_manager):
        self.parent = parent
        self.font_manager = font_manager
        self.frame = ttk.Frame(parent)
        
        # UI 變數
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
        
        # 說明文字
        desc_label = ttk.Label(main_frame, 
                              text="如果內建下載器無法使用，您可以嘗試以下線上下載工具：",
                              font=self.font_manager.get_font())
        desc_label.pack(pady=(0, 20))
        
        # URL 輸入區域
        self.create_url_input(main_frame)
        
        # 外部下載器列表
        self.create_downloader_list(main_frame)
        
        # 註冊字體
        self.font_manager.register_widget(title_label, 'large')
        self.font_manager.register_widget(desc_label)
        
    def create_url_input(self, parent):
        """創建 URL 輸入區域"""
        url_frame = ttk.LabelFrame(parent, text="視頻網址", padding=15)
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        # URL 輸入框
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, 
                                  font=self.font_manager.get_font())
        self.url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 按鈕框架
        button_frame = ttk.Frame(url_frame)
        button_frame.pack(fill=tk.X)
        
        # 貼上按鈕
        paste_btn = ttk.Button(button_frame, text="貼上", 
                              command=self.paste_url, width=10)
        paste_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空按鈕
        clear_btn = ttk.Button(button_frame, text="清空", 
                              command=self.clear_url, width=10)
        clear_btn.pack(side=tk.LEFT)
        
        # 複製按鈕
        copy_btn = ttk.Button(button_frame, text="複製網址", 
                             command=self.copy_url, width=12)
        copy_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 註冊字體
        self.font_manager.register_widget(self.url_entry)
        for btn in [paste_btn, clear_btn, copy_btn]:
            self.font_manager.register_widget(btn)
            
    def create_downloader_list(self, parent):
        """創建下載器列表"""
        list_frame = ttk.LabelFrame(parent, text="推薦的線上下載工具", padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        for key, downloader in EXTERNAL_DOWNLOADERS.items():
            self.create_downloader_item(list_frame, downloader)
            
    def create_downloader_item(self, parent, downloader):
        """創建單個下載器項目"""
        item_frame = ttk.Frame(parent)
        item_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 左側資訊
        info_frame = ttk.Frame(item_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 名稱
        name_label = ttk.Label(info_frame, text=downloader['name'], 
                              font=self.font_manager.get_font('bold'))
        name_label.pack(anchor=tk.W)
        
        # 描述
        desc_label = ttk.Label(info_frame, text=downloader['description'],
                              font=self.font_manager.get_font('small'))
        desc_label.pack(anchor=tk.W, pady=(2, 0))
        
        # URL
        url_label = ttk.Label(info_frame, text=downloader['url'],
                             font=self.font_manager.get_font('small'),
                             foreground="blue")
        url_label.pack(anchor=tk.W, pady=(2, 0))
        
        # 右側按鈕
        button_frame = ttk.Frame(item_frame)
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 複製連結按鈕
        copy_link_btn = ttk.Button(button_frame, text="複製連結", width=12,
                                  command=lambda url=downloader['url']: self.copy_link(url))
        copy_link_btn.pack(pady=(0, 5))
        
        # 開啟網站按鈕
        open_btn = ttk.Button(button_frame, text="開啟網站", width=12,
                             command=lambda url=downloader['url']: self.open_website(url))
        open_btn.pack(pady=(0, 5))
        
        # 帶網址開啟按鈕
        open_with_url_btn = ttk.Button(button_frame, text="帶網址開啟", width=12,
                                      command=lambda url=downloader['url']: self.open_with_url(url))
        open_with_url_btn.pack()
        
        # 分隔線
        separator = ttk.Separator(parent, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=(10, 0))
        
        # 註冊字體
        self.font_manager.register_widget(name_label, 'bold')
        self.font_manager.register_widget(desc_label, 'small')
        self.font_manager.register_widget(url_label, 'small')
        for btn in [copy_link_btn, open_btn, open_with_url_btn]:
            self.font_manager.register_widget(btn)
            
    def paste_url(self):
        """貼上 URL"""
        try:
            clipboard_text = self.frame.clipboard_get()
            if clipboard_text:
                self.url_var.set(clipboard_text.strip())
        except Exception as e:
            logger.warning(f"貼上失敗: {e}")
            
    def clear_url(self):
        """清空 URL"""
        self.url_var.set("")
        
    def copy_url(self):
        """複製 URL"""
        url = self.url_var.get().strip()
        if url:
            try:
                self.frame.clipboard_clear()
                self.frame.clipboard_append(url)
                messagebox.showinfo("成功", "網址已複製到剪貼板")
            except Exception as e:
                messagebox.showerror("錯誤", f"複製失敗: {e}")
        else:
            messagebox.showwarning("警告", "請先輸入網址")
            
    def copy_link(self, link_url):
        """複製連結"""
        try:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(link_url)
            messagebox.showinfo("成功", "連結已複製到剪貼板")
        except Exception as e:
            messagebox.showerror("錯誤", f"複製失敗: {e}")
            
    def open_website(self, website_url):
        """開啟網站"""
        try:
            webbrowser.open(website_url)
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟網站: {e}")
            
    def open_with_url(self, website_url):
        """帶網址開啟網站"""
        video_url = self.url_var.get().strip()
        
        if not video_url:
            messagebox.showwarning("警告", "請先輸入視頻網址")
            return
            
        if not URLValidator.is_valid_url(video_url):
            messagebox.showwarning("警告", "請輸入有效的視頻網址")
            return
            
        try:
            # 構建帶參數的 URL
            if '?' in website_url:
                full_url = f"{website_url}&url={video_url}"
            else:
                full_url = f"{website_url}?url={video_url}"
                
            webbrowser.open(full_url)
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟網站: {e}")