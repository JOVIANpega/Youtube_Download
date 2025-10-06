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
import subprocess
import platform
# 暫時註解掉可能有問題的導入
# from utils.threading_utils import BackgroundTask, CancellationToken
# from services.downloader import VideoDownloader, DownloadStatus
# from services.history_store import HistoryStore, HistoryEntry
# 移除可能造成循環導入的模組
# from models.types import DownloadOptions, DownloadQuality
from logging_config import get_logger

logger = get_logger(__name__)

class DownloadTab:
    """下載頁面"""
    
    def __init__(self, parent, font_manager, settings_manager):
        self.parent = parent
        self.font_manager = font_manager
        self.settings_manager = settings_manager
        self.frame = ttk.Frame(parent)
        
        # 服務（暫時註解掉，避免依賴問題）
        # self.downloader = VideoDownloader()
        # self.history_store = HistoryStore()
        
        # 狀態
        # self.current_task: Optional[BackgroundTask] = None
        # self.cancellation_token: Optional[CancellationToken] = None
        self.is_downloading = False
        self.show_advanced = False
        self.show_log = False
        
        # UI 變數
        self.url_var = tk.StringVar()
        self.download_path_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="best")
        self.prefix_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value=STATUS_MESSAGES['ready'])
        self.message_var = tk.StringVar()
        
        self.setup_ui()
        self.setup_callbacks()
        self.load_settings()
        
    def _create_gui_logger(self):
        """建立一個將 yt-dlp 日誌輸出到 GUI 的 logger 物件"""
        tab = self
        class _GuiLogger:
            def debug(self, msg):
                try:
                    tab.frame.after(0, lambda: tab.update_progress_info(str(msg)))
                except Exception:
                    pass
            def info(self, msg):
                try:
                    tab.frame.after(0, lambda: tab.update_progress_info(str(msg)))
                except Exception:
                    pass
            def warning(self, msg):
                try:
                    tab.frame.after(0, lambda: tab.update_progress_info(f"[WARN] {msg}"))
                except Exception:
                    pass
            def error(self, msg):
                try:
                    tab.frame.after(0, lambda: tab.update_progress_info(f"[ERROR] {msg}"))
                except Exception:
                    pass
        return _GuiLogger()

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
        
        # 進度區域
        self.create_progress_section(main_frame)
        
        # 進階選項區域
        self.create_advanced_section(main_frame)
        
        # 日誌區域
        self.create_log_section(main_frame)
        
    def create_url_section(self, parent):
        """創建 URL 輸入區域"""
        url_frame = ttk.LabelFrame(parent, text="視頻網址", padding=10)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        # URL 輸入框
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=self.font_manager.get_font())
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
        browse_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # 開啟資料夾按鈕
        open_folder_btn = ttk.Button(path_row, text="開啟資料夾", 
                                   command=self.open_download_folder, width=10)
        open_folder_btn.pack(side=tk.RIGHT)
        
        # 註冊字體
        self.font_manager.register_widget(self.path_entry)
        for btn in [browse_btn, open_folder_btn]:
            self.font_manager.register_widget(btn)
        
        # 檔名前綴
        prefix_row = ttk.Frame(path_frame)
        prefix_row.pack(fill=tk.X)
        
        ttk.Label(prefix_row, text="檔名前綴：").pack(side=tk.LEFT)
        
        # 為前綴下拉框建立使用符號字體的樣式
        try:
            style = ttk.Style(self.frame)
            style.configure('Prefix.TCombobox', font=self.font_manager.get_font('symbols'))
            combobox_style = 'Prefix.TCombobox'
        except Exception:
            combobox_style = 'TCombobox'

        self.prefix_combo = ttk.Combobox(prefix_row, textvariable=self.prefix_var,
                                        values=self.get_prefix_options(), width=15,
                                        style=combobox_style)
        self.prefix_combo.pack(side=tk.LEFT, padx=(5, 10))
        # 重新載入前綴按鈕
        reload_btn = ttk.Button(prefix_row, text="重新載入前綴", command=self.reload_prefix_list, width=12)
        reload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 品質選擇
        ttk.Label(prefix_row, text="品質：").pack(side=tk.LEFT)
        
        self.quality_combo = ttk.Combobox(prefix_row, textvariable=self.quality_var,
                                         values=[option[0] for option in QUALITY_OPTIONS],
                                         state="readonly", width=12)
        self.quality_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.quality_combo.set(QUALITY_OPTIONS[0][0])
        
        # 註冊字體
        for widget in [self.path_entry, browse_btn, self.prefix_combo, self.quality_combo, reload_btn]:
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
        
        # 主下載按鈕
        self.download_btn = ttk.Button(button_frame, text=UI_TEXT['download_button'],
                                      command=self.start_download, style="Accent.TButton")
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 暫停/繼續按鈕
        self.pause_btn = ttk.Button(button_frame, text=UI_TEXT['pause_button'],
                                   command=self.toggle_pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 取消按鈕
        self.cancel_btn = ttk.Button(button_frame, text=UI_TEXT['cancel_button'],
                                    command=self.cancel_download, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 進階選項按鈕
        self.advanced_btn = ttk.Button(button_frame, text="進階選項",
                                      command=self.toggle_advanced)
        self.advanced_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 註冊字體
        for btn in [self.download_btn, self.pause_btn, self.cancel_btn, self.advanced_btn]:
            self.font_manager.register_widget(btn)
            
    def create_progress_section(self, parent):
        """創建進度區域"""
        self.progress_frame = ttk.LabelFrame(parent, text="下載狀態", padding=10)
        # 初始隱藏
        
        # 即時狀態顯示框
        self.progress_display_container = ttk.Frame(self.progress_frame)
        self.progress_display_container.pack(fill=tk.X, pady=(0, 5))
        
        # 狀態顯示區域（較大的文字區域用於顯示進度信息）
        status_frame = ttk.Frame(self.progress_display_container)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # 使用 Text 控件顯示多行狀態信息
        from tkinter import scrolledtext
        self.status_text = scrolledtext.ScrolledText(status_frame, 
                                                   height=6, 
                                                   width=60,
                                                   font=self.font_manager.get_font(),
                                                   foreground="blue", 
                                                   wrap=tk.WORD,
                                                   state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # 初始化顯示
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, STATUS_MESSAGES['ready'])
        self.status_text.config(state=tk.DISABLED)
        
        # 註冊字體
        self.font_manager.register_widget(self.status_text)
        
        # 進度條和百分比（隱藏，保留變數）
        progress_container = ttk.Frame(self.progress_frame)
        self.progress_bar = ttk.Progressbar(progress_container, variable=self.progress_var,
                                           maximum=100, length=300)
        # 不需要顯示進度條
        self.percent_label = ttk.Label(progress_container, text="0%", width=5)
        # 不需要顯示百分比標籤
        
        # 綁定進度變化事件（保留但不顯示）
        self.progress_var.trace('w', self.update_progress_percentage)
            
    def create_advanced_section(self, parent):
        """創建進階選項區域"""
        self.advanced_frame = ttk.LabelFrame(parent, text="進階選項", padding=10)
        # 初始隱藏
        
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
        
        # 日誌按鈕
        self.log_btn = ttk.Button(row2, text="顯示日誌", command=self.toggle_log)
        self.log_btn.pack(side=tk.RIGHT)
        
        # 註冊字體
        for widget in [subtitle_cb, auto_subtitle_cb, keep_video_cb, 
                      keep_audio_cb, auto_merge_cb, self.log_btn]:
            self.font_manager.register_widget(widget)
            
    def create_log_section(self, parent):
        """創建日誌區域"""
        self.log_frame = ttk.LabelFrame(parent, text="下載日誌", padding=10)
        # 初始隱藏
        
        # 日誌文字區域
        log_text_frame = ttk.Frame(self.log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_text_frame, height=8, wrap=tk.WORD,
                               font=self.font_manager.get_font('monospace'))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滾動條
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, 
                                     command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # 日誌按鈕
        log_btn_frame = ttk.Frame(self.log_frame)
        log_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        clear_log_btn = ttk.Button(log_btn_frame, text="清空日誌", 
                                  command=self.clear_log)
        clear_log_btn.pack(side=tk.LEFT)
        
        save_log_btn = ttk.Button(log_btn_frame, text="保存日誌", 
                                 command=self.save_log)
        save_log_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 註冊字體
        self.font_manager.register_widget(self.log_text, 'monospace')
        for btn in [clear_log_btn, save_log_btn]:
            self.font_manager.register_widget(btn)
            
    def setup_callbacks(self):
        """設置回調函數"""
        # 下載器回調（暫時註解掉，避免依賴問題）
        # self.downloader.set_progress_callback(self.on_progress_update)
        # self.downloader.set_status_callback(self.on_status_update)
        
        # URL 變化回調
        self.url_var.trace('w', self.on_url_change)
        
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
            
            # 載入進階選項
            self.subtitle_var.set(settings.get('download_subtitles', False))
            self.auto_subtitle_var.set(settings.get('download_auto_subtitles', False))
            self.keep_video_var.set(settings.get('keep_video', True))
            self.keep_audio_var.set(settings.get('keep_audio', False))
            self.auto_merge_var.set(settings.get('auto_merge', True))
            
        except Exception as e:
            logger.error(f"載入設定失敗: {e}")
            
    def save_current_settings(self):
        """保存當前設定"""
        try:
            settings = {
                'download_path': self.download_path_var.get(),
                'quality_preference': self.quality_var.get(),
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
            
    # 事件處理方法
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
            
    def toggle_advanced(self):
        """切換進階選項顯示"""
        self.show_advanced = not self.show_advanced
        
        if self.show_advanced:
            self.advanced_frame.pack(fill=tk.X, pady=(0, 10))
            self.advanced_btn.config(text="隱藏進階選項")
        else:
            self.advanced_frame.pack_forget()
            self.advanced_btn.config(text="進階選項")
            
    def toggle_log(self):
        """切換日誌顯示"""
        self.show_log = not self.show_log
        
        if self.show_log:
            self.log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            self.log_btn.config(text="隱藏日誌")
        else:
            self.log_frame.pack_forget()
            self.log_btn.config(text="顯示日誌")
            
    def start_download(self):
        """開始下載"""
        # 驗證輸入
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
            
        valid, error_msg = InputValidator.validate_download_path(download_path)
        if not valid:
            self.show_message(error_msg, "error")
            return
            
        # 保存設定
        self.save_current_settings()
        
        # 創建下載選項
        options = self.create_download_options()
        
        # 創建取消令牌（暫時註解掉，避免依賴問題）
        # self.cancellation_token = CancellationToken()
        
        # 創建背景任務（暫時註解掉，避免依賴問題）
        # self.current_task = BackgroundTask(
        #     target=self.download_worker,
        #     args=(url, download_path, options),
        #     progress_callback=self.on_progress_update,
        #     completion_callback=self.on_download_complete
        # )
        
        # 更新 UI 狀態
        self.set_downloading_state(True)
        
        # 顯示進度區域
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 開始任務（暫時註解掉，顯示提示訊息）
        # if self.current_task.start():
        #     self.log_message("開始下載...")
        #     self.show_message("正在解析視頻資訊...", "info")
        # else:
        #     self.show_message("無法啟動下載任務", "error")
        #     self.set_downloading_state(False)
        
        # 檢查並安裝依賴
        self.check_and_install_dependencies(url, download_path, options)
    
    def check_and_install_dependencies(self, url, download_path, options):
        """檢查並安裝必要的依賴"""
        try:
            import yt_dlp
            # 如果已經安裝了 yt-dlp，啟動下載
            self.start_simple_download(url, download_path, options)
        except ImportError:
            # 如果沒有安裝，顯示安裝對話框
            self.show_install_dialog(url, download_path, options)
    
    def show_install_dialog(self, url, download_path, options):
        """顯示安裝對話框"""
        result = messagebox.askyesno(
            "缺少依賴",
            "檢測到下載器需要 yt-dlp 依賴包。\n\n是否現在自動安裝？\n\n注意：安裝過程可能需要數分鐘時間。",
            icon="question"
        )
        
        if result:
            self.install_dependencies_in_thread(url, download_path, options)
        else:
            self.show_message("已取消下載，請手動安裝 yt-dlp", "warning")
            self.set_downloading_state(False)
    
    def install_dependencies_in_thread(self, url, download_path, options):
        """在背景執行緒中安裝依賴"""
        def install_worker():
            try:
                self.show_message("正在安裝 yt-dlp...，請稍候", "info")
                self.log_message("開始安裝 yt-dlp...")
                
                # 安裝 yt-dlp
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "yt-dlp>=2023.12.30"],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分鐘超時
                )
                
                if result.returncode == 0:
                    self.log_message("yt-dlp 安裝成功！")
                    self.show_message("依賴安裝完成，開始下載...", "success")
                    
                    # 延遲一秒後開始下載
                    time.sleep(1)
                    self.start_simple_download(url, download_path, options)
                else:
                    error_msg = result.stderr or "未知錯誤"
                    self.log_message(f"安裝失敗：{error_msg}")
                    self.show_message("依賴安裝失敗，請手動安裝", "error")
                    self.set_downloading_state(False)
                    
            except subprocess.TimeoutExpired:
                self.log_message("安裝超時")
                self.show_message("安裝超時，請手動安裝 yt-dlp", "error")
                self.set_downloading_state(False)
            except Exception as e:
                self.log_message(f"安裝過程發生錯誤：{str(e)}")
                self.show_message("安裝失敗，請手動安裝 yt-dlp", "error")
                self.set_downloading_state(False)
        
        # 在背景執行緒中執行安裝
        install_thread = threading.Thread(target=install_worker, daemon=True)
        install_thread.start()
    
    def start_simple_download(self, url, download_path, options):
        """啟動簡化的下載功能"""
        def download_worker():
            try:
                import yt_dlp
                
                # 創建下載器
                # 獲取檔名前綴和品質設定
                prefix = options.get('prefix', '')
                quality = options.get('quality', 'best')  # 提前定義 quality
                filename_template = f'{prefix}%(title)s.%(ext)s' if prefix else '%(title)s.%(ext)s'
                
                # 除錯信息
                self.frame.after(0, lambda q=quality, p=prefix: self.log_message(f"下載選項: 品質={q}, 前綴='{p}'"))
                
                ydl_opts = {
                    'outtmpl': os.path.join(download_path, filename_template),
                    'progress_hooks': [self.on_progress_hook],
                    # 基本設定
                    'socket_timeout': 30,
                    'retries': 3,
                    # 讓日誌/進度完整輸出並導入 GUI
                    'quiet': False,
                    'no_warnings': False,
                    'verbose': True,
                    'logger': self._create_gui_logger(),
                    'progress_with_newlines': True,
                    # 添加用戶代理以避免某些阻擋
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                }
                
                # 根據用戶選擇設定格式 - 使用更簡化和相容的格式選擇
                if quality == 'best':
                    # 使用最簡單的格式選擇，讓 yt-dlp 自動選擇最佳格式
                    ydl_opts['format'] = 'best'
                elif quality == 'audio':
                    # 僅音頻
                    ydl_opts['format'] = 'bestaudio'
                elif quality == '720p':
                    # 指定720p，使用更簡化的格式選擇
                    ydl_opts['format'] = 'best[height<=720]/best'
                elif quality == '480p':
                    # 指定480p
                    ydl_opts['format'] = 'best[height<=480]/best'
                elif quality == '360p':
                    # 指定360p
                    ydl_opts['format'] = 'best[height<=360]/best'
                else:
                    # 預設使用最佳格式
                    ydl_opts['format'] = 'best'
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # 確認文件夾存在
                    os.makedirs(download_path, exist_ok=True)
                    
                    self.frame.after(0, lambda u=url: self.log_message(f"開始下載：{u}"))
                    self.frame.after(0, lambda: self.show_message("正在解析視頻資訊...", "info"))
                    # 初始化狀態顯示
                    self.frame.after(0, lambda: self.update_progress_info("準備開始下載..."))
                    
                    # 先取得視頻資訊（用於顯示檔案名）
                    try:
                        info = ydl.extract_info(url, download=False)
                        title = info.get('title', 'Unknown')
                        self.frame.after(0, lambda tn=title: self.update_download_info(tn, 0, 0))
                    except Exception as e:
                        self.frame.after(0, lambda: self.update_progress_info(f"無法獲取視頻資訊：{e}"))
                    
                    # 下載
                    ydl.download([url])
                    
                    self.frame.after(0, lambda: self.show_message("下載完成！", "success"))
                    self.frame.after(0, lambda: self.log_message("下載完成"))
                    
                    # 詢問是否開啟影片
                    self.frame.after(0, lambda dp=download_path: self.ask_open_video(dp))
                    
            except ImportError:
                self.frame.after(0, lambda: self.show_message("yt-dlp 未正確安裝，請重新啟動程式", "error"))
            except Exception as e:
                # 根據錯誤類型給出更具體的訊息
                error_type = type(e).__name__
                if "HTTP Error 403" in str(e):
                    error_msg = f"下載失敗：伺服器拒絕訪問 (403錯誤)，可能該影片暫時無法存取"
                elif "Requested format is not available" in str(e):
                    error_msg = f"下載失敗：請求的格式不可用，嘗試使用其他品質選項"
                elif "ExtractionError" in str(e):
                    error_msg = f"下載失敗：無法解析影片資訊，請檢查影片網址是否正確"
                else:
                    error_msg = f"下載失敗 ({error_type})：{str(e)}"
                
                self.frame.after(0, lambda msg=error_msg: self.show_message(msg, "error"))
                self.frame.after(0, lambda msg=error_msg: self.log_message(msg))
            finally:
                self.frame.after(0, lambda: self.set_downloading_state(False))
        
        # 在背景執行緒中執行下載
        download_thread = threading.Thread(target=download_worker, daemon=True)
        download_thread.start()
    
    def on_progress_hook(self, d):
        """進度回調"""
        try:
            status = d.get('status', 'unset')
            # 計算百分比：優先使用 bytes，其次使用 _percent_str，其次估算
            percent = None
            downloaded = d.get('downloaded_bytes')
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if downloaded is not None and total:
                try:
                    percent = downloaded / total * 100
                except Exception:
                    percent = None
            if percent is None:
                pstr = d.get('_percent_str')  # 如 ' 12.3%'
                if pstr and '%' in pstr:
                    try:
                        percent = float(pstr.strip().replace('%', ''))
                    except Exception:
                        percent = None

            # 速度（MB/s）
            speed_mbps = 0.0
            speed = d.get('speed')
            if speed:
                speed_mbps = speed / 1024 / 1024
            else:
                spstr = d.get('_speed_str')  # 如 '3.40MiB/s'
                if spstr and 'iB/s' in spstr:
                    try:
                        num = spstr.split('iB/s')[0]
                        # 支援 KiB/MiB/GiB
                        units = {'KiB': 1/1024, 'MiB': 1, 'GiB': 1024}
                        for u, mul in units.items():
                            if u in num:
                                val = float(num.replace(u, '').strip())
                                speed_mbps = val * mul
                                break
                    except Exception:
                        pass

            # 取得檔案名 -> 標題
            filename = d.get('filename', '')
            if filename:
                title = os.path.splitext(os.path.basename(filename))[0]
                if title.startswith(('per- ', 'per best- ', 'per best2- ', 'per best3- ', 'per nice- ')):
                    title = title.split(' ', 1)[1]
            else:
                title = "下載中的檔案"

            # 更新主下載資訊（覆蓋式）
            if percent is not None:
                self.frame.after(0, lambda t=title, p=percent, s=speed_mbps: self.update_download_info(t, p, s))

            # 追加原始進度行，便於完整觀察
            line_parts = []
            if percent is not None:
                line_parts.append(f"進度 {percent:.1f}%")
            if speed_mbps:
                line_parts.append(f"速度 {speed_mbps:.2f} MB/s")
            eta = d.get('eta')
            if isinstance(eta, (int, float)) and eta >= 0:
                # 簡單格式化 ETA
                m, s = divmod(int(eta), 60)
                h, m = divmod(m, 60)
                eta_str = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
                line_parts.append(f"ETA {eta_str}")
            if status:
                line_parts.append(f"狀態 {status}")
            if line_parts:
                msg = " | ".join(line_parts)
                self.frame.after(0, lambda m=msg: self.update_progress_info(m))

            # 完成
            if status == 'finished':
                self.frame.after(0, lambda: self.update_progress_info("下載完成！"))
                        
        except Exception as e:
            error_info = f"進度回調錯誤: {e}"
            self.frame.after(0, lambda info=error_info: self.update_progress_info(info))
    
    def ask_open_video(self, download_path):
        """詢問是否開啟下載的影片"""
        try:
            # 尋找最近下載的影片檔案
            video_extensions = ['*.mp4', '*.mp3', '*.wav', '*.mkv', '*.avi', '*.webm']
            video_files = []
            
            for extension in video_extensions:
                video_files.extend(glob.glob(os.path.join(download_path, extension)))
            
            if video_files:
                # 按修改時間排序，取最新的
                latest_video = max(video_files, key=os.path.getmtime)
                
                result = messagebox.askyesno(
                    "下載完成",
                    f"影片已下載完成！\n\n檔案：{os.path.basename(latest_video)}\n\n是否現在播放？",
                    icon="question"
                )
                
                if result:
                    self.open_file_with_system(latest_video)
                    
        except Exception as e:
            self.log_message(f"檢查影片檔案時發生錯誤：{str(e)}")
    
    def open_file_with_system(self, file_path):
        """使用系統預設程式開啟檔案"""
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            self.log_message(f"開啟檔案時發生錯誤：{str(e)}")
            messagebox.showerror("錯誤", f"無法開啟檔案：{str(e)}")
    
    def open_download_folder(self):
        """開啟下載資料夾"""
        try:
            download_path = self.download_path_var.get()
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
    
    def update_progress(self, percent):
        """更新進度條和百分比"""
        try:
            # 更新進度條
            self.progress_var.set(percent)
            # 更新百分比標籤
            self.percent_label.config(text=f"{int(percent)}%")
            # 強制更新顯示
            self.frame.update_idletasks()
        except Exception as e:
            print(f"Update progress error: {e}")
    
    def update_speed_display(self, speed_str):
        """更新速度顯示"""
        try:
            self.speed_label.config(text=speed_str)
            # 強制更新顯示
            self.frame.update_idletasks()
        except Exception as e:
            print(f"Update speed error: {e}")
    
    def update_status_display(self, status):
        """更新狀態顯示"""
        try:
            status_map = {
                'downloading': '下載中...',
                'finished': '下載完成',
                'error': '下載錯誤'
            }
            display_status = status_map.get(status, status)
            self.status_var.set(display_status)
            # 強制更新顯示
            self.frame.update_idletasks()
        except Exception as e:
            print(f"Update status error: {e}")
    
    def update_progress_info(self, info):
        """更新即時進度信息"""
        try:
            # 更新 Text 控件
            current_time = datetime.now().strftime("%H:%M:%S")
            status_line = f"[{current_time}] {info}"
            
            self.status_text.config(state=tk.NORMAL)
            self.status_text.insert(tk.END, status_line + "\n")
            self.status_text.config(state=tk.DISABLED)
            self.status_text.see(tk.END)  # 自動滾動到最新
            
            # 也在日誌中記錄
            self.log_message(info)
            # 強制更新顯示
            self.frame.update_idletasks()
        except Exception as e:
            print(f"Update progress info error: {e}")
    
    def update_download_info(self, title, percent, speed_mbps):
        """更新下載信息（標題、進度、速度）"""
        try:
            # 安全地截斷標題，避免太長
            display_title = title[:50] + "..." if len(title) > 50 else title
                        
            # 建立完整的狀態信息（多行格式）
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if percent > 0:
                status_lines = [
                    f"[{current_time}] 檔案：{display_title}",
                    f"進度：{percent:.1f}%",
                    f"速度：{speed_mbps:.1f} MB/s"
                ]
            else:
                status_lines = [
                    f"[{current_time}] 檔案：{display_title}",
                    "狀態：準備下載..."
                ]
                
            # 更新 Text 控件
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "\n".join(status_lines))
            self.status_text.config(state=tk.DISABLED)
            self.status_text.see(tk.END)  # 自動滾動到最新
        
            # 強制更新顯示
            self.frame.update_idletasks()
        except Exception as e:
            print(f"Update download info error: {e}")
    
    def update_speed_label(self, speed_str):
        """更新速度標籤"""
        try:
            # 尋找速度標籤並更新
            for child in self.progress_frame.winfo_children():
                if hasattr(child, 'winfo_children'):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Label) and "MB/s" in grandchild.cget('text'):
                            grandchild.config(text=speed_str)
                            return
        except Exception:
            pass
    def download_worker(self, url, download_path, options, cancellation_token, progress_reporter):
        """下載工作執行緒"""
        try:
            # 下載視頻（暫時註解掉）
            # filename = self.downloader.download(
            #     url=url,
            #     output_path=download_path,
            #     options=options,
            #     cancellation_token=cancellation_token,
            #     progress_reporter=progress_reporter
            # )
            filename = "test_video.mp4"  # 暫時的測試值
            
            # 添加到歷史記錄
            if filename:
                file_path = os.path.join(download_path, filename)
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                
                # 獲取視頻資訊（暫時註解掉）
                # try:
                #     video_info = self.downloader.get_video_info(url)
                #     title = video_info.get('title', filename)
                #     platform = video_info.get('platform', '')
                #     duration = video_info.get('duration', 0)
                # except:
                #     title = filename
                #     platform = URLValidator.detect_platform(url) or ""
                #     duration = 0
                #     
                # history_entry = HistoryEntry(
                #     url=url,
                #     title=title,
                #     platform=platform,
                #     filename=filename,
                #     file_path=file_path,
                #     file_size=file_size,
                #     quality=options.get('quality', ''),
                #     duration=duration
                # )
                # 
                # self.history_store.add_entry(history_entry)
                pass  # 暫時跳過歷史記錄
                
            return filename
            
        except Exception as e:
            logger.error(f"下載失敗: {e}")
            raise
            
    def create_download_options(self):
        """創建下載選項"""
        # 獲取品質對應值
        quality_text = self.quality_var.get()
        quality_value = "best"
        for text, value in QUALITY_OPTIONS:
            if text == quality_text:
                quality_value = value
                break
                
        return {
            'quality': quality_value,
            'prefix': self.prefix_var.get(),
            'download_subtitles': self.subtitle_var.get(),
            'download_auto_subtitles': self.auto_subtitle_var.get(),
            'keep_video': self.keep_video_var.get(),
            'keep_audio': self.keep_audio_var.get(),
            'auto_merge': self.auto_merge_var.get(),
            'video_format': 'mp4',
            'audio_format': 'mp3',
            'retry_attempts': 3,
            'timeout': 300,
        }
        
    def toggle_pause(self):
        """切換暫停/繼續"""
        # 注意：yt-dlp 不支援暫停/繼續，這裡只是 UI 佔位
        if self.pause_btn.cget('text') == UI_TEXT['pause_button']:
            self.pause_btn.config(text=UI_TEXT['resume_button'])
            self.show_message("暫停功能暫未實現", "warning")
        else:
            self.pause_btn.config(text=UI_TEXT['pause_button'])
            
    def cancel_download(self):
        """取消下載"""
        if self.cancellation_token:
            self.cancellation_token.cancel()
            self.log_message("正在取消下載...")
            
    def on_progress_update(self, progress, message):
        """進度更新回調"""
        self.frame.after(0, self._update_progress_ui, progress, message)
        
    def _update_progress_ui(self, progress, message):
        """更新進度 UI（主執行緒）"""
        self.progress_var.set(progress)
        if message:
            self.speed_label.config(text=message)
            
    def on_status_update(self, status, message):
        """狀態更新回調"""
        self.frame.after(0, self._update_status_ui, status, message)
        
    def _update_status_ui(self, status, message):
        """更新狀態 UI（主執行緒）"""
        if status == DownloadStatus.EXTRACTING:
            self.status_var.set("正在解析視頻資訊...")
        elif status == DownloadStatus.DOWNLOADING:
            self.status_var.set("下載中...")
        elif status == DownloadStatus.MERGING:
            self.status_var.set("正在合併音視頻...")
        elif status == DownloadStatus.COMPLETED:
            self.status_var.set("下載完成")
        elif status == DownloadStatus.FAILED:
            self.status_var.set("下載失敗")
        elif status == DownloadStatus.CANCELLED:
            self.status_var.set("已取消")
            
        if message:
            self.log_message(f"[{status.value}] {message}")
            
    def on_download_complete(self, result, error):
        """下載完成回調"""
        self.frame.after(0, self._handle_download_complete, result, error)
        
    def _handle_download_complete(self, result, error):
        """處理下載完成（主執行緒）"""
        self.set_downloading_state(False)
        
        if error:
            if "已取消" in str(error):
                self.show_message("下載已取消", "warning")
                self.log_message("下載已取消")
            else:
                self.show_message(f"下載失敗: {error}", "error")
                self.log_message(f"下載失敗: {error}")
        else:
            self.show_message(SUCCESS_MESSAGES['download_complete'], "success")
            self.log_message(f"下載完成: {result}")
            
            # 清空 URL
            self.url_placeholder.clear()
            
            # 詢問是否開啟下載資料夾
            if messagebox.askyesno("下載完成", "是否開啟下載資料夾？"):
                self.open_download_folder()
                
    def set_downloading_state(self, downloading):
        """設置下載狀態"""
        self.is_downloading = downloading
        
        if downloading:
            self.download_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.NORMAL)
        else:
            self.download_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            self.cancel_btn.config(state=tk.DISABLED)
            
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
            self.frame.after(5000, lambda: self.show_message("", ""))
            
    def log_message(self, message):
        """記錄日誌訊息"""
        if hasattr(self, 'log_text'):
            timestamp = time.strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            
    def clear_log(self):
        """清空日誌"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
            
    def save_log(self):
        """保存日誌"""
        if hasattr(self, 'log_text'):
            content = self.log_text.get(1.0, tk.END)
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
                        
    def open_download_folder(self):
        """開啟下載資料夾"""
        download_path = self.download_path_var.get()
        if download_path and os.path.exists(download_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(download_path)
                elif os.name == 'posix':  # macOS/Linux
                    os.system(f'open "{download_path}"' if sys.platform == 'darwin' 
                             else f'xdg-open "{download_path}"')
            except Exception as e:
                self.show_message(f"無法開啟資料夾: {e}", "error")
                
    def get_download_path(self):
        """獲取下載路徑"""
        return self.download_path_var.get()
        
    def cleanup(self):
        """清理資源"""
        # 暫時註解掉，避免依賴問題
        # if self.current_task and self.current_task.is_running():
        #     self.cancel_download()
        #     self.current_task.wait(timeout=5)
        pass
        
    def get_prefix_options(self):
        """獲取檔名前綴選項"""
        # 改為直接使用 constants 中由 prename.txt 載入的清單
        return FILENAME_PREFIXES

    def reload_prefix_list(self):
        """重新載入 config/prename.txt 並更新下拉清單"""
        try:
            current = self.prefix_var.get()
            new_list = reload_filename_prefixes()
            # 更新下拉
            self.prefix_combo.configure(values=new_list)
            # 儘量保留原本選擇
            if current in new_list:
                self.prefix_var.set(current)
            else:
                # 若原選擇不在新清單，預設選第一項（空前綴）
                self.prefix_var.set(new_list[0] if new_list else '')
            self.show_message("前綴已重新載入", "success")
        except Exception as e:
            self.show_message(f"重新載入前綴失敗：{e}", "error")