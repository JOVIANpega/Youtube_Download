#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 下載器主程式
主視窗、分頁容器、全域字體控制、狀態列、全域例外處理
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
import traceback

from services.history_store import HistoryStore

# 導入自定義模組
from ui_download import DownloadTab
from ui_external import ExternalTab
from ui_history import HistoryTab
from ui_settings import SettingsTab
from utils.ui_fonts import FontManager
from utils.path_utils import get_resource_path
from services.settings import SettingsManager
from logging_config import setup_logging
from constants import APP_TITLE, WINDOW_SIZE, MIN_WINDOW_SIZE
import version_info

class MainApplication:
    """主應用程式類"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_logging()
        self.setup_managers()
        self.setup_ui()
        self.setup_exception_handler()
        self.load_settings()
        
    def setup_window(self):
        """設置主視窗"""
        self.root.title(f"{APP_TITLE} v{version_info.VERSION}")
        self.root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.root.minsize(*MIN_WINDOW_SIZE)
        
        # 設置圖標
        try:
            icon_path = get_resource_path("assets/icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"無法載入圖標: {e}")
            
    def setup_logging(self):
        """設置日誌"""
        self.logger = setup_logging()
        self.logger.info(f"應用程式啟動 - 版本 {version_info.VERSION}")
        
    def setup_managers(self):
        """設置管理器"""
        self.settings_manager = SettingsManager()
        self.font_manager = FontManager(self.root)
        self.history_store = HistoryStore()
        self.root.option_add("*Font", self.font_manager.get_font())
        
    def setup_ui(self):
        """設置用戶介面"""
        # 創建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 創建頂部框架（標題和字體控制）
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 標題
        title_label = ttk.Label(top_frame, text=APP_TITLE, font=('Arial', 14, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # 字體控制按鈕
        font_frame = ttk.Frame(top_frame)
        font_frame.pack(side=tk.RIGHT)
        
        ttk.Button(font_frame, text="A-", width=3, 
                  command=self.font_manager.decrease_font).pack(side=tk.LEFT, padx=2)
        ttk.Button(font_frame, text="A+", width=3, 
                  command=self.font_manager.increase_font).pack(side=tk.LEFT)
        
        # 創建分頁控件
        self.notebook = ttk.Notebook(main_frame)
        # 樣式：TAB 標籤顏色與 hover 效果
        try:
            style = ttk.Style(self.root)
            # Notebook 背景與分頁未選取顏色
            style.configure('TNotebook', background='#e9edf3')
            style.configure('TNotebook.Tab', padding=(12, 6), background='#f2f4f7', foreground='#000000')
            # 分頁顏色對比：選取深藍底、黑字；未選取黑色字；hover 淺藍底
            style.map('TNotebook.Tab',
                      background=[('selected', '#2b6cb0'), ('active', '#e6f0ff'), ('!selected', '#f2f4f7')],
                      foreground=[('selected', '#000000'), ('!selected', '#000000'), ('active', '#000000')])
        except Exception:
            pass
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 創建各個分頁
        self.download_tab = DownloadTab(self.notebook, self.font_manager, self.settings_manager, self.history_store)
        self.external_tab = ExternalTab(self.notebook, self.font_manager)
        self.history_tab = HistoryTab(self.notebook, self.font_manager, self.history_store)
        self.settings_tab = SettingsTab(self.notebook, self.font_manager, self.settings_manager)
        
        # 添加分頁到筆記本
        self.notebook.add(self.download_tab.frame, text="下載")
        self.notebook.add(self.external_tab.frame, text="外部下載器")
        self.notebook.add(self.history_tab.frame, text="歷史記錄")
        self.notebook.add(self.settings_tab.frame, text="設定")
        
        # 綁定分頁切換事件，自動刷新內容
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # 創建狀態列
        self.status_bar = ttk.Label(main_frame, text="就緒", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def on_tab_changed(self, event):
        """當切換分頁時執行"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        
        if tab_text == "歷史記錄":
            self.history_tab.refresh_data()
        elif tab_text == "設定":
            self.settings_tab.load_settings()
        elif tab_text == "下載":
            # 下載分頁若有需要刷新 (如前綴清單等)
            if hasattr(self.download_tab, 'reload_prefix_list'):
                self.download_tab.reload_prefix_list()

    def setup_exception_handler(self):
        """設置全域例外處理"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
                
            error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.logger.error(f"未處理的例外: {error_msg}")
            
            messagebox.showerror("錯誤", f"發生未預期的錯誤:\n{exc_value}")
            
        sys.excepthook = handle_exception
        
    def load_settings(self):
        """載入設置"""
        try:
            settings = self.settings_manager.load_settings()
            
            # 恢復視窗位置和大小
            if 'window_geometry' in settings:
                self.root.geometry(settings['window_geometry'])
                
            # 恢復字體大小
            if 'font_size' in settings:
                self.font_manager.set_font_size(settings['font_size'])
                
        except Exception as e:
            self.logger.error(f"載入設置失敗: {e}")
            
    def save_settings(self):
        """保存設置"""
        try:
            settings = {
                'window_geometry': self.root.geometry(),
                'font_size': self.font_manager.current_size,
                'download_path': self.download_tab.get_download_path(),
                'settings_split_pos': getattr(self.settings_tab, 'get_split_pos', lambda: 320)(),
            }
            
            # 從下載分頁取得額外設定
            if hasattr(self, 'download_tab'):
                # 獲取品質代碼
                quality_text = self.download_tab.quality_var.get()
                quality_value = "best"
                from ui_download import QUALITY_OPTIONS # 確保能存取
                for text, val in QUALITY_OPTIONS:
                    if text == quality_text:
                        quality_value = val
                        break
                
                settings.update({
                    'quality_preference': quality_value,
                    'browser_preference': self.download_tab._get_browser_code(self.download_tab.browser_var.get()),
                    'filename_prefix': self.download_tab.prefix_var.get(),
                })

            # 如果有設定分頁，保存其設定
            if hasattr(self, 'settings_tab'):
                settings.update({
                    'auto_merge': self.settings_tab.auto_merge_var.get(),
                    'keep_video': self.settings_tab.keep_video_var.get(),
                    'keep_audio': self.settings_tab.keep_audio_var.get(),
                    'show_advanced_options': self.settings_tab.show_advanced_var.get(),
                    'auto_open_download_folder': self.settings_tab.auto_open_folder_var.get(),
                    'check_for_updates': self.settings_tab.check_updates_var.get(),
                    'ffmpeg_path': self.settings_tab.ffmpeg_path_var.get(),
                })
            
            self.settings_manager.save_settings(settings)
        except Exception as e:
            self.logger.error(f"保存設置失敗: {e}")
            
    def update_status(self, message):
        """更新狀態列"""
        self.status_bar.config(text=message)
        
    def on_closing(self):
        """關閉應用程式時的處理"""
        try:
            self.save_settings()
            self.download_tab.cleanup()
            self.logger.info("應用程式正常關閉")
        except Exception as e:
            self.logger.error(f"關閉時發生錯誤: {e}")
        finally:
            self.root.destroy()
            
    def run(self):
        """運行應用程式"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """主函數"""
    try:
        app = MainApplication()
        app.run()
    except Exception as e:
        print(f"啟動應用程式失敗: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()