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
        # 主容器：左右可調整的分割面板
        paned = ttk.Panedwindow(self.frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = ttk.Frame(paned)
        right = ttk.Frame(paned)

        paned.add(left, weight=1)
        paned.add(right, weight=1)

        self._paned = paned

        # 左側：下載設定 + 介面設定
        self.create_download_section(left)
        self.create_ui_preference_section(left)

        # 右側：進階設定 + 重設/保存
        self.create_advanced_section(right)
        self.create_reset_section(right)
        
    def create_filename_section(self, parent):
        """創建檔案命名區域（前綴項已移除）"""
        filename_frame = ttk.LabelFrame(parent, text="檔案命名設定", padding=10)
        filename_frame.pack(fill=tk.X, pady=(0, 10))
        info_label = ttk.Label(
            filename_frame,
            text="前綴現由 config/prename.txt 管理，請編輯該檔案後重啟程式生效。",
            foreground="gray",
            font=self.font_manager.get_font()
        )
        info_label.pack(anchor=tk.W)
        self.font_manager.register_widget(info_label)
        
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
        
        check_updates_cb = ttk.Checkbutton(
            ui_pref_frame,
            text="檢查程式更新",
            variable=self.check_updates_var
        )
        check_updates_cb.pack(anchor=tk.W)
        
        self.font_manager.register_widget(show_advanced_cb)
        self.font_manager.register_widget(auto_open_cb)
        self.font_manager.register_widget(check_updates_cb)
        
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
        browse_ffmpeg_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.font_manager.register_widget(ffmpeg_entry)
        self.font_manager.register_widget(browse_ffmpeg_btn)
        
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
                # 延後設置，確保控件已經布局完成
                self.frame.after(0, lambda: self._paned.sashpos(0, split_pos))
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
            
    # 前綴相關的互動已移除
                
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
