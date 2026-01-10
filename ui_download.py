#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載頁面UI
網址區、下載路徑、訊息條、主按鈕、進度/控制/日誌
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import time
import threading
import webbrowser
import subprocess
from datetime import datetime
from typing import Optional

from constants import UI_TEXT, STATUS_MESSAGES, ERROR_MESSAGES, SUCCESS_MESSAGES, QUALITY_OPTIONS, FILENAME_PREFIXES, reload_filename_prefixes
from utils.validators import URLValidator, PlaceholderManager, InputValidator
import glob
import platform
from logging_config import get_logger
from services.downloader import VideoDownloader, DownloadStatus
from services.history_store import HistoryStore
from utils.threading_utils import CancellationToken

logger = get_logger(__name__)

class DownloadTab:
    """下載頁面"""
    
    def __init__(self, parent, font_manager, settings_manager, history_store=None):
        self.parent = parent
        self.font_manager = font_manager
        self.settings_manager = settings_manager
        self.history_store = history_store or HistoryStore()
        self.frame = ttk.Frame(parent)
        
        # 狀態
        self.is_downloading = False
        self.show_advanced = False
        self.cancel_requested = False
        self.cancellation_token = None
        self.current_downloader = None
        
        # UI 變數
        self.url_var = tk.StringVar()
        self.download_path_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="best")
        self.prefix_var = tk.StringVar()
        self.browser_var = tk.StringVar(value="none")
        self.progress_var = tk.DoubleVar()
        self.message_var = tk.StringVar()
        
        self.show_full_log_var = tk.BooleanVar(value=False)
        self.quick_link_var = tk.StringVar()
        
        self.setup_ui()
        self.setup_callbacks()
        self.load_settings()
        
    def _create_gui_logger(self):
        """建立一個將 yt-dlp 日誌輸出到 GUI 的 logger 物件"""
        tab = self
        class _GuiLogger:
            def debug(self, msg):
                # 捕獲所有 debug 訊息（包含 yt-dlp 的即時進度細節）
                try:
                    tab.frame.after(0, lambda: tab.log_to_status(msg))
                except Exception:
                    pass
            def info(self, msg):
                try:
                    tab.frame.after(0, lambda: tab.log_to_status(msg))
                except Exception:
                    pass
            def warning(self, msg):
                try:
                    tab.frame.after(0, lambda: tab.log_to_status(f"[WARN] {msg}"))
                except Exception:
                    pass
            def error(self, msg):
                try:
                    tab.frame.after(0, lambda: tab.log_to_status(f"[ERROR] {msg}"))
                except Exception:
                    pass
        return _GuiLogger()

    def setup_ui(self):
        """設置用戶介面"""
        # 主容器
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 集中擺放設定零件容器
        config_container = ttk.LabelFrame(main_frame, text="下載任務設定", padding=10)
        config_container.pack(fill=tk.X, pady=(0, 5))
        
        # URL 輸入區域 (併入容器)
        self.create_url_section(config_container)
        
        # 下載路徑與參數區域 (併入容器)
        self.create_path_section(config_container)
        
        # 主操作按鈕 (併入容器或緊跟其後)
        self.create_button_section(config_container)
        
        # 訊息條
        self.create_message_section(main_frame)
        
        # 進度區域 (保持原樣顯示)
        self.create_progress_section(main_frame)
        
        # 進階設定 (由設定分頁控制，此處通常不展開)
        self.create_advanced_section(main_frame)
        
    def create_url_section(self, parent):
        """創建 URL 輸入區域"""
        url_frame = ttk.Frame(parent)
        url_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 第一排：網址標籤 + 輸入框
        url_row = ttk.Frame(url_frame)
        url_row.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(url_row, text="影片網址:", width=10).pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_row, textvariable=self.url_var, font=self.font_manager.get_font())
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 設置佔位符
        self.url_placeholder = PlaceholderManager(self.url_entry, UI_TEXT['url_placeholder'])
        
        # 第二排：操作按鈕與快速連結
        btn_row = ttk.Frame(url_frame)
        btn_row.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(btn_row, text="", width=10).pack(side=tk.LEFT)
        
        paste_btn = ttk.Button(btn_row, text="貼上", command=self.paste_url, width=6)
        paste_btn.pack(side=tk.LEFT, padx=(0, 2))
        copy_btn = ttk.Button(btn_row, text="複製", command=self.copy_url, width=6)
        copy_btn.pack(side=tk.LEFT, padx=(0, 2))
        clear_btn = ttk.Button(btn_row, text="清空", command=self.clear_url, width=6)
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(btn_row, text="快速選單:").pack(side=tk.LEFT)
        self.quick_link_combo = ttk.Combobox(btn_row, textvariable=self.quick_link_var, 
                                            values=self.get_quick_links_list(), state="readonly", width=12)
        self.quick_link_combo.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.quick_link_combo.bind("<<ComboboxSelected>>", self.on_quick_link_selected)
        
        edit_btn = ttk.Button(btn_row, text="編輯", command=self.edit_quick_links, width=6)
        edit_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        open_btn = ttk.Button(btn_row, text="瀏覽器開啟", command=self.open_in_browser, width=12)
        open_btn.pack(side=tk.RIGHT)
        
        # 註冊字體
        self.font_manager.register_widget(self.url_entry)
        for btn in [paste_btn, copy_btn, clear_btn, open_btn, self.quick_link_combo, edit_btn]:
            self.font_manager.register_widget(btn)

    def create_path_section(self, parent):
        """創建下載設定區域 (緊湊版)"""
        path_frame = ttk.Frame(parent)
        path_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 第三排：儲存路徑
        path_row = ttk.Frame(path_frame)
        path_row.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(path_row, text="儲存路徑:", width=10).pack(side=tk.LEFT)
        self.path_entry = ttk.Entry(path_row, textvariable=self.download_path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(path_row, text="瀏覽", command=self.browse_download_path, width=6)
        browse_btn.pack(side=tk.LEFT, padx=(0, 2))
        open_folder_btn = ttk.Button(path_row, text="打開", command=self.open_download_folder, width=6)
        open_folder_btn.pack(side=tk.LEFT)

        # 第四排：多項設定橫向排列
        row4 = ttk.Frame(path_frame)
        row4.pack(fill=tk.X, pady=(2, 2))
        
        ttk.Label(row4, text="下載前綴:", width=10).pack(side=tk.LEFT)
        self.prefix_combo = ttk.Combobox(row4, textvariable=self.prefix_var,
                                        values=self.get_prefix_options(), width=10)
        self.prefix_combo.pack(side=tk.LEFT, padx=(0, 5))
        reload_btn = ttk.Button(row4, text="🔃", command=self.reload_prefix_list, width=3)
        reload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(row4, text="畫質:").pack(side=tk.LEFT)
        self.quality_combo = ttk.Combobox(row4, textvariable=self.quality_var,
                                         values=[option[0] for option in QUALITY_OPTIONS],
                                         state="readonly", width=8)
        self.quality_combo.pack(side=tk.LEFT, padx=(2, 10))
        
        ttk.Label(row4, text="Cookies 授權(會員/限制影片):").pack(side=tk.LEFT)
        browser_options = ['不使用', 'Chrome', 'Edge', 'Firefox', 'Opera', 'Brave', 'Safari']
        self.browser_combo = ttk.Combobox(row4, textvariable=self.browser_var,
                                         values=browser_options, state="readonly", width=8)
        self.browser_combo.pack(side=tk.LEFT, padx=(2, 0))
        
        # 註冊字體
        for widget in [self.path_entry, browse_btn, self.prefix_combo, self.quality_combo, reload_btn, self.browser_combo, open_folder_btn]:
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
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 主下載按鈕
        self.download_btn = ttk.Button(button_frame, text=UI_TEXT['download_button'],
                                      command=self.start_download, style="Accent.TButton", width=18)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=5)
        
        # 取消按鈕
        self.cancel_btn = ttk.Button(button_frame, text=UI_TEXT['cancel_button'],
                                     command=self.cancel_download, state=tk.DISABLED, width=18)
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=5)
        
        # 進階選項按鈕移至設定分頁；此處不再顯示（保留屬性為 None 以相容）
        self.advanced_btn = None
        
        # 註冊字體
        for btn in [self.download_btn, self.cancel_btn]:
            self.font_manager.register_widget(btn)
            
    def create_progress_section(self, parent):
        """創建進度區域"""
        self.progress_frame = ttk.LabelFrame(parent, text="下載狀態", padding=10)
        # 初始隱藏
        
        # 即時狀態顯示框 (Dashboard Info)
        self.progress_display_container = ttk.Frame(self.progress_frame)
        self.progress_display_container.pack(fill=tk.X, pady=(0, 5))
        
        # 資訊標籤 (用於顯示當前檔案、速度、ETA)
        self.info_label = ttk.Label(self.progress_display_container, 
                                   text="準備就緒...", 
                                   font=self.font_manager.get_font(),
                                   foreground="#003366")
        self.info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 詳細日誌核取方塊
        full_log_cb = ttk.Checkbutton(self.progress_display_container, text="詳細日誌", 
                                     variable=self.show_full_log_var)
        full_log_cb.pack(side=tk.RIGHT)
        
        # 清空日誌按鈕
        clear_log_btn = ttk.Button(self.progress_display_container, text="清空", 
                                  command=self.clear_log, width=5)
        clear_log_btn.pack(side=tk.RIGHT, padx=(5, 5))
        
        # 複製檔名按鈕
        self.copy_name_btn = ttk.Button(self.progress_display_container, text="複製名稱", 
                                  command=self.copy_current_filename, width=8)
        self.copy_name_btn.pack(side=tk.RIGHT)

        self.font_manager.register_widget(full_log_cb)
        self.font_manager.register_widget(clear_log_btn)
        self.font_manager.register_widget(self.copy_name_btn)
        
        # 狀態顯示區域（滾動日誌）
        status_frame = ttk.Frame(self.progress_frame)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        
        # 使用 Text 控件顯示多行狀態信息 (Log)
        from tkinter import scrolledtext
        self.status_text = scrolledtext.ScrolledText(status_frame, 
                                                   height=10, 
                                                   width=80,
                                                   font=self.font_manager.get_font('monospace'),
                                                   state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 設置強調標籤
        self.status_text.tag_configure("highlight", background="yellow", foreground="black")
        self.status_text.tag_configure("title", background="#ADD8E6", foreground="#000080")
        self.status_text.tag_configure("error", foreground="red")
        self.status_text.tag_configure("success", foreground="green")
        
        # 初始化顯示
        # self.log_to_status(STATUS_MESSAGES['ready'])
        
        # 註冊字體
        self.font_manager.register_widget(self.status_text, 'monospace')
        self.font_manager.register_widget(self.info_label)
        
        # 進度條和百分比
        progress_container = ttk.Frame(self.progress_frame)
        progress_container.pack(fill=tk.X, pady=(5, 0))
        
        self.progress_bar = ttk.Progressbar(progress_container, variable=self.progress_var,
                                           maximum=100, length=300)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.percent_label = ttk.Label(progress_container, text="0%", width=5)
        self.percent_label.pack(side=tk.RIGHT)
        
        # 綁定進度變化事件
        self.progress_var.trace('w', self.update_progress_percentage)
        
        # 正式顯示狀態面板 (之前漏掉 pack 了)
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    def create_advanced_section(self, parent):
        """創建進階選項區域"""
        self.advanced_frame = ttk.LabelFrame(parent, text="進階選項", padding=10)
        # 初始隱藏
        self.advanced_frame.pack_forget()
        
        # 第一行選項
        row1 = ttk.Frame(self.advanced_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        self.subtitle_var = tk.BooleanVar()
        subtitle_cb = ttk.Checkbutton(row1, text="下載字幕", variable=self.subtitle_var)
        subtitle_cb.pack(side=tk.LEFT, padx=(0, 20))
        
        self.auto_subtitle_var = tk.BooleanVar()
        auto_subtitle_cb = ttk.Checkbutton(row1, text="自動字幕", variable=self.auto_subtitle_var)
        auto_subtitle_cb.pack(side=tk.LEFT, padx=(0, 20))
        
        self.keep_video_var = tk.BooleanVar(value=True)
        keep_video_cb = ttk.Checkbutton(row1, text="保留視頻", variable=self.keep_video_var)
        keep_video_cb.pack(side=tk.LEFT)
        
        # 第二行選項
        row2 = ttk.Frame(self.advanced_frame)
        row2.pack(fill=tk.X)
        
        self.keep_audio_var = tk.BooleanVar()
        keep_audio_cb = ttk.Checkbutton(row2, text="保留音頻", variable=self.keep_audio_var)
        keep_audio_cb.pack(side=tk.LEFT, padx=(0, 20))
        
        self.auto_merge_var = tk.BooleanVar(value=True)
        auto_merge_cb = ttk.Checkbutton(row2, text="自動合併", variable=self.auto_merge_var)
        auto_merge_cb.pack(side=tk.LEFT, padx=(0, 20))
        
        # 註冊字體
        for widget in [subtitle_cb, auto_subtitle_cb, keep_video_cb, 
                      keep_audio_cb, auto_merge_cb]:
            self.font_manager.register_widget(widget)



    def setup_callbacks(self):
        """設置回調函數"""
        # URL 變化回調
        self.url_var.trace('w', self.on_url_change)

        # 自動保存
        def _auto_save(*_):
            try:
                self.save_current_settings()
            except Exception:
                pass

        self.quality_var.trace('w', _auto_save)
        self.prefix_var.trace('w', _auto_save)
        self.browser_var.trace('w', _auto_save)
        self.download_path_var.trace('w', _auto_save)

        try:
            self.subtitle_var.trace('w', _auto_save)
            self.auto_subtitle_var.trace('w', _auto_save)
            self.keep_video_var.trace('w', _auto_save)
            self.keep_audio_var.trace('w', _auto_save)
            self.auto_merge_var.trace('w', _auto_save)
        except Exception:
            pass

    def load_settings(self):
        """載入設定"""
        try:
            settings = self.settings_manager.load_settings()
            
            # 載入下載路徑
            download_path = settings.get('download_path', '')
            if download_path and os.path.exists(download_path):
                self.download_path_var.set(download_path)
            else:
                default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
                self.download_path_var.set(default_path)
                
            # 載入畫質設定
            saved_quality = settings.get('quality_preference', 'best')
            q_display = "1080p (最佳)" # Default
            for text, val in QUALITY_OPTIONS:
                if val == saved_quality:
                    q_display = text
                    break
            self.quality_var.set(q_display)
            
            # 載入瀏覽器設定
            saved_browser = settings.get('browser_preference', 'none')
            browser_map_inv = {
                'none': '不使用',
                'chrome': 'Chrome',
                'edge': 'Edge',
                'firefox': 'Firefox',
                'opera': 'Opera',
                'brave': 'Brave',
                'safari': 'Safari'
            }
            display_value = browser_map_inv.get(saved_browser, '不使用')
            self.browser_var.set(display_value)
            
            saved_prefix = settings.get('filename_prefix', '')
            self.prefix_var.set(saved_prefix)
            try:
                current_values = list(self.prefix_combo.cget('values'))
                if saved_prefix not in current_values:
                    self.prefix_combo.configure(values=current_values + [saved_prefix])
            except Exception:
                pass
            
            self.subtitle_var.set(settings.get('download_subtitles', False))
            self.auto_subtitle_var.set(settings.get('download_auto_subtitles', False))
            self.keep_video_var.set(settings.get('keep_video', True))
            self.keep_audio_var.set(settings.get('keep_audio', False))
            self.auto_merge_var.set(settings.get('auto_merge', True))

            self.show_advanced = False
            self.advanced_frame.pack_forget()
            
        except Exception as e:
            logger.error(f"載入設定失敗: {e}")

    def save_current_settings(self):
        """保存當前設定"""
        try:
            # 獲取品質代碼
            quality_text = self.quality_var.get()
            quality_value = "best"
            for text, val in QUALITY_OPTIONS:
                if text == quality_text:
                    quality_value = val
                    break

            settings = {
                'download_path': self.download_path_var.get(),
                'quality_preference': quality_value,
                'browser_preference': self._get_browser_code(self.browser_var.get()),
                'filename_prefix': self.prefix_var.get(),
                'download_subtitles': self.subtitle_var.get(),
                'download_auto_subtitles': self.auto_subtitle_var.get(),
                'keep_video': self.keep_video_var.get(),
                'keep_audio': self.keep_audio_var.get(),
                'auto_merge': self.auto_merge_var.get(),
            }
            self.settings_manager.update_settings(settings)
        except Exception as e:
            logger.error(f"保存設定失敗: {e}")

    def _get_browser_code(self, display_name):
        """將瀏覽器顯示名稱轉換為代碼"""
        browser_map = {
            '不使用': 'none',
            'Chrome': 'chrome',
            'Edge': 'edge',
            'Firefox': 'firefox',
            'Opera': 'opera',
            'Brave': 'brave',
            'Safari': 'safari'
        }
        return browser_map.get(display_name, 'none')

    def on_url_change(self, *args):
        """URL 變化時的處理"""
        url = self.url_placeholder.get_value()
        if url and URLValidator.is_valid_url(url):
            platform = URLValidator.detect_platform(url)
            if platform:
                self.show_message(f"檢測到 {platform} 視頻", "info")
            else:
                self.show_message("", "")
        else:
            self.show_message("", "")
            
    def paste_url(self):
        """貼上 URL"""
        try:
            clipboard_text = self.frame.clipboard_get()
            if clipboard_text:
                self.url_placeholder.set_value(clipboard_text.strip())
        except Exception:
            pass
            
    def clear_url(self):
        """清空 URL"""
        self.url_placeholder.clear()
        self.show_message("", "")
        
    def copy_url(self):
        """複製 URL 到剪貼簿"""
        url = self.url_placeholder.get_value()
        if url:
            try:
                self.frame.clipboard_clear()
                self.frame.clipboard_append(url)
                self.show_message("網址已複製到剪貼簿", "success")
            except Exception as e:
                self.show_message(f"複製失敗: {e}", "error")
        
    def open_in_browser(self):
        """在瀏覽器中開啟 URL"""
        url = self.url_placeholder.get_value()
        if url and URLValidator.is_valid_url(url):
            try:
                webbrowser.open(url)
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

    def get_download_path(self):
        """獲取下載路徑"""
        return self.download_path_var.get()
            
    def toggle_advanced(self):
        """切換進階選項顯示"""
        self.show_advanced = not self.show_advanced
        
        if self.show_advanced:
            self.advanced_frame.pack(fill=tk.X, pady=(0, 10))
            if self.advanced_btn:
                self.advanced_btn.config(text="隱藏進階選項")
        else:
            self.advanced_frame.pack_forget()
            if self.advanced_btn:
                self.advanced_btn.config(text="進階選項")
        try:
            self.settings_manager.set_setting('show_advanced_options', self.show_advanced)
        except Exception:
            pass
            

            
    def create_download_options(self):
        """創建下載選項"""
        quality_text = self.quality_var.get()
        quality_value = "best"
        for text, value in QUALITY_OPTIONS:
            if text == quality_text:
                quality_value = value
                break
        
        # 修正瀏覽器代碼對映
        browser_display = self.browser_var.get()
        browser_code = self._get_browser_code(browser_display)
                
        settings = self.settings_manager.load_settings()
        
        return {
            'quality': quality_value,
            'filename_prefix': self.prefix_var.get(),
            'browser': browser_code,
            'subtitles': self.subtitle_var.get(),
            'auto_subtitles': self.auto_subtitle_var.get(),
            'keep_video': self.keep_video_var.get(),
            'keep_audio': self.keep_audio_var.get(),
            'auto_merge': self.auto_merge_var.get(),
            'proxy': settings.get('proxy', ''),
            'use_random_delay': settings.get('use_random_delay', False),
        }

    def log_to_status(self, message, tag=None):
        """寫入狀態日誌區域"""
        try:
            # 1. 徹底清理 ANSI 顏色代碼 (包含各種控制序列)
            import re
            ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
            message = ansi_escape.sub('', message).strip()
            
            # 2. 如果沒勾選完整日誌，過濾掉進度行
            if not self.show_full_log_var.get():
                if message.startswith('[download]') and '%' in message:
                    return

            if not message:
                return

            self.status_text.config(state=tk.NORMAL)
            # 限制日誌長度
            if float(self.status_text.index('end-1c')) > 1000:
                 self.status_text.delete(1.0, 2.0)
            
            start_index = self.status_text.index(tk.END)
            self.status_text.insert(tk.END, message + '\n')
            
            if tag:
                # 取得剛插入的那一行的位置（排除最後的換行符）
                row = int(float(start_index))
                self.status_text.tag_add(tag, f"{row}.0", f"{row}.end")

            self.status_text.see(tk.END)
            self.status_text.config(state=tk.DISABLED)
        except Exception:
            pass

    def start_download(self):
        """開始下載"""
        # 檢查 FFmpeg (新增自動引導)
        from services.ffmpeg_manager import FFmpegManager
        ffmpeg_manager = FFmpegManager()
        if not ffmpeg_manager.is_available() and platform.system() == 'Windows':
            if messagebox.askyesno("缺少 FFmpeg", "偵測到您的系統缺少 FFmpeg，這會導致無法下載 1080p 以上畫質。是否要現在自動下載並安裝？"):
                self._auto_download_ffmpeg()
                return

        url = self.url_placeholder.get_value()
        if not url:
            self.show_message(ERROR_MESSAGES['invalid_url'], "error")
            return
            
        if not URLValidator.is_valid_url(url):
            self.show_message(ERROR_MESSAGES['invalid_url'], "error")
            return
            
        download_path = self.download_path_var.get()
        if not download_path or not os.path.exists(download_path):
            self.show_message(ERROR_MESSAGES['invalid_path'], "error")
            return
            
        self.set_downloading_state(True)
        self.cancel_requested = False
        self.cancellation_token = CancellationToken()
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.log_to_status(f"[{datetime.now().strftime('%H:%M:%S')}] 開始下載: {url}")
        self.log_to_status(f"[{datetime.now().strftime('%H:%M:%S')}] 正在與伺服器建立連線，獲取影片格式與資訊...")
        
        options = self.create_download_options()
        
        # 立即紀錄到歷史紀錄 (狀態為正在下載)
        try:
            self.history_store.add_record({
                'url': url,
                'title': "正在獲取資訊...",
                'platform': URLValidator.detect_platform(url) or "未知",
                'status': '正在下載'
            })
        except Exception:
            pass
            
        threading.Thread(target=self._download_thread, 
                        args=(url, download_path, options),
                        daemon=True).start()

    def _download_thread(self, url, output_path, options):
        """下載執行緒"""
        downloader = VideoDownloader()
        gui_logger = self._create_gui_logger()
        
        def progress_callback(progress, message):
            task = downloader.get_current_task()
            filename = task.filename if task and task.filename else "正在解析..."
            self.frame.after(0, lambda: self.update_dashboard_info(filename, progress, message))
            
        def status_callback(status, message):
            # 任何狀態變化都更新進度板
            task = downloader.get_current_task()
            filename = task.title if task and task.title else "正在處理..."
            
            if status == DownloadStatus.EXTRACTING:
                self.frame.after(0, lambda: self.progress_bar.start(10)) # 啟動跑馬燈
                self.frame.after(0, lambda: self.update_dashboard_info(filename, 0, "正在獲取視頻資訊..."))
                self.frame.after(0, lambda: self.log_to_status(f"[{datetime.now().strftime('%H:%M:%S')}] 解析中: {filename}"))
            elif status == DownloadStatus.DOWNLOADING:
                self.frame.after(0, lambda: self.progress_bar.stop()) # 停止跑馬燈
                self.frame.after(0, lambda: self.log_to_status(f"[{datetime.now().strftime('%H:%M:%S')}] 擷取到檔名: {filename}", tag="title"))
                self.frame.after(0, lambda: self.log_to_status(f"[{datetime.now().strftime('%H:%M:%S')}] 下載中: {filename}"))
            elif status == DownloadStatus.MERGING:
                self.frame.after(0, lambda: self.progress_bar.start(10)) 
                self.frame.after(0, lambda: self.update_dashboard_info(filename, 99, "正在合併檔案..."))
                self.frame.after(0, lambda: self.log_to_status(f"[{datetime.now().strftime('%H:%M:%S')}] 合併中: 正將影音軌跡進行合併..."))
            elif status == DownloadStatus.COMPLETED:
                self.frame.after(0, lambda: self.progress_bar.stop())
                self.frame.after(0, lambda: self.show_message(SUCCESS_MESSAGES['download_complete'], "success"))
                self.frame.after(0, lambda: self.update_dashboard_info("下載完成", 100, "所有任務已完成"))
                self.frame.after(0, lambda: self.log_to_status(f"[{datetime.now().strftime('%H:%M:%S')}] 下載完成", tag="success"))
            elif status == DownloadStatus.FAILED:
                self.frame.after(0, lambda: self.progress_bar.stop())
                self.frame.after(0, lambda: self.show_message(f"下載失敗: {message}", "error"))
                self.frame.after(0, lambda m=message: self.log_to_status(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {m}", tag="error"))
                self.frame.after(0, lambda: self.update_dashboard_info("下載失敗", 0, message))
                # ... (歷史記錄更新邏輯保持不變)
                try:
                    history = self.history_store.get_history()
                    for record in history:
                        if record.get('url') == url and record.get('status') == '正在下載':
                            record.update({'status': '失敗', 'error': message})
                            break
                    self.history_store._save()
                except Exception: pass
            elif status == DownloadStatus.CANCELLED:
                self.frame.after(0, lambda: self.progress_bar.stop())
                self.frame.after(0, lambda: self.show_message("下載已取消", "warning"))
                self.frame.after(0, lambda: self.log_to_status(f"[{datetime.now().strftime('%H:%M:%S')}] 下載已取消", tag="error"))
                self.frame.after(0, lambda: self.update_dashboard_info("已取消", 0, "操作已中止"))
                
        downloader.set_progress_callback(progress_callback)
        downloader.set_status_callback(status_callback)
        
        try:
            self.current_downloader = downloader
            filename = downloader.download(url, output_path, options, self.cancellation_token, 
                                        logger=gui_logger)
            
            # 下載完成後邏輯
            task = downloader.get_current_task()
            
            # 使用更可靠的狀態判斷
            if task and task.status == DownloadStatus.COMPLETED:
                # 取得檔名（優先使用 downloader 返回的，其次是 task 存的）
                final_filename = filename or task.filename
                
                if final_filename:
                    final_filename = os.path.basename(final_filename)
                    # 強制移除可能殘留的 .part 顯示字樣
                    if final_filename.endswith('.part'):
                        final_filename = final_filename[:-5]
                    full_path = os.path.join(output_path, final_filename)
                else:
                    full_path = ""

                # 更新歷史記錄
                try:
                    history = self.history_store.get_history()
                    # 尋找最近一條符合網址且狀態為「正在下載」或「失敗」的紀錄進行更新
                    updated = False
                    for record in history:
                        if record.get('url') == url and record.get('status') in ['正在下載', '失敗']:
                            record.update({
                                'title': task.title or final_filename or "未知影片",
                                'filename': final_filename,
                                'filepath': full_path,
                                'quality': options.get('quality', 'best'),
                                'status': '成功'
                            })
                            updated = True
                            break
                    
                    if not updated:
                        # 如果沒找到可更新的，則新增一條（保險起見）
                        self.history_store.add_record({
                            'url': url,
                            'title': task.title or final_filename or "未知影片",
                            'platform': URLValidator.detect_platform(url) or "未知",
                            'filename': final_filename,
                            'filepath': full_path,
                            'quality': options.get('quality', 'best'),
                            'status': '成功'
                        })
                    
                    self.history_store._save()
                except Exception:
                    pass

                # 尋找實際生成的檔案 (處理合併或修正後的檔名)
                actual_file = None
                if full_path and os.path.exists(full_path):
                    actual_file = full_path
                else:
                    # 使用 video_id 進項最強效的搜尋
                    video_id = task.video_id if task else ""
                    if video_id:
                        import glob
                        # 搜尋包含 [ID] 的所有檔案
                        pattern = os.path.join(output_path, f"*[{video_id}]*.*")
                        matches = glob.glob(pattern)
                        # 過濾掉臨時檔案，並選擇最短的路徑（通常是最終成品）
                        valid_matches = [m for m in matches if not m.endswith(('.part', '.ytdl', '.temp', '.merged'))]
                        if valid_matches:
                            actual_file = max(valid_matches, key=os.path.getmtime)
                    
                    # 備援：如果 ID 搜尋失敗，嘗試模糊標題搜尋
                    if not actual_file and task.title:
                        import re
                        safe_title = re.escape(task.title[:10]) # 取標題前10字
                        pattern = os.path.join(output_path, f"*{task.title[:10]}*.*")
                        matches = glob.glob(pattern)
                        valid_matches = [m for m in matches if not m.endswith(('.part', '.ytdl', '.temp'))]
                        if valid_matches:
                            actual_file = valid_matches[0]

                # 如果找到了實際檔案，彈窗詢問播放
                if actual_file and os.path.exists(actual_file):
                    def ask_play():
                        if messagebox.askyesno("下載完成", f"影片下載成功！\n檔名：{os.path.basename(actual_file)}\n\n是否立即播放？"):
                            try:
                                if platform.system() == 'Windows':
                                    os.startfile(actual_file)
                                elif platform.system() == 'Darwin':
                                    subprocess.call(['open', actual_file])
                                else:
                                    subprocess.call(['xdg-open', actual_file])
                            except Exception as e:
                                messagebox.showerror("錯誤", f"無法播放檔案：{e}")
                    
                    self.frame.after(200, ask_play)
                else:
                    self.log_to_status(f"警告: 已完成但未能定位實體檔案 (ID: {task.video_id})")
            
            # 移除這裡的失敗紀錄，因為已移至 status_callback 中統一處理

        except Exception as e:
            err_msg = str(e)
            logger.error(f"下載執行緒發生錯誤: {err_msg}")
            self.frame.after(0, lambda m=err_msg: self.log_to_status(f"ERROR: {m}", tag="error"))
        finally:
            self.frame.after(0, lambda: self.set_downloading_state(False))
            self.current_downloader = None

    def _auto_download_ffmpeg(self):
        """自動下載 FFmpeg 的內部邏輯"""
        from services.ffmpeg_manager import FFmpegManager
        manager = FFmpegManager()
        
        self.log_to_status("正在自動下載 FFmpeg，請稍候...", tag="highlight")
        self.set_downloading_state(True)
        self.download_btn.config(text="正在安裝...")
        
        def do_download():
            try:
                def progress(p, msg):
                    self.frame.after(0, lambda: self.log_to_status(f"FFmpeg 下載進度: {int(p)}%"))
                
                success = manager.download_ffmpeg_windows(progress_callback=progress)
                if success:
                    self.frame.after(0, lambda: messagebox.showinfo("成功", "FFmpeg 安裝完成！現在您可以下載高品質影片了。"))
                    self.frame.after(0, lambda: self.log_to_status("FFmpeg 安裝成功，準備就緒。"))
                else:
                    self.frame.after(0, lambda: messagebox.showerror("錯誤", "FFmpeg 下載失敗，請手動到設定頁面嘗試。"))
            except Exception as e:
                err_msg = str(e)
                self.frame.after(0, lambda m=err_msg: self.log_to_status(f"安裝失敗: {m}"))
            finally:
                self.frame.after(0, lambda: self.set_downloading_state(False))
                self.frame.after(0, lambda: self.download_btn.config(text=UI_TEXT['download_button']))
        
        threading.Thread(target=do_download, daemon=True).start()

    def update_dashboard_info(self, filename, progress, extra_info):
        """更新下載資訊面板 (Label & Progress Bar)"""
        try:
            info_text = f"檔案: {filename} | 進度: {progress:.1f}% | {extra_info}"
            if len(info_text) > 80:
                info_text = info_text[:77] + "..."
            self.info_label.config(text=info_text)
            self.progress_var.set(progress)
        except Exception as e:
            print(f"Update dashboard error: {e}")

    def update_dashboard(self, filename, progress, extra_info):
        """(Deprecated) 舊方法兼容，轉發到 update_dashboard_info"""
        self.update_dashboard_info(filename, progress, extra_info)

    def open_download_folder(self):
        """開啟下載資料夾"""
        download_path = self.download_path_var.get()
        try:
            if download_path and os.path.exists(download_path):
                if platform.system() == 'Windows':
                    os.startfile(download_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', download_path])
                else:  # Linux
                    subprocess.call(['xdg-open', download_path])
            else:
                messagebox.showwarning("警告", "下載路徑不存在")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟資料夾：{str(e)}")
    
    def update_progress_percentage(self, *args):
        """更新進度百分比標籤"""
        try:
            percent = int(self.progress_var.get())
            self.percent_label.config(text=f"{percent}%")
        except Exception:
            pass
    
    def update_progress_info(self, info):
        """更新即時進度信息 (兼容舊代碼)"""
        self.log_to_status(info)
    
    def update_download_info(self, title, percent, speed_mbps):
        """更新下載信息（標題、進度、速度）"""
        pass # 已由 update_dashboard_info 取代

    def toggle_pause(self):
        """切換暫停/繼續"""
        pass
            
    def cancel_download(self):
        """取消下載"""
        try:
            if self.cancel_requested:
                return
                
            self.cancel_requested = True
            self.log_to_status("正在發送取消訊號...")
            self.show_message("正在取消，請稍候...", "warning")
            
            # 立即禁用取消按鈕，防止重複點擊
            self.cancel_btn.config(state=tk.DISABLED)
            
            if self.cancellation_token:
                self.cancellation_token.cancel()
                
            # 如果還在解析階段，downloader 可能不會立即報錯，我們手動設置狀態
            def force_reset():
                if self.is_downloading:
                    self.set_downloading_state(False)
                    self.log_to_status("下載已取消 (UI 界面已重置)")
            
            self.frame.after(1500, force_reset)
        except Exception as e:
            self.log_to_status(f"取消時發生錯誤: {e}")

    def set_downloading_state(self, downloading):
        """設置下載狀態"""
        self.is_downloading = downloading
        
        if downloading:
            self.download_btn.config(state=tk.DISABLED)
            self.cancel_btn.config(state=tk.NORMAL)
        else:
            self.download_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.DISABLED)
            
    def show_message(self, message, msg_type="info"):
        """顯示訊息"""
        if not message:
            self.message_frame.pack_forget()
            return
            
        self.message_var.set(message)
        
        colors = {
            "info": "blue",
            "success": "green",
            "warning": "orange",
            "error": "red"
        }
        self.message_label.config(foreground=colors.get(msg_type, "blue"))
        
        self.message_frame.pack(fill=tk.X, pady=(0, 10))
        
        if msg_type != "error":
            self.frame.after(5000, lambda: self.show_message("", ""))
            
    def log_message(self, message):
        """記錄日誌訊息 (兼容)"""
        self.log_to_status(message)
            
    def clear_log(self):
        """清空日誌"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
            
    def copy_current_filename(self):
        """複製當前擷取到的名稱到剪貼簿"""
        try:
             import pyperclip
             # 如果有當前任務，優先從任務拿檔名
             filename = ""
             if self.current_downloader and self.current_downloader.current_task:
                 filename = self.current_downloader.current_task.filename or self.current_downloader.current_task.title
             
             # 如果都沒有，從 info_label 的文字抓
             if not filename:
                 info_text = self.info_label.cget("text")
                 if "檔案: " in info_text:
                     filename = info_text.split("檔案: ")[1].split(" | ")[0]
             
             if filename:
                 # 移除可能存在的副檔名或 ID
                 if " [" in filename:
                     filename = filename.split(" [")[0]
                 elif "." in filename:
                     filename = os.path.splitext(filename)[0]
                 
                 pyperclip.copy(filename)
                 self.show_message(f"已複製: {filename}", "info")
             else:
                 self.show_message("目前沒有可供複製的檔名", "warning")
        except ImportError:
             # 如果沒裝 pyperclip，嘗試用 tkinter 內建方式
             try:
                 filename = ""
                 if self.current_downloader and self.current_downloader.current_task:
                     filename = self.current_downloader.current_task.filename or self.current_downloader.current_task.title
                 if filename:
                     self.frame.clipboard_clear()
                     self.frame.clipboard_append(filename)
                     self.show_message("名稱已複製到剪貼簿", "info")
                 else:
                     self.show_message("目前沒有可供複製的檔名", "warning")
             except Exception:
                 self.show_message("無法存取剪貼簿", "error")
        except Exception as e:
            self.show_message(f"複製失敗: {e}", "error")

    def save_log(self):
        """保存日誌"""
        content = self.status_text.get(1.0, tk.END)
        if content.strip():
            filename = filedialog.asksaveasfilename(
                title="保存日誌",
                defaultextension=".txt",
                filetypes=[("文字檔案", "*.txt"), ("所有檔案", "*.*")]
            )
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.show_message("日誌已保存", "success")
                except Exception as e:
                    self.show_message(f"保存日誌失敗: {e}", "error")

    def get_prefix_options(self):
        """獲取檔名前綴選項項目"""
        return FILENAME_PREFIXES

    def get_quick_links_list(self):
        """從 config/quick_links.txt 獲取快速連結"""
        links = ["-- 選擇連結 --"]
        path = os.path.join('config', 'quick_links.txt')
        
        # 如果檔案不存在，則建立一個範例
        if not os.path.exists(path):
            try:
                os.makedirs('config', exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("# 快速連結格式: 名稱|網址\n")
                    f.write("YouTube|https://www.youtube.com\n")
                    f.write("Bilibili|https://www.bilibili.com\n")
            except Exception:
                pass

        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            links.append(line.split('|')[0].strip())
            except Exception:
                pass
        return links

    def on_quick_link_selected(self, event):
        """當選取快速連結時"""
        selection = self.quick_link_var.get()
        if selection == "-- 選擇連結 --":
            return
            
        path = os.path.join('config', 'quick_links.txt')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('|')
                            if parts[0].strip() == selection:
                                url = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                                self.url_placeholder.set_value(url)
                                break
            except Exception:
                pass
        # 重置下拉選單顯示
        self.quick_link_combo.current(0)

    def edit_quick_links(self):
        """開啟快速連結檔案進行編輯"""
        path = os.path.join('config', 'quick_links.txt')
        if not os.path.exists('config'):
            os.makedirs('config')
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                f.write("# 快速連結格式: 名稱|網址\n# 例如: Google|https://www.google.com\n")
        
        try:
            if platform.system() == 'Windows':
                os.startfile(path)
            else:
                subprocess.call(['open' if platform.system() == 'Darwin' else 'xdg-open', path])
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟檔案: {e}")

    def reload_prefix_list(self):
        """重新載入 config/prename.txt 並更新下拉清單"""
        try:
            current = self.prefix_var.get()
            new_list = reload_filename_prefixes()
            self.prefix_combo.configure(values=new_list)
            if current in new_list:
                self.prefix_var.set(current)
            else:
                self.prefix_var.set(new_list[0] if new_list else '')
            self.show_message("前綴已重新載入", "success")
        except Exception as e:
            self.show_message(f"重新載入前綴失敗：{e}", "error")

    def cleanup(self):
        """清理資源"""
        pass