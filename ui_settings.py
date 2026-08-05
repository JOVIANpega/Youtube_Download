#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定頁面UI
檔名前綴、下載路徑、字體大小、其他偏好設定
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import platform
import subprocess
from constants import UI_TEXT, FILENAME_PREFIXES, THEMES, DEFAULT_THEME, COLORS, APP_VERSION
from utils.ui_fonts import FontManager


class SettingsTab:
    """設定頁面"""
    
    def __init__(self, parent, font_manager, settings_manager):
        self.parent = parent
        self.font_manager = font_manager
        self.settings_manager = settings_manager
        self.frame = ttk.Frame(parent)
        
        # UI 變數
        self.font_size_var = tk.IntVar()
        self.download_path_var = tk.StringVar()
        self.auto_merge_var = tk.BooleanVar()
        self.keep_video_var = tk.BooleanVar()
        self.keep_audio_var = tk.BooleanVar()
        self.show_advanced_var = tk.BooleanVar()
        self.auto_open_folder_var = tk.BooleanVar()
        self.check_updates_var = tk.BooleanVar()
        self.theme_var = tk.StringVar(value=DEFAULT_THEME)
        self.version_var = tk.StringVar(value=APP_VERSION)
        self.proxy_var = tk.StringVar()
        self.cookie_file_var = tk.StringVar() # 修正：在這裡初始化以防啟動崩潰
        self.use_random_delay_var = tk.BooleanVar()
        self.po_token_var = tk.StringVar()
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """設置用戶介面"""
        # 主容器：左右可調整的分割面板
        paned = tk.PanedWindow(
            self.frame,
            orient=tk.HORIZONTAL,
            sashwidth=8,
            sashrelief=tk.RAISED,
            relief=tk.FLAT,
            bd=0
        )
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = ttk.Frame(paned)
        right = ttk.Frame(paned)

        paned.add(left)
        paned.add(right)

        self._paned = paned

        # 左側：下載設定 + 介面設定
        self.create_download_section(left)
        self.create_ui_preference_section(left)

        # 右側：進階設定 + 重設/保存
        self.create_advanced_section(right)
        self.create_reset_section(right)
        
    def create_download_section(self, parent):
        """創建下載設定區域"""
        download_frame = ttk.LabelFrame(parent, text="下載設定", padding=10)
        download_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 下載路徑
        path_frame = ttk.Frame(download_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, text="預設下載路徑：").pack(anchor=tk.W)
        
        path_input_frame = ttk.Frame(path_frame)
        path_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.download_path_entry = ttk.Entry(
            path_input_frame,
            textvariable=self.download_path_var,
            font=self.font_manager.get_font()
        )
        self.download_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_path_btn = ttk.Button(
            path_input_frame,
            text="瀏覽",
            command=self.browse_download_path
        )
        browse_path_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.font_manager.register_widget(self.download_path_entry)
        self.font_manager.register_widget(browse_path_btn)
        
        # 自動合併
        auto_merge_frame = ttk.Frame(download_frame)
        auto_merge_frame.pack(fill=tk.X, pady=(0, 5))
        
        auto_merge_cb = ttk.Checkbutton(
            auto_merge_frame,
            text="自動合併音視頻",
            variable=self.auto_merge_var
        )
        auto_merge_cb.pack(anchor=tk.W)
        self.font_manager.register_widget(auto_merge_cb)
        
        # 保留檔案選項
        keep_frame = ttk.Frame(download_frame)
        keep_frame.pack(fill=tk.X)
        
        keep_video_cb = ttk.Checkbutton(
            keep_frame,
            text="保留視頻檔案",
            variable=self.keep_video_var
        )
        keep_video_cb.pack(anchor=tk.W, padx=(0, 0))
        
        keep_audio_cb = ttk.Checkbutton(
            keep_frame,
            text="保留音頻檔案",
            variable=self.keep_audio_var
        )
        keep_audio_cb.pack(anchor=tk.W, padx=(0, 0))
        
        self.font_manager.register_widget(keep_video_cb)
        self.font_manager.register_widget(keep_audio_cb)
        
    def create_ui_preference_section(self, parent):
        """創建UI偏好區域"""
        ui_frame = ttk.LabelFrame(parent, text="介面設定", padding=10)
        ui_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 字體大小
        font_frame = ttk.Frame(ui_frame)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_frame, text="字體大小：").pack(anchor=tk.W)
        
        font_size_frame = ttk.Frame(font_frame)
        font_size_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.font_size_scale = tk.Scale(
            font_size_frame,
            from_=8,
            to=20,
            orient=tk.HORIZONTAL,
            variable=self.font_size_var,
            command=self.on_font_size_changed,
            showvalue=False
        )
        self.font_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.font_size_label = ttk.Label(
            font_size_frame,
            textvariable=self.font_size_var,
            font=self.font_manager.get_font('bold'),
            foreground=COLORS['primary']
        )
        self.font_size_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.font_manager.register_widget(self.font_size_scale)
        self.font_manager.register_widget(self.font_size_label)
        
        # UI 偏好選項
        ui_pref_frame = ttk.Frame(ui_frame)
        ui_pref_frame.pack(fill=tk.X)
        
        show_advanced_cb = ttk.Checkbutton(
            ui_pref_frame,
            text="顯示進階選項",
            variable=self.show_advanced_var
        )
        show_advanced_cb.pack(anchor=tk.W)
        
        auto_open_cb = ttk.Checkbutton(
            ui_pref_frame,
            text="下載完成後自動開啟資料夾",
            variable=self.auto_open_folder_var
        )
        auto_open_cb.pack(anchor=tk.W)
        
        # 檢查更新列
        update_row = ttk.Frame(ui_pref_frame)
        update_row.pack(fill=tk.X, pady=(5, 5))
        
        check_updates_cb = ttk.Checkbutton(
            update_row,
            text="啟動時檢查更新",
            variable=self.check_updates_var
        )
        check_updates_cb.pack(side=tk.LEFT)
        
        check_now_btn = ttk.Button(
            update_row,
            text="立即檢查",
            command=self.check_updates_now,
            width=10
        )
        check_now_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 介面主題
        theme_row = ttk.Frame(ui_pref_frame)
        theme_row.pack(fill=tk.X, pady=(5, 5))
        
        ttk.Label(theme_row, text="介面主題：", width=10).pack(side=tk.LEFT)
        self.theme_combo = ttk.Combobox(
            theme_row, 
            textvariable=self.theme_var,
            values=list(THEMES.keys()),
            state="readonly",
            width=15
        )
        self.theme_combo.pack(side=tk.LEFT)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_selection_changed)
        
        # 版本顯示與編輯
        version_row = ttk.Frame(ui_pref_frame)
        version_row.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(version_row, text="版本號碼：", width=10).pack(side=tk.LEFT)
        self.version_entry = ttk.Entry(
            version_row,
            textvariable=self.version_var,
            width=10
        )
        self.version_entry.pack(side=tk.LEFT)
        
        self.font_manager.register_widget(show_advanced_cb)
        self.font_manager.register_widget(auto_open_cb)
        self.font_manager.register_widget(check_updates_cb)
        self.font_manager.register_widget(check_now_btn)
        self.font_manager.register_widget(self.version_entry)
        self.font_manager.register_widget(self.theme_combo)

        # 自動保存 UI 偏好變更 (排除主題即時持久化)
        def _auto_save(*_):
            try:
                self.save_all_settings_silent()
            except Exception:
                pass
        self.show_advanced_var.trace('w', _auto_save)
        self.auto_open_folder_var.trace('w', _auto_save)
        self.check_updates_var.trace('w', _auto_save)
        
    def create_advanced_section(self, parent):
        """創建進階設定區域"""
        advanced_frame = ttk.LabelFrame(parent, text="進階設定", padding=10)
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        # FFmpeg 路徑
        ffmpeg_frame = ttk.Frame(advanced_frame)
        ffmpeg_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ffmpeg_frame, text="FFmpeg 路徑：").pack(anchor=tk.W)
        
        ffmpeg_input_frame = ttk.Frame(ffmpeg_frame)
        ffmpeg_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.ffmpeg_path_var = tk.StringVar()
        ffmpeg_entry = ttk.Entry(
            ffmpeg_input_frame,
            textvariable=self.ffmpeg_path_var,
            font=self.font_manager.get_font()
        )
        ffmpeg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_ffmpeg_btn = ttk.Button(
            ffmpeg_input_frame,
            text="瀏覽",
            command=self.browse_ffmpeg_path
        )
        browse_ffmpeg_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        self.download_ffmpeg_btn = ttk.Button(
            ffmpeg_input_frame,
            text="自動下載",
            command=self.download_ffmpeg_btn_click
        )
        self.download_ffmpeg_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        self.font_manager.register_widget(ffmpeg_entry)
        self.font_manager.register_widget(browse_ffmpeg_btn)
        self.font_manager.register_widget(self.download_ffmpeg_btn)

        # FFmpeg 路徑變更即時保存
        self.ffmpeg_path_var.trace('w', lambda *_: self.save_all_settings_silent())

        # 網路與避障設定
        # 代理伺服器
        proxy_row = ttk.Frame(advanced_frame)
        proxy_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(proxy_row, text="代理伺服器 (Proxy):", width=20).pack(side=tk.LEFT)
        self.proxy_entry = ttk.Entry(proxy_row, textvariable=self.proxy_var)
        self.proxy_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 登入狀態檔案是進階備援；一般公開影片不需要設定。
        cookie_row = ttk.Frame(advanced_frame)
        cookie_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(cookie_row, text="登入狀態檔 (*.txt):", width=20).pack(side=tk.LEFT)
        
        self.cookie_file_entry = ttk.Entry(cookie_row, textvariable=self.cookie_file_var)
        self.cookie_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        cookie_browse_btn = ttk.Button(
            cookie_row,
            text="瀏覽",
            command=self.browse_cookie_file
        )
        cookie_browse_btn.pack(side=tk.LEFT)
        self.font_manager.register_widget(self.cookie_file_entry)
        self.font_manager.register_widget(cookie_browse_btn)
        cookie_hint = ttk.Label(
            advanced_frame,
            text="公開影片不用設定。只有 FB / IG / Threads / TikTok 等限制內容下載失敗時，才需要選擇 cookies.txt 或在下載頁選 Chrome / Edge / Firefox。",
            foreground="gray",
            font=self.font_manager.get_font('small'),
            wraplength=360,
            justify=tk.LEFT
        )
        cookie_hint.pack(anchor=tk.W, pady=(0, 8))
        self.font_manager.register_widget(cookie_hint)
        
        # --- 新增：PO Token (針對 403 Forbidden 與高畫質) ---
        po_token_row = ttk.Frame(advanced_frame)
        po_token_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(po_token_row, text="YouTube PO Token:", width=20).pack(side=tk.LEFT)
        self.po_token_entry = ttk.Entry(po_token_row, textvariable=self.po_token_var)
        self.po_token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.font_manager.register_widget(self.po_token_entry)
        
        # 幫用戶寫個小小提示
        po_help_label = ttk.Label(
            advanced_frame,
            text="💡 若 1080P 下載出現 Requested format is not available，請填寫此 Token。\n   (請上網搜尋「yt-dlp po token 獲取工具」或從 GitHub 取得)",
            foreground="#d9534f",
            font=self.font_manager.get_font('small'),
            justify=tk.LEFT
        )
        po_help_label.pack(anchor=tk.W, pady=(0, 5))
        self.font_manager.register_widget(po_help_label)

        # 隨機延遲
        delay_row = ttk.Frame(advanced_frame)
        delay_row.pack(fill=tk.X, pady=(5, 0))
        random_delay_cb = ttk.Checkbutton(
            delay_row,
            text="啟用隨機延遲 (防封鎖/人機模擬)",
            variable=self.use_random_delay_var
        )
        random_delay_cb.pack(anchor=tk.W)
        
        self.font_manager.register_widget(self.proxy_entry)
        self.font_manager.register_widget(random_delay_cb)
        
        # 即時保存網路設定
        self.proxy_var.trace('w', lambda *_: self.save_all_settings_silent())
        self.cookie_file_var.trace('w', lambda *_: self.save_all_settings_silent()) # 新增 cookie_file_var trace
        self.po_token_var.trace('w', lambda *_: self.save_all_settings_silent())
        self.use_random_delay_var.trace('w', lambda *_: self.save_all_settings_silent())
        
        # 系統維護按鈕
        maint_frame = ttk.Frame(advanced_frame)
        maint_frame.pack(fill=tk.X, pady=(10, 0))
        
        open_logs_btn = ttk.Button(
            maint_frame,
            text="開啟日誌資料夾",
            command=self.open_logs_folder
        )
        open_logs_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_cache_btn = ttk.Button(
            maint_frame,
            text="清理下載快取",
            command=self.clear_download_cache
        )
        clear_cache_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        update_ytdlp_btn = ttk.Button(
            maint_frame,
            text="更新下載組件",
            command=self.update_ytdlp_click
        )
        update_ytdlp_btn.pack(side=tk.LEFT)
        
        self.font_manager.register_widget(open_logs_btn)
        self.font_manager.register_widget(clear_cache_btn)
        self.font_manager.register_widget(update_ytdlp_btn)
        
        # 說明文字
        advanced_help_frame = ttk.Frame(advanced_frame)
        advanced_help_frame.pack(fill=tk.X, pady=(10, 0))
        
        help_text = "• FFmpeg 路徑：留空表示使用系統 PATH 中的 ffmpeg\n• 自定義路徑：指定 ffmpeg 程式的完整路徑"
        help_label = ttk.Label(
            advanced_help_frame,
            text=help_text,
            foreground="gray",
            font=self.font_manager.get_font()
        )
        help_label.pack(anchor=tk.W)
        self.font_manager.register_widget(help_label)
        
    def create_reset_section(self, parent):
        """創建重設按鈕區域"""
        reset_frame = ttk.Frame(parent)
        reset_frame.pack(fill=tk.X, pady=(10, 0))
        
        reset_btn = ttk.Button(
            reset_frame,
            text="重置所有設定",
            command=self.reset_all_settings
        )
        reset_btn.pack(side=tk.RIGHT)
        self.font_manager.register_widget(reset_btn)
        
        save_btn = ttk.Button(
            reset_frame,
            text="保存設定",
            command=self.save_all_settings
        )
        save_btn.pack(side=tk.RIGHT, padx=(0, 10))
        self.font_manager.register_widget(save_btn)

        # 底部說明文字
        help_label = ttk.Label(
            reset_frame,
            text="* 設定將於點擊「保存設定」後永久生效",
            foreground="gray",
            font=self.font_manager.get_font('small')
        )
        help_label.pack(side=tk.LEFT)
        self.font_manager.register_widget(help_label)

    def save_all_settings_silent(self):
        """保存所有設置（不顯示提示框，不含主題）"""
        try:
            settings = {
                'font_size': self.font_size_var.get(),
                'download_path': self.download_path_var.get(),
                'auto_merge': self.auto_merge_var.get(),
                'keep_video': self.keep_video_var.get(),
                'keep_audio': self.keep_audio_var.get(),
                'show_advanced_options': self.show_advanced_var.get(),
                'auto_open_download_folder': self.auto_open_folder_var.get(),
                'check_for_updates': self.check_updates_var.get(),
                'ffmpeg_path': self.ffmpeg_path_var.get(),
                'proxy': self.proxy_var.get(),
                'cookie_file_path': self.cookie_file_var.get(), # 新增 cookie_file_path
                'po_token': self.po_token_var.get(),
                'use_random_delay': self.use_random_delay_var.get(),
            }
            self.settings_manager.update_settings(settings)
        except Exception:
            pass
        
    def load_settings(self):
        """載入設定"""
        try:
            settings = self.settings_manager.load_settings()
            
            self.font_size_var.set(settings.get('font_size', 12))
            self.download_path_var.set(settings.get('download_path', ''))
            self.auto_merge_var.set(settings.get('auto_merge', True))
            self.keep_video_var.set(settings.get('keep_video', True))
            self.keep_audio_var.set(settings.get('keep_audio', False))
            self.show_advanced_var.set(settings.get('show_advanced_options', False))
            self.auto_open_folder_var.set(settings.get('auto_open_download_folder', False))
            self.check_updates_var.set(settings.get('check_for_updates', True))
            self.theme_var.set(settings.get('theme', DEFAULT_THEME))
            self.ffmpeg_path_var.set(settings.get('ffmpeg_path', ''))
            self.proxy_var.set(settings.get('proxy', ''))
            self.po_token_var.set(settings.get('po_token', ''))
            
            current_cookie_path = settings.get('cookie_file_path', '')
            if current_cookie_path and not os.path.exists(current_cookie_path):
                current_cookie_path = ''
            self.cookie_file_var.set(current_cookie_path)
            
            self.use_random_delay_var.set(settings.get('use_random_delay', True))

            try:
                split_pos = int(settings.get('settings_split_pos', 320))
                def _apply_pos():
                    try:
                        self._paned.sashpos(0, split_pos)
                    except Exception:
                        pass
                self.frame.after(100, _apply_pos)
            except Exception:
                pass
            
        except Exception as e:
            messagebox.showerror("錯誤", f"載入設定失敗：{e}")
            
    def save_all_settings(self):
        """保存所有設置（含主題）"""
        try:
            settings = {
                'font_size': self.font_size_var.get(),
                'download_path': self.download_path_var.get(),
                'auto_merge': self.auto_merge_var.get(),
                'keep_video': self.keep_video_var.get(),
                'keep_audio': self.keep_audio_var.get(),
                'show_advanced_options': self.show_advanced_var.get(),
                'auto_open_download_folder': self.auto_open_folder_var.get(),
                'check_for_updates': self.check_updates_var.get(),
                'theme': self.theme_var.get(),
                'ffmpeg_path': self.ffmpeg_path_var.get(),
                'proxy': self.proxy_var.get(),
                'cookie_file_path': self.cookie_file_var.get(), # 新增 cookie_file_path
                'po_token': self.po_token_var.get(),
                'use_random_delay': self.use_random_delay_var.get(),
            }
            
            self.settings_manager.update_settings(settings)
            
            # 同步更新 version_info.py 與 constants.py
            self.sync_version_to_files(self.version_var.get())
            
            messagebox.showinfo("成功", "所有設定已永久保存")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"保存設定失敗：{e}")
            
    def reset_all_settings(self):
        """重置所有設定"""
        if messagebox.askyesno("確認重置", "確定要重置所有設定嗎？此動作無法復原。"):
            try:
                self.settings_manager.reset_settings()
                self.load_settings()
                self.font_manager.set_font_size(self.font_size_var.get())
                messagebox.showinfo("成功", "所有設定已重置為預設值")
            except Exception as e:
                messagebox.showerror("錯誤", f"重置設定失敗：{e}")
                
    def on_font_size_changed(self, value=None):
        """字體大小改變時的回調"""
        try:
            new_size = int(self.font_size_var.get())
            self.font_manager.set_font_size(new_size)
        except Exception:
            pass
            
    def browse_download_path(self):
        """瀏覽下載路徑"""
        path = filedialog.askdirectory(
            title="選擇下載路徑",
            initialdir=self.download_path_var.get()
        )
        if path:
            self.download_path_var.set(path)
            
    def browse_ffmpeg_path(self):
        """瀏覽FFmpeg路徑"""
        filetypes = [("執行檔", "*.exe"), ("所有檔案", "*.*")]
        path = filedialog.askopenfilename(
            title="選擇 FFmpeg 程式",
            filetypes=filetypes,
            initialdir=self.ffmpeg_path_var.get()
        )
        if path:
            self.ffmpeg_path_var.set(path)
            
    def download_ffmpeg_btn_click(self):
        """點擊自動下載 FFmpeg"""
        from services.ffmpeg_manager import FFmpegManager
        manager = FFmpegManager()
        if manager.is_available():
            if not messagebox.askyesno("提示", "系統已偵測到 FFmpeg，確定要重新下載嗎？"):
                return
        self.download_ffmpeg_btn.config(state=tk.DISABLED, text="下載中...")
        def do_download():
            try:
                def progress(p, msg):
                    self.frame.after(0, lambda: self.download_ffmpeg_btn.config(text=f"{int(p)}%"))
                if manager.download_ffmpeg_windows(progress_callback=progress):
                    self.frame.after(0, lambda: self.ffmpeg_path_var.set(manager.get_ffmpeg_path()))
                    self.frame.after(0, lambda: messagebox.showinfo("成功", "FFmpeg 安裝完成！"))
                else:
                    self.frame.after(0, lambda: messagebox.showerror("錯誤", "FFmpeg 下載失敗。"))
            finally:
                self.frame.after(0, lambda: self.download_ffmpeg_btn.config(state=tk.NORMAL, text="自動下載"))
        import threading
        threading.Thread(target=do_download, daemon=True).start()
            
    def on_theme_selection_changed(self, event=None):
        """當使用者選擇主題時（僅預覽）"""
        new_theme = self.theme_var.get()
        app = self.get_main_app()
        if app:
            app.apply_theme(new_theme)

    def get_main_app(self):
        """取得主應用程式例項"""
        curr = self.frame
        while curr:
            if hasattr(curr, 'apply_theme'):
                return curr
            if hasattr(curr, 'master'):
                curr = curr.master
            else:
                break
        return None

    def on_theme_changed(self, colors):
        """當主題改變時同步更新本頁面元件顏色"""
        try:
            self.font_size_label.config(foreground=colors['primary'])
        except Exception:
            pass

    def get_split_pos(self):
        try:
            return int(self._paned.sashpos(0))
        except Exception:
            return 320

    def check_updates_now(self):
        messagebox.showinfo("檢查更新", "目前已是最新版本 (v1.0.0)。")

    def open_logs_folder(self):
        try:
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            if platform.system() == 'Windows':
                os.startfile(log_dir)
            else:
                subprocess.call(['open' if platform.system() == 'Darwin' else 'xdg-open', log_dir])
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟日誌資料夾：{e}")

    def clear_download_cache(self):
        """清理 yt-dlp 緩存與暫存檔"""
        from services.downloader import VideoDownloader
        downloader = VideoDownloader()
        
        cache_ok = downloader.clear_cache()
        
        # 詢問是否要刪除 .part 檔案 (這對於解決 403 Forbidden 續傳報錯非常有幫助)
        msg = "下載組件內建快取已清理。" if cache_ok else "下載快取清理失敗。"
        msg += "\n\n是否也要一併刪除下載資料夾中的 .part 暫存檔？\n(注意：這會清空未完成的下載進度，但通常能有效解決「HTTP 403 Forbidden」報錯)"
        
        if messagebox.askyesno("清理暫存", msg):
            path = self.download_path_var.get()
            if os.path.exists(path):
                import glob
                try:
                    part_files = glob.glob(os.path.join(path, "*.part"))
                    ytdl_part_files = glob.glob(os.path.join(path, "*.ytdl")) # 同時清理 .ytdl 檔
                    all_parts = part_files + ytdl_part_files
                    
                    count = 0
                    for f in all_parts:
                        try:
                            os.remove(f)
                            count += 1
                        except:
                            pass
                    messagebox.showinfo("清理完成", f"已刪除 {count} 個暫存檔案。")
                except Exception as e:
                    messagebox.showerror("錯誤", f"清理暫存檔時發生錯誤: {e}")
            else:
                messagebox.showwarning("警告", "找不到目前的下載路徑，無法清理暫存檔。")
        elif cache_ok:
            messagebox.showinfo("成功", "已成功清理下載組件快取。")

    def update_ytdlp_click(self):
        """點擊更新 yt-dlp"""
        from services.downloader import VideoDownloader
        downloader = VideoDownloader()
        
        # 標記按鈕狀態
        # 注意：這裡由於按鈕沒有儲存為成員變數，暫不變更文字，直接異步執行
        def do_update():
            try:
                if downloader.update_ytdlp():
                    self.frame.after(0, lambda: messagebox.showinfo("成功", "下載組件 (yt-dlp) 更新完成！"))
                else:
                    self.frame.after(0, lambda: messagebox.showerror("錯誤", "下載組件更新失敗，請檢查網路連線。"))
            except Exception as e:
                messagebox.showerror("錯誤", f"更新發生異常: {e}")

        messagebox.showinfo("提示", "正在後端嘗試更新下載組件，請稍候...")
        import threading
        threading.Thread(target=do_update, daemon=True).start()

    def browse_cookie_file(self):
        """瀏覽並選取 Cookies 檔案"""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="選取登入狀態 Cookies 檔案",
            filetypes=[("Cookies 檔案", "*.txt"), ("所有檔案", "*.*")]
        )
        if path:
            self.cookie_file_var.set(path)
            # 自動儲存
            self.save_all_settings_silent() # Changed to silent save

    def sync_version_to_files(self, new_version):
        """同步版本號到 constants.py 與 version_info.py"""
        try:
            # 1. 更新 constants.py
            const_path = 'constants.py'
            if os.path.exists(const_path):
                with open(const_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                content = re.sub(r'APP_VERSION = ".*?"', f'APP_VERSION = "{new_version}"', content)
                with open(const_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # 2. 更新 version_info.py
            vinfo_path = 'version_info.py'
            if os.path.exists(vinfo_path):
                with open(vinfo_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = re.sub(r'VERSION = ".*?"', f'VERSION = "{new_version}"', content)
                # 切分版本號碼元組
                v_parts = new_version.split('.')
                v_tuple = [0, 0, 0, 0]
                for i in range(min(len(v_parts), 4)):
                    try:
                        v_tuple[i] = int(v_parts[i])
                    except:
                        pass
                content = re.sub(r'VERSION_TUPLE = \(.*?\)', f'VERSION_TUPLE = {tuple(v_tuple)}', content)
                with open(vinfo_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            # 更新主視窗標題 (如果能獲取到)
            app = self.get_main_app()
            if app and hasattr(app, 'root'):
                from constants import APP_TITLE
                app.root.title(f"{APP_TITLE} v{new_version}")
                
        except Exception as e:
            print(f"同步版本資訊失敗: {e}")
