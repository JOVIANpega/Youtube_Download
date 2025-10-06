#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復版主程式
使用簡化的UI模組，避免複雜依賴
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import traceback

# 導入基本模組
from ui_download_simple import DownloadTabSimple
from ui_external import ExternalTab
from ui_history import HistoryTab
from utils.ui_fonts import FontManager
from utils.path_utils import get_resource_path
from services.settings import SettingsManager
from logging_config import setup_logging
from constants import APP_TITLE, WINDOW_SIZE, MIN_WINDOW_SIZE
import version_info

class MainApplicationFixed:
    """修復版主應用程式類"""
    
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
        self.root.title(f"{APP_TITLE} v{version_info.VERSION} (修復版)")
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
        self.logger.info(f"修復版應用程式啟動 - 版本 {version_info.VERSION}")
        
    def setup_managers(self):
        """設置管理器"""
        self.settings_manager = SettingsManager()
        self.font_manager = FontManager(self.root)
        
    def setup_ui(self):
        """設置用戶介面"""
        # 創建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 創建頂部框架（標題和字體控制）
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 標題
        title_label = ttk.Label(top_frame, text=f"{APP_TITLE} (修復版)", 
                               font=('Arial', 14, 'bold'))
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
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 創建各個分頁（使用簡化版）
        try:
            self.download_tab = DownloadTabSimple(self.notebook, self.font_manager, self.settings_manager)
            self.notebook.add(self.download_tab.frame, text="下載 (簡化版)")
            print("✅ 下載頁面創建成功")
        except Exception as e:
            print(f"❌ 下載頁面創建失敗: {e}")
            # 創建錯誤頁面
            error_frame = ttk.Frame(self.notebook)
            ttk.Label(error_frame, text=f"下載頁面載入失敗: {e}").pack(pady=20)
            self.notebook.add(error_frame, text="下載 (錯誤)")
        
        try:
            self.external_tab = ExternalTab(self.notebook, self.font_manager)
            self.notebook.add(self.external_tab.frame, text="外部下載器")
            print("✅ 外部下載器頁面創建成功")
        except Exception as e:
            print(f"❌ 外部下載器頁面創建失敗: {e}")
            # 創建錯誤頁面
            error_frame = ttk.Frame(self.notebook)
            ttk.Label(error_frame, text=f"外部下載器頁面載入失敗: {e}").pack(pady=20)
            self.notebook.add(error_frame, text="外部下載器 (錯誤)")
        
        try:
            self.history_tab = HistoryTab(self.notebook, self.font_manager)
            self.notebook.add(self.history_tab.frame, text="歷史記錄")
            print("✅ 歷史記錄頁面創建成功")
        except Exception as e:
            print(f"❌ 歷史記錄頁面創建失敗: {e}")
            # 創建錯誤頁面
            error_frame = ttk.Frame(self.notebook)
            ttk.Label(error_frame, text=f"歷史記錄頁面載入失敗: {e}").pack(pady=20)
            self.notebook.add(error_frame, text="歷史記錄 (錯誤)")
        
        # 創建狀態列
        self.status_bar = ttk.Label(main_frame, text="修復版就緒", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 添加說明標籤
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        info_text = "修復版說明: 這是簡化版本，避免了複雜依賴。要獲得完整功能請安裝 yt-dlp。"
        info_label = ttk.Label(info_frame, text=info_text, foreground="blue", 
                              font=self.font_manager.get_font('small'))
        info_label.pack()
        
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
            }
            
            # 嘗試獲取下載路徑
            try:
                if hasattr(self, 'download_tab'):
                    settings['download_path'] = self.download_tab.get_download_path()
            except:
                pass
                
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
            
            # 清理資源
            if hasattr(self, 'download_tab'):
                self.download_tab.cleanup()
                
            self.logger.info("修復版應用程式正常關閉")
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
        print("🚀 啟動修復版 YouTube 下載器...")
        app = MainApplicationFixed()
        print("✅ 應用程式創建成功")
        app.run()
    except Exception as e:
        print(f"❌ 啟動應用程式失敗: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()