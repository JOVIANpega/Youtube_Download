#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多平台影片下載器 - 下載進度標籤頁
"""

import os
import sys
import time
import json # Added for saving settings
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QScrollArea, QFrame, QMessageBox, QLineEdit,
    QGroupBox, QGridLayout
)

class ProgressTab(QWidget):
    """下載進度標籤頁"""
    
    def __init__(self, parent=None, download_path=None):
        super().__init__(parent)
        self.parent = parent
        self.download_path = download_path or os.path.expanduser("~/Downloads")
        self.download_items = {}  # 儲存下載項目的相關資訊
        self.download_threads = {}  # 儲存下載線程
        self.error_dialogs = {}  # 儲存錯誤對話框
        self.format_dialogs = {}  # 儲存格式選項對話框
        self.download_completed_dialogs = {}  # 儲存下載完成對話框
        self.init_ui()
    
    def set_download_path(self, new_path):
        """設置下載路徑"""
        self.download_path = new_path
    
    def save_settings(self):
        """保存進度標籤頁設定"""
        try:
            # 使用通用的設定檔路徑
            settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'setup.json')
            
            # 讀取現有設定（如果存在）
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    try:
                        settings = json.load(f)
                    except:
                        settings = {}
            
            # 確保progress_tab區段存在
            if "progress_tab" not in settings:
                settings["progress_tab"] = {}
                
            # 保存正在進行的下載數量
            active_downloads = 0
            completed_downloads = 0
            for filename, item in self.download_items.items():
                if 'progress' in item and 0 < item['progress'].value() < 100:
                    active_downloads += 1
                elif 'progress' in item and item['progress'].value() == 100:
                    completed_downloads += 1
                    
            settings["progress_tab"]["active_downloads"] = active_downloads
            settings["progress_tab"]["completed_downloads"] = completed_downloads
            settings["progress_tab"]["total_downloads"] = len(self.download_items)
            
            # 保存設定
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            # 輸出日誌
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] 已保存進度標籤頁設定：活動下載數量 {active_downloads}，完成下載數量 {completed_downloads}")
            
        except Exception as e:
            # 輸出日誌
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] 保存進度標籤頁設定失敗：{str(e)}")
    
    def init_ui(self):
        """初始化用戶界面"""
        main_layout = QVBoxLayout(self)
        
        # 下載進度標題
        header_layout = QHBoxLayout()
        title_label = QLabel("下載進度")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # 新增清除已完成按鈕
        clear_btn = QPushButton("清除已完成")
        clear_btn.setToolTip("從列表中移除已完成的下載項目")
        clear_btn.clicked.connect(self.clear_completed_downloads)
        header_layout.addWidget(clear_btn)
        
        # 新增全部暫停按鈕
        pause_all_btn = QPushButton("全部暫停")
        pause_all_btn.setToolTip("暫停所有正在進行的下載")
        pause_all_btn.clicked.connect(self.pause_all_downloads)
        header_layout.addWidget(pause_all_btn)
        
        # 新增全部繼續按鈕
        resume_all_btn = QPushButton("全部繼續")
        resume_all_btn.setToolTip("繼續所有暫停的下載")
        resume_all_btn.clicked.connect(self.resume_all_downloads)
        header_layout.addWidget(resume_all_btn)
        
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)
        
        # 建立下載項目的捲動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll_area)
        
        # 建立容器小部件來放置下載項目
        self.downloads_container = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_container)
        self.downloads_layout.setContentsMargins(0, 0, 0, 0)
        self.downloads_layout.setSpacing(10)
        self.downloads_layout.addStretch(1)
        
        scroll_area.setWidget(self.downloads_container)
        
        # 添加總進度顯示
        progress_group = QGroupBox("總進度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.total_progress = QProgressBar()
        self.total_progress.setRange(0, 100)
        self.total_progress.setValue(0)
        self.total_progress.setFormat("%p% (0/0)")
        progress_layout.addWidget(self.total_progress)
        
        main_layout.addWidget(progress_group)
    
    def update_download_progress(self, filename, message, percent, speed, eta):
        """更新下載進度"""
        if filename in self.download_items:
            # 更新進度條
            if 'progress' in self.download_items[filename]:
                progress_bar = self.download_items[filename]['progress']
                progress_bar.setValue(percent)
            
            # 更新狀態標籤
            if 'status' in self.download_items[filename]:
                status_label = self.download_items[filename]['status']
                status_label.setText(f"狀態: {message}")
            
            # 更新速度標籤
            if 'speed' in self.download_items[filename]:
                speed_label = self.download_items[filename]['speed']
                speed_label.setText(f"速度: {speed}")
            
            # 更新ETA標籤
            if 'eta' in self.download_items[filename]:
                eta_label = self.download_items[filename]['eta']
                eta_label.setText(f"剩餘時間: {eta}")
            
            # 更新總進度
            self.update_total_progress()
    
    def update_total_progress(self):
        """更新總進度條"""
        total_percent = 0
        active_items = 0
        completed_items = 0
        
        # 計算平均進度
        for filename, item_data in self.download_items.items():
            if 'progress' in item_data:
                progress_bar = item_data['progress']
                current_progress = progress_bar.value()
                
                # 檢查是否是活動中的下載項目
                if 0 < current_progress < 100:
                    total_percent += current_progress
                    active_items += 1
                elif current_progress == 100:
                    completed_items += 1
        
        # 計算平均進度
        if active_items > 0:
            avg_percent = total_percent / active_items
        else:
            avg_percent = 0
        
        # 設置總進度條
        self.total_progress.setValue(int(avg_percent))
        self.total_progress.setFormat(f"%p% ({completed_items}/{active_items + completed_items})")
    
    def clear_completed_downloads(self):
        """清除已完成的下載項目"""
        items_to_remove = []
        
        # 找出所有已完成的下載項目
        for filename, item_data in self.download_items.items():
            if 'progress' in item_data:
                progress_bar = item_data['progress']
                if progress_bar.value() == 100:
                    items_to_remove.append(filename)
        
        # 移除已完成的項目
        for filename in items_to_remove:
            self.remove_item_from_ui(filename)
        
        # 更新總進度
        self.update_total_progress()
        
        # 顯示通知
        if len(items_to_remove) > 0:
            QMessageBox.information(self, "清除完成", f"已清除 {len(items_to_remove)} 個已完成的下載項目")
    
    def pause_all_downloads(self):
        """暫停所有下載"""
        paused_count = 0
        
        for filename, item_data in self.download_items.items():
            if 'thread' in item_data and item_data['thread'] is not None and not item_data['thread'].is_paused:
                # 暫停下載線程
                item_data['thread'].pause()
                
                # 更新暫停/繼續按鈕
                if 'pause_btn' in item_data:
                    item_data['pause_btn'].setText("繼續")
                    item_data['pause_btn'].setStyleSheet("""
                        QPushButton {
                            background-color: #5cb85c;
                            color: white;
                            border-radius: 3px;
                            padding: 3px 8px;
                        }
                        QPushButton:hover {
                            background-color: #4cae4c;
                        }
                    """)
                
                paused_count += 1
        
        if paused_count > 0:
            QMessageBox.information(self, "暫停下載", f"已暫停 {paused_count} 個下載任務")
    
    def resume_all_downloads(self):
        """繼續所有下載"""
        resumed_count = 0
        
        for filename, item_data in self.download_items.items():
            if 'thread' in item_data and item_data['thread'] is not None and item_data['thread'].is_paused:
                # 繼續下載線程
                item_data['thread'].resume()
                
                # 更新暫停/繼續按鈕
                if 'pause_btn' in item_data:
                    item_data['pause_btn'].setText("暫停")
                    item_data['pause_btn'].setStyleSheet("""
                        QPushButton {
                            background-color: #f0ad4e;
                            color: white;
                            border-radius: 3px;
                            padding: 3px 8px;
                        }
                        QPushButton:hover {
                            background-color: #ec971f;
                        }
                    """)
                
                resumed_count += 1
        
        if resumed_count > 0:
            QMessageBox.information(self, "繼續下載", f"已繼續 {resumed_count} 個下載任務")
    
    def add_download_item(self, filename, url, thread=None):
        """添加新的下載項目到進度標籤頁"""
        # 如果已存在相同文件名的項目，先移除
        if filename in self.download_items:
            self.remove_item_from_ui(filename)
        
        # 創建下載項目容器
        item_widget = QFrame()
        item_widget.setFrameShape(QFrame.StyledPanel)
        item_widget.setFrameShadow(QFrame.Raised)
        item_widget.setStyleSheet("QFrame { background-color: #f9f9f9; border-radius: 5px; }")
        
        item_layout = QVBoxLayout(item_widget)
        
        # 文件名和URL
        header_layout = QHBoxLayout()
        
        # 文件名標籤
        filename_label = QLabel(filename)
        filename_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(filename_label, 1)
        
        # 創建按鈕
        button_layout = QHBoxLayout()
        
        # 暫停/繼續按鈕
        pause_btn = QPushButton("暫停")
        pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0ad4e;
                color: white;
                border-radius: 3px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
        """)
        button_layout.addWidget(pause_btn)
        
        # 刪除按鈕
        delete_btn = QPushButton("取消")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 3px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        button_layout.addWidget(delete_btn)
        
        header_layout.addLayout(button_layout)
        item_layout.addLayout(header_layout)
        
        # URL輸入框 (隱藏但保存URL)
        url_input = QLineEdit(url)
        url_input.setVisible(False)
        url_input.setObjectName(f"url_input_{filename}")
        item_layout.addWidget(url_input)
        
        # 進度信息
        info_layout = QGridLayout()
        
        # 狀態標籤
        status_label = QLabel("狀態: 準備下載...")
        info_layout.addWidget(status_label, 0, 0)
        
        # 速度標籤
        speed_label = QLabel("速度: --")
        info_layout.addWidget(speed_label, 0, 1)
        
        # ETA標籤
        eta_label = QLabel("剩餘時間: --")
        info_layout.addWidget(eta_label, 1, 0)
        
        item_layout.addLayout(info_layout)
        
        # 進度條
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        progress_bar.setFormat("%p%")
        item_layout.addWidget(progress_bar)
        
        # 保存到下載項目字典
        self.download_items[filename] = {
            'widget': item_widget,
            'progress': progress_bar,
            'status': status_label,
            'speed': speed_label,
            'eta': eta_label,
            'url': url,
            'pause_btn': pause_btn,
            'delete_btn': delete_btn,
            'thread': thread  # 下載線程
        }
        
        # 連接按鈕信號
        pause_btn.clicked.connect(lambda: self.toggle_pause_item(filename))
        delete_btn.clicked.connect(lambda: self.delete_item(filename))
        
        # 插入到下載佈局中 (在 stretch 之前)
        self.downloads_layout.insertWidget(self.downloads_layout.count() - 1, item_widget)
        
        return self.download_items[filename]
    
    def remove_item_from_ui(self, filename):
        """從UI中移除下載項目"""
        if filename in self.download_items:
            # 移除部件
            item_widget = self.download_items[filename]['widget']
            self.downloads_layout.removeWidget(item_widget)
            item_widget.setParent(None)
            item_widget.deleteLater()
            
            # 清理線程
            if 'thread' in self.download_items[filename] and self.download_items[filename]['thread'] is not None:
                self.download_items[filename]['thread'].cancel()
            
            # 從字典中移除
            del self.download_items[filename]
            
            # 更新總進度
            self.update_total_progress()
    
    def toggle_pause_item(self, filename):
        """切換下載項目的暫停/繼續狀態"""
        if filename in self.download_items and 'thread' in self.download_items[filename]:
            thread = self.download_items[filename]['thread']
            if thread is not None:
                if thread.is_paused:
                    # 繼續下載
                    thread.resume()
                    self.download_items[filename]['pause_btn'].setText("暫停")
                    self.download_items[filename]['pause_btn'].setStyleSheet("""
                        QPushButton {
                            background-color: #f0ad4e;
                            color: white;
                            border-radius: 3px;
                            padding: 3px 8px;
                        }
                        QPushButton:hover {
                            background-color: #ec971f;
                        }
                    """)
                    self.download_items[filename]['status'].setText("狀態: 正在下載...")
                else:
                    # 暫停下載
                    thread.pause()
                    self.download_items[filename]['pause_btn'].setText("繼續")
                    self.download_items[filename]['pause_btn'].setStyleSheet("""
                        QPushButton {
                            background-color: #5cb85c;
                            color: white;
                            border-radius: 3px;
                            padding: 3px 8px;
                        }
                        QPushButton:hover {
                            background-color: #4cae4c;
                        }
                    """)
                    self.download_items[filename]['status'].setText("狀態: 已暫停")
    
    def delete_item(self, filename):
        """刪除下載項目"""
        if filename in self.download_items:
            # 詢問用戶是否確認刪除
            reply = QMessageBox.question(
                self, 
                "確認取消", 
                f"確定要取消下載 '{filename}' 嗎？",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.remove_item_from_ui(filename)
                
    def download_finished(self, filename, success, message, file_path):
        """處理下載完成事件"""
        if filename in self.download_items:
            if success:
                # 下載成功
                self.download_items[filename]['status'].setText(f"狀態: 下載完成 ✅")
                self.download_items[filename]['progress'].setValue(100)
                self.download_items[filename]['speed'].setText("速度: --")
                self.download_items[filename]['eta'].setText("剩餘時間: 完成")
                
                # 更新按鈕狀態
                if 'pause_btn' in self.download_items[filename]:
                    self.download_items[filename]['pause_btn'].setText("完成")
                    self.download_items[filename]['pause_btn'].setEnabled(False)
                    self.download_items[filename]['pause_btn'].setStyleSheet("""
                        QPushButton {
                            background-color: #5cb85c;
                            color: white;
                            border-radius: 3px;
                            padding: 3px 8px;
                        }
                    """)
            else:
                # 下載失敗
                self.download_items[filename]['status'].setText(f"狀態: 下載失敗 ❌")
                self.download_items[filename]['progress'].setValue(0)
                self.download_items[filename]['progress'].setStyleSheet("""
                    QProgressBar::chunk {
                        background-color: #d9534f;
                    }
                """)
                
                # 更新按鈕狀態
                if 'pause_btn' in self.download_items[filename]:
                    self.download_items[filename]['pause_btn'].setText("失敗")
                    self.download_items[filename]['pause_btn'].setEnabled(False)
                    self.download_items[filename]['pause_btn'].setStyleSheet("""
                        QPushButton {
                            background-color: #d9534f;
                            color: white;
                            border-radius: 3px;
                            padding: 3px 8px;
                        }
                    """)
            
            # 更新總進度
            self.update_total_progress() 