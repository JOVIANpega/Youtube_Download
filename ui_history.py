#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歷史記錄頁面UI
顯示下載歷史、搜索、統計與管理功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform
import webbrowser
from services.history_store import HistoryStore
from constants import UI_TEXT

class HistoryTab:
    """歷史記錄分頁"""
    
    def __init__(self, parent, font_manager, history_store=None):
        self.parent = parent
        self.font_manager = font_manager
        self.history_store = history_store or HistoryStore()
        self.frame = ttk.Frame(parent)
        
        # UI 變數
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """設置用戶介面"""
        # 頂部控制欄
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 搜索框
        ttk.Label(control_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        
        # 刷新按鈕
        refresh_btn = ttk.Button(control_frame, text="刷新", command=self.refresh_data, width=8)
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        # 清除按鈕
        clear_btn = ttk.Button(control_frame, text="清除歷史", command=self.clear_history, width=10)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # 統計資訊標籤
        self.stats_label = ttk.Label(self.frame, text="載入中...", foreground="gray")
        self.stats_label.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # 表格區域
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 滾動條
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ('title', 'platform', 'quality', 'time', 'status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                selectmode='browse', yscrollcommand=scrollbar.set)
        
        # 設置列標題
        self.tree.heading('title', text='標題')
        self.tree.heading('platform', text='平台')
        self.tree.heading('quality', text='品質')
        self.tree.heading('time', text='時間')
        self.tree.heading('status', text='狀態')
        
        # 設置列寬
        self.tree.column('title', width=200, anchor=tk.W)
        self.tree.column('platform', width=80, anchor=tk.CENTER)
        self.tree.column('quality', width=80, anchor=tk.CENTER)
        self.tree.column('time', width=130, anchor=tk.CENTER)
        self.tree.column('status', width=60, anchor=tk.CENTER)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # 右鍵選單
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="開啟檔案", command=self.open_file)
        self.context_menu.add_command(label="開啟資料夾", command=self.open_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="複製 URL", command=self.copy_url)
        self.context_menu.add_command(label="在瀏覽器開啟", command=self.open_browser)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="刪除記錄", command=self.delete_selected)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.open_file())
        
        # 註冊字體
        self.font_manager.register_widget(self.search_entry)
        self.font_manager.register_widget(refresh_btn)
        self.font_manager.register_widget(clear_btn)
        self.font_manager.register_widget(self.stats_label)
        self.font_manager.register_widget(self.tree)
        
    def refresh_data(self):
        """刷新歷史記錄顯示"""
        # 清空現有表格
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        history = self.history_store.get_history()
        search_term = self.search_var.get().lower()
        
        for i, record in enumerate(history):
            title = record.get('title', '')
            platform_name = record.get('platform', '')
            
            # 搜索過濾
            if search_term and search_term not in title.lower() and search_term not in platform_name.lower():
                continue
                
            self.tree.insert('', tk.END, iid=i, values=(
                title,
                platform_name,
                record.get('quality', ''),
                record.get('timestamp', ''),
                record.get('status', '')
            ))
            
        # 更新統計板
        stats = self.history_store.get_stats()
        self.stats_label.config(text=f"總下載: {stats['total_count']} | 成功: {stats['successful_count']} | 篩選後: {len(self.tree.get_children())}")
        
    def on_search_change(self, *args):
        """搜索詞變化時"""
        self.refresh_data()
        
    def show_context_menu(self, event):
        """顯示右鍵選單"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def get_selected_record(self):
        """獲取選取的記錄物件"""
        selection = self.tree.selection()
        if selection:
            idx = int(selection[0])
            return self.history_store.get_history()[idx]
        return None
        
    def open_file(self):
        """開啟選取的檔案"""
        record = self.get_selected_record()
        if record and record.get('filename'):
            # 這邊需要知道下載路徑，假設在 record 裡也有存
            path = record.get('filepath') 
            if not path:
                # 嘗試在預設下載路徑尋找
                from services.settings import SettingsManager
                sm = SettingsManager()
                default_path = sm.get_setting('download_path')
                if default_path:
                    path = os.path.join(default_path, record.get('filename'))
            
            if path and os.path.exists(path):
                try:
                    if platform.system() == 'Windows':
                        os.startfile(path)
                    elif platform.system() == 'Darwin':
                        subprocess.call(['open', path])
                    else:
                        subprocess.call(['xdg-open', path])
                except Exception as e:
                    messagebox.showerror("錯誤", f"無法開啟檔案: {e}")
            else:
                messagebox.showwarning("警告", "檔案不存在或已被移動")
                
    def open_folder(self):
        """開啟選取的資料夾"""
        record = self.get_selected_record()
        if record:
            path = record.get('filepath')
            if path:
                folder = os.path.dirname(path)
            else:
                from services.settings import SettingsManager
                sm = SettingsManager()
                folder = sm.get_setting('download_path')
                
            if folder and os.path.exists(folder):
                try:
                    if platform.system() == 'Windows':
                        os.startfile(folder)
                    else:
                        subprocess.call(['open' if platform.system() == 'Darwin' else 'xdg-open', folder])
                except Exception as e:
                    messagebox.showerror("錯誤", f"無法開啟資料夾: {e}")
                    
    def copy_url(self):
        """複製 URL 到剪貼簿"""
        record = self.get_selected_record()
        if record and record.get('url'):
            self.frame.clipboard_clear()
            self.frame.clipboard_append(record.get('url'))
            messagebox.showinfo("成功", "URL 已複製到剪貼簿")
            
    def open_browser(self):
        """在瀏覽器中開啟"""
        record = self.get_selected_record()
        if record and record.get('url'):
            webbrowser.open(record.get('url'))
            
    def delete_selected(self):
        """刪除選取的記錄"""
        selection = self.tree.selection()
        if selection:
            if messagebox.askyesno("確認刪除", "確定要刪除這條下載記錄嗎？"):
                idx = int(selection[0])
                if self.history_store.delete_record(idx):
                    self.refresh_data()
                    
    def clear_history(self):
        """清空所有歷史"""
        if messagebox.askyesno("確認清除", "確定要清空所有下載記錄嗎？"):
            self.history_store.clear_history()
            self.refresh_data()
