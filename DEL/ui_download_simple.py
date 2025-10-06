#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版下載頁面UI
僅包含基本功能，避免複雜依賴
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import webbrowser

from constants import UI_TEXT, ERROR_MESSAGES, QUALITY_OPTIONS, FILENAME_PREFIXES
from utils.validators import URLValidator, PlaceholderManager

class DownloadTabSimple:
    """簡化版下載頁面"""
    
    def __init__(self, parent, font_manager, settings_manager):
        self.parent = parent
        self.font_manager = font_manager
        self.settings_manager = settings_manager
        self.frame = ttk.Frame(parent)
        
        # UI 變數
        self.url_var = tk.StringVar()
        self.download_path_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="best")
        self.prefix_var = tk.StringVar()
        self.message_var = tk.StringVar()
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """設置用戶介面"""
        # 主容器
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # URL 輸入區域
        self.create_url_section(main_frame)
        
        # 下載路徑區域
        self.create_path_section(main_frame)
        
        # 訊息條
        self.create_message_section(main_frame)
        
        # 主按鈕區域
        self.create_button_section(main_frame)
        
    def create_url_section(self, parent):
        """創建 URL 輸入區域"""
        url_frame = ttk.LabelFrame(parent, text="視頻網址", padding=10)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        # URL 輸入框
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, 
                                  font=self.font_manager.get_font())
        self.url_entry.pack(fill=tk.X, pady=(0, 5))
        
        # 設置佔位符
        self.url_placeholder = PlaceholderManager(
            self.url_entry, 
            UI_TEXT['url_placeholder']
        )
        
        # 按鈕框架
        url_buttons_frame = ttk.Frame(url_frame)
        url_buttons_frame.pack(fill=tk.X)
        
        # 貼上按鈕
        paste_btn = ttk.Button(url_buttons_frame, text="貼上", 
                              command=self.paste_url, width=8)
        paste_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 清空按鈕
        clear_btn = ttk.Button(url_buttons_frame, text="清空", 
                              command=self.clear_url, width=8)
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 在瀏覽器中開啟按鈕
        open_btn = ttk.Button(url_buttons_frame, text="瀏覽器開啟", 
                             command=self.open_in_browser, width=12)
        open_btn.pack(side=tk.RIGHT)
        
        # 註冊字體
        self.font_manager.register_widget(self.url_entry)
        for btn in [paste_btn, clear_btn, open_btn]:
            self.font_manager.register_widget(btn)
            
    def create_path_section(self, parent):
        """創建下載路徑區域"""
        path_frame = ttk.LabelFrame(parent, text="下載設定", padding=10)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 下載路徑
        path_row = ttk.Frame(path_frame)
        path_row.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(path_row, text=UI_TEXT['download_path_label']).pack(side=tk.LEFT)
        
        self.path_entry = ttk.Entry(path_row, textvariable=self.download_path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        browse_btn = ttk.Button(path_row, text=UI_TEXT['browse_button'], 
                               command=self.browse_download_path, width=10)
        browse_btn.pack(side=tk.RIGHT)
        
        # 檔名前綴和品質
        options_row = ttk.Frame(path_frame)
        options_row.pack(fill=tk.X)
        
        ttk.Label(options_row, text="檔名前綴：").pack(side=tk.LEFT)
        
        self.prefix_combo = ttk.Combobox(options_row, textvariable=self.prefix_var, 
                                        values=FILENAME_PREFIXES, width=15)
        self.prefix_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(options_row, text="品質：").pack(side=tk.LEFT)
        
        self.quality_combo = ttk.Combobox(options_row, textvariable=self.quality_var,
                                         values=[option[0] for option in QUALITY_OPTIONS],
                                         state="readonly", width=12)
        self.quality_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.quality_combo.set(QUALITY_OPTIONS[0][0])
        
        # 註冊字體
        for widget in [self.path_entry, browse_btn, self.prefix_combo, self.quality_combo]:
            self.font_manager.register_widget(widget)
            
    def create_message_section(self, parent):
        """創建訊息條"""
        self.message_frame = ttk.Frame(parent)
        self.message_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.message_label = ttk.Label(self.message_frame, textvariable=self.message_var,
                                      foreground="blue", font=self.font_manager.get_font())
        self.message_label.pack(side=tk.LEFT)
        
        # 隱藏訊息框架
        self.message_frame.pack_forget()
        
    def create_button_section(self, parent):
        """創建主按鈕區域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 主下載按鈕（簡化版）
        self.download_btn = ttk.Button(button_frame, text="測試下載功能",
                                      command=self.test_download, style="Accent.TButton")
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 驗證按鈕
        self.validate_btn = ttk.Button(button_frame, text="驗證網址",
                                      command=self.validate_url)
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 設定按鈕
        self.settings_btn = ttk.Button(button_frame, text="保存設定",
                                      command=self.save_current_settings)
        self.settings_btn.pack(side=tk.RIGHT)
        
        # 註冊字體
        for btn in [self.download_btn, self.validate_btn, self.settings_btn]:
            self.font_manager.register_widget(btn)
            
    def load_settings(self):
        """載入設定"""
        try:
            settings = self.settings_manager.load_settings()
            
            # 載入下載路徑
            download_path = settings.get('download_path', '')
            if download_path and os.path.exists(download_path):
                self.download_path_var.set(download_path)
            else:
                # 使用預設路徑
                default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
                self.download_path_var.set(default_path)
                
            # 載入其他設定
            self.quality_var.set(settings.get('quality_preference', 'best'))
            self.prefix_var.set(settings.get('filename_prefix', ''))
            
        except Exception as e:
            print(f"載入設定失敗: {e}")
            
    def save_current_settings(self):
        """保存當前設定"""
        try:
            settings = {
                'download_path': self.download_path_var.get(),
                'quality_preference': self.quality_var.get(),
                'filename_prefix': self.prefix_var.get(),
            }
            self.settings_manager.update_settings(settings)
            self.show_message("設定已保存", "success")
        except Exception as e:
            self.show_message(f"保存設定失敗: {e}", "error")
            
    def paste_url(self):
        """貼上 URL"""
        try:
            clipboard_text = self.frame.clipboard_get()
            if clipboard_text:
                self.url_placeholder.set_value(clipboard_text.strip())
                self.validate_url()
        except Exception:
            pass
            
    def clear_url(self):
        """清空 URL"""
        self.url_placeholder.clear()
        self.show_message("", "")
        
    def open_in_browser(self):
        """在瀏覽器中開啟 URL"""
        url = self.url_placeholder.get_value()
        if url and URLValidator.is_valid_url(url):
            try:
                webbrowser.open(url)
                self.show_message("已在瀏覽器中開啟", "success")
            except Exception as e:
                self.show_message(f"開啟瀏覽器失敗: {e}", "error")
        else:
            self.show_message("請輸入有效的 URL", "error")
            
    def browse_download_path(self):
        """瀏覽下載路徑"""
        current_path = self.download_path_var.get()
        if not current_path:
            current_path = os.path.expanduser('~')
            
        path = filedialog.askdirectory(
            title="選擇下載路徑",
            initialdir=current_path
        )
        
        if path:
            self.download_path_var.set(path)
            self.save_current_settings()
            
    def validate_url(self):
        """驗證 URL"""
        url = self.url_placeholder.get_value()
        if not url:
            self.show_message("", "")
            return
            
        if URLValidator.is_valid_url(url):
            platform = URLValidator.detect_platform(url)
            if platform:
                self.show_message(f"✅ 檢測到 {platform} 視頻", "success")
            else:
                self.show_message("✅ URL 格式有效", "success")
        else:
            self.show_message("❌ URL 格式無效", "error")
            
    def test_download(self):
        """測試下載功能"""
        url = self.url_placeholder.get_value()
        if not url:
            self.show_message(ERROR_MESSAGES['invalid_url'], "error")
            return
            
        if not URLValidator.is_valid_url(url):
            self.show_message(ERROR_MESSAGES['invalid_url'], "error")
            return
            
        download_path = self.download_path_var.get()
        if not download_path:
            self.show_message(ERROR_MESSAGES['no_download_path'], "error")
            return
            
        # 簡化版只做驗證，不實際下載
        platform = URLValidator.detect_platform(url)
        quality = self.quality_var.get()
        prefix = self.prefix_var.get()
        
        info_msg = f"測試下載設定:\n"
        info_msg += f"平台: {platform or '未知'}\n"
        info_msg += f"品質: {quality}\n"
        info_msg += f"路徑: {download_path}\n"
        if prefix:
            info_msg += f"前綴: {prefix}\n"
        info_msg += f"\n注意: 這是簡化版，僅驗證設定。\n要實際下載請安裝 yt-dlp 並使用完整版。"
        
        messagebox.showinfo("下載測試", info_msg)
        self.show_message("下載設定驗證完成", "success")
        
    def show_message(self, message, msg_type="info"):
        """顯示訊息"""
        if not message:
            self.message_frame.pack_forget()
            return
            
        self.message_var.set(message)
        
        # 設置顏色
        colors = {
            "info": "blue",
            "success": "green",
            "warning": "orange",
            "error": "red"
        }
        self.message_label.config(foreground=colors.get(msg_type, "blue"))
        
        # 顯示訊息框架
        self.message_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 自動隱藏（除了錯誤訊息）
        if msg_type != "error":
            self.frame.after(3000, lambda: self.show_message("", ""))
            
    def get_download_path(self):
        """獲取下載路徑"""
        return self.download_path_var.get()
        
    def cleanup(self):
        """清理資源"""
        pass  # 簡化版無需清理