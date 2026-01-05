#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定頁面UI
檔名前綴、下載路徑、字體大小、其他偏好設定
"""

import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import platform
import subprocess
from constants import UI_TEXT, FILENAME_PREFIXES
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
        self.filename_prefix_var = tk.StringVar()
        self.custom_prefix_var = tk.StringVar()
        self.auto_merge_var = tk.BooleanVar()
        self.keep_video_var = tk.BooleanVar()
        self.keep_audio_var = tk.BooleanVar()
        self.show_advanced_var = tk.BooleanVar()
        self.auto_open_folder_var = tk.BooleanVar()
        self.check_updates_var = tk.BooleanVar()
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """設置用戶介面"""
        # 主容器：左右可調整的分割面板（改用 tk.PanedWindow 提供較明顯的分隔拖曳區）
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
        
        font_size_scale = tk.Scale(
            font_size_frame,
            from_=8,
            to=20,
            orient=tk.HORIZONTAL,
            variable=self.font_size_var,
            command=self.on_font_size_changed
        )
        font_size_scale.pack(fill=tk.X)
        
        font_size_label = ttk.Label(
            font_size_frame,
            textvariable=self.font_size_var,
            font=self.font_manager.get_font()
        )
        font_size_label.pack(anchor=tk.W, pady=(5, 0))
        
        self.font_manager.register_widget(font_size_scale)
        self.font_manager.register_widget(font_size_label)
        
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
        update_row.pack(fill=tk.X, pady=(5, 0))
        
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
        
        self.font_manager.register_widget(show_advanced_cb)
        self.font_manager.register_widget(auto_open_cb)
        self.font_manager.register_widget(check_updates_cb)
        self.font_manager.register_widget(check_now_btn)

        # 自動保存 UI 偏好變更
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
        
        # 新增自動下載按鈕
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
        
        # 系統維護按鈕
        maint_frame = ttk.Frame(advanced_frame)
        maint_frame.pack(fill=tk.X, pady=(10, 0))
        
        open_logs_btn = ttk.Button(
            maint_frame,
            text="開啟日誌資料夾",
            command=self.open_logs_folder
        )
        open_logs_btn.pack(side=tk.LEFT)
        self.font_manager.register_widget(open_logs_btn)
        
        # 說明文字
        advanced_help_frame = ttk.Frame(advanced_frame)
        advanced_help_frame.pack(fill=tk.X, pady=(10, 0))
        
        help_text = """進階設定說明：
• FFmpeg 路徑：留空表示使用系統 PATH 中的 ffmpeg
• 自定義路徑：指定 ffmpeg 程式的完整路徑
        """
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

        # 在設定分頁提供「進階選項」切換按鈕，呼叫下載分頁的切換方法
        try:
            from ui_download import DownloadTab  # 僅用於型別提示
            adv_btn = ttk.Button(
                reset_frame,
                text="切換進階選項",
                command=lambda: getattr(self.parent.master, 'download_tab', None) and self.parent.master.download_tab.toggle_advanced()
            )
            adv_btn.pack(side=tk.LEFT)
            self.font_manager.register_widget(adv_btn)
        except Exception:
            pass

        # 分割條位置在視窗關閉時由 main.py 保存，這裡也提供立即保存入口
        try:
            self._paned.bind('<ButtonRelease-1>', lambda e: self.settings_manager.set_setting('settings_split_pos', self.get_split_pos()))
        except Exception:
            pass

    def save_all_settings_silent(self):
        """保存所有設置（不顯示提示框）"""
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
            }
            self.settings_manager.update_settings(settings)
        except Exception:
            # 靜默失敗以避免啟動時彈窗
            pass
        
    def load_settings(self):
        """載入設定"""
        try:
            settings = self.settings_manager.load_settings()
            
            # 載入各項設定
            self.font_size_var.set(settings.get('font_size', 12))
            self.download_path_var.set(settings.get('download_path', ''))
            # 已不在設定頁設定前綴
            
            self.auto_merge_var.set(settings.get('auto_merge', True))
            self.keep_video_var.set(settings.get('keep_video', True))
            self.keep_audio_var.set(settings.get('keep_audio', False))
            
            self.show_advanced_var.set(settings.get('show_advanced_options', False))
            self.auto_open_folder_var.set(settings.get('auto_open_download_folder', False))
            self.check_updates_var.set(settings.get('check_for_updates', True))
            
            # FFmpeg 路徑
            self.ffmpeg_path_var.set(settings.get('ffmpeg_path', ''))

            # 分割條位置
            try:
                split_pos = int(settings.get('settings_split_pos', 320))
                def _apply_pos():
                    try:
                        self._paned.sashpos(0, split_pos)
                    except Exception:
                        pass
                # 多次嘗試以確保在各平台布局完成後套用
                self.frame.after(0, _apply_pos)
                self.frame.after(100, _apply_pos)
                self.frame.after(300, _apply_pos)
            except Exception:
                pass
            
        except Exception as e:
            messagebox.showerror("錯誤", f"載入設定失敗：{e}")
            
    def save_all_settings(self):
        """保存所有設置"""
        try:
            settings = {
                'font_size': self.font_size_var.get(),
                'download_path': self.download_path_var.get(),
                # 'filename_prefix' 已移除由設定頁維護
                'auto_merge': self.auto_merge_var.get(),
                'keep_video': self.keep_video_var.get(),
                'keep_audio': self.keep_audio_var.get(),
                'show_advanced_options': self.show_advanced_var.get(),
                'auto_open_download_folder': self.auto_open_folder_var.get(),
                'check_for_updates': self.check_updates_var.get(),
                'ffmpeg_path': self.ffmpeg_path_var.get(),
            }
            
            self.settings_manager.update_settings(settings)
            messagebox.showinfo("成功", "設定已保存")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"保存設定失敗：{e}")
            
    def reset_all_settings(self):
        """重置所有設定"""
        result = messagebox.askyesno(
            "確認重置",
            "確定要重置所有設定嗎？這個動作無法復原。"
        )
        
        if result:
            try:
                self.settings_manager.reset_settings()
                self.load_settings()
                
                # 更新字體大小
                new_size = self.font_size_var.get()
                self.font_manager.set_font_size(new_size)
                
                messagebox.showinfo("成功", "所有設定已重置為預設值")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"重置設定失敗：{e}")
                
    def on_font_size_changed(self, value=None):
        """字體大小改變時的回調"""
        try:
            new_size = int(self.font_size_var.get())
            self.font_manager.set_font_size(new_size)
        except Exception as e:
            print(f"字體大小更新錯誤: {e}")
            
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
        
        # Windows 的可執行檔案類型
        filetypes = [
            ("執行檔", "*.exe"),
            ("所有檔案", "*.*")
        ]
        
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
                
                success = manager.download_ffmpeg_windows(progress_callback=progress)
                
                if success:
                    self.frame.after(0, lambda: self.ffmpeg_path_var.set(manager.get_ffmpeg_path()))
                    self.frame.after(0, lambda: messagebox.showinfo("成功", "FFmpeg 安裝完成！現在您可以下載高品質影片了。"))
                else:
                    self.frame.after(0, lambda: messagebox.showerror("錯誤", "FFmpeg 下載失敗，請檢查網路連線或稍後再試。"))
            finally:
                self.frame.after(0, lambda: self.download_ffmpeg_btn.config(state=tk.NORMAL, text="自動下載"))
        
        import threading
        threading.Thread(target=do_download, daemon=True).start()
            
    def get_filename_prefix(self):
        """獲取當前選擇的檔名前綴"""
        return self.filename_prefix_var.get()
        
    def get_download_path(self):
        """獲取當前設置的下載路徑"""
        return self.download_path_var.get()

    def get_split_pos(self):
        """取得當前分割條位置"""
        try:
            return int(self._paned.sashpos(0))
        except Exception:
            return 320

    def check_updates_now(self):
        """立即檢查更新（模擬）"""
        messagebox.showinfo("檢查更新", "目前已是最新版本 (v1.0.0)。")

    def open_logs_folder(self):
        """開啟日誌資料夾"""
        try:
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            if platform.system() == 'Windows':
                os.startfile(log_dir)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', log_dir])
            else:
                subprocess.call(['xdg-open', log_dir])
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟日誌資料夾：{e}")
