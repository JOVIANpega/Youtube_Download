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
        self.total_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                background-color: #f5f5f5;
                color: black;
                font-weight: bold;
                min-height: 25px;
            }
            QProgressBar::chunk {
                background-color: #5cb85c;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.total_progress)
        
        main_layout.addWidget(progress_group)
    
    def update_download_progress(self, filename, message, percent, speed, eta):
        """更新下載進度 - 增強版，確保項目可見且正確顯示"""
        try:
            # 輸出更詳細的診斷日誌
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if filename not in self.download_items:
                print(f"[{timestamp}] 警告: 找不到下載項目 [{filename}] 無法更新進度")
                return
            
            # 更新進度條
            if 'progress' in self.download_items[filename]:
                progress_bar = self.download_items[filename]['progress']
                
                # 確保進度條可見
                if not progress_bar.isVisible():
                    progress_bar.setVisible(True)
                    print(f"[{timestamp}] 設置進度條可見: [{filename}]")
                
                # 設定進度條格式和樣式 - 確保進度文字清晰可見
                progress_bar.setFormat(f"{percent}%")
                
                # 設置進度文字格式 - 更加明確的狀態顯示
                if "下載中" in message or "downloading" in message.lower():
                    # 顯示進度百分比和MB大小（如果可用）
                    progress_bar.setFormat(f"{percent}% 下載中")
                    
                    # 進度條使用藍色
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #0078d7;
                            border-radius: 5px;
                            text-align: center;
                            background-color: #f5f5f5;
                            color: black;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: #0078d7;
                            border-radius: 5px;
                        }
                    """)
                elif "失敗" in message or "錯誤" in message:
                    # 失敗時使用紅色
                    progress_bar.setFormat("失敗 - 點擊「重試」")
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #d9534f;
                            border-radius: 5px;
                            text-align: center;
                            background-color: #f5f5f5;
                            color: black;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: #d9534f;
                            border-radius: 5px;
                        }
                    """)
                elif "合併" in message or "處理" in message:
                    # 處理中使用藍色
                    progress_bar.setFormat("合併處理中...")
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #5bc0de;
                            border-radius: 5px;
                            text-align: center;
                            background-color: #f5f5f5;
                            color: black;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: #5bc0de;
                            border-radius: 5px;
                        }
                    """)
                elif "暫停" in message:
                    # 暫停時使用黃色
                    progress_bar.setFormat("已暫停 - 點擊「繼續」")
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #f0ad4e;
                            border-radius: 5px;
                            text-align: center;
                            background-color: #f5f5f5;
                            color: black;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: #f0ad4e;
                            border-radius: 5px;
                        }
                    """)
                elif "完成" in message:
                    # 完成時使用綠色
                    progress_bar.setFormat("100% - 下載完成!")
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #5cb85c;
                            border-radius: 5px;
                            text-align: center;
                            background-color: #f5f5f5;
                            color: black;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: #5cb85c;
                            border-radius: 5px;
                        }
                    """)
                else:
                    # 其他狀態使用紫色
                    progress_bar.setFormat(f"{percent}% - {message}")
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #605ca8;
                            border-radius: 5px;
                            text-align: center;
                            background-color: #f5f5f5;
                            color: black;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: #605ca8;
                            border-radius: 5px;
                        }
                    """)
                
                # 更新進度值
                if percent >= 0 and percent <= 100:
                    progress_bar.setValue(percent)
                else:
                    # 如果進度值超出範圍，設為0
                    progress_bar.setValue(0)
                    
                # 確保父元件可見
                parent_item = self.download_items[filename].get('frame')
                if parent_item and not parent_item.isVisible():
                    parent_item.setVisible(True)
                    print(f"[{timestamp}] 設置項目框架可見: [{filename}]")
            else:
                print(f"[{timestamp}] 警告: [{filename}] 沒有進度條元件")
            
            # 更新狀態標籤
            if 'status' in self.download_items[filename]:
                status_label = self.download_items[filename]['status']
                if "下載中" in message or "downloading" in message.lower():
                    status_label.setText(f"狀態: 下載中 {percent}%")
                elif "處理中" in message or "合併" in message:
                    status_label.setText(f"狀態: 處理中 {percent}%")
                else:
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
            
            # 每10%或者每分鐘記錄一次詳細日誌
            if percent % 10 == 0 and percent > 0:
                print(f"[{timestamp}] 進度更新 [{filename}]: {percent}%, 速度: {speed}, ETA: {eta}")
        except Exception as e:
            print(f"[{timestamp}] 更新進度條時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def update_total_progress(self):
        """更新總進度條和狀態資訊"""
        total_percent = 0
        active_items = 0
        completed_items = 0
        error_items = 0
        paused_items = 0
        total_items = len(self.download_items)
        
        # 計算各種狀態的項目數量和總進度
        for filename, item_data in self.download_items.items():
            if 'progress' in item_data:
                progress_bar = item_data['progress']
                current_progress = progress_bar.value()
                status_text = ""
                
                if 'status' in item_data:
                    status_text = item_data['status'].text().lower()
                
                # 檢查項目狀態
                if "失敗" in status_text or "錯誤" in status_text:
                    error_items += 1
                elif "暫停" in status_text:
                    paused_items += 1
                    # 暫停的項目也算入進度
                    if 0 < current_progress < 100:
                        total_percent += current_progress
                        active_items += 1
                elif current_progress == 100:
                    completed_items += 1
                elif 0 < current_progress < 100:
                    total_percent += current_progress
                    active_items += 1
        
        # 計算平均進度
        if active_items > 0:
            avg_percent = total_percent / active_items
        else:
            avg_percent = 0
        
        # 設置總進度條
        self.total_progress.setValue(int(avg_percent))
        
        # 設置總進度條顯示文字，包含各種狀態的項目數量
        if total_items > 0:
            status_text = f"總進度: {int(avg_percent)}% | "
            status_text += f"總計: {total_items}項 ("
            status_parts = []
            
            if completed_items > 0:
                status_parts.append(f"完成: {completed_items}")
            if active_items > 0:
                status_parts.append(f"下載中: {active_items}")
            if paused_items > 0:
                status_parts.append(f"暫停: {paused_items}")
            if error_items > 0:
                status_parts.append(f"失敗: {error_items}")
                
            status_text += ", ".join(status_parts) + ")"
            
            self.total_progress.setFormat(status_text)
            
            # 更新進度條顏色
            if error_items > 0:
                # 有錯誤時使用紅色
                self.total_progress.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #d9534f;
                        border-radius: 5px;
                        text-align: center;
                        background-color: #f5f5f5;
                        color: black;
                        font-weight: bold;
                        min-height: 25px;
                    }
                    QProgressBar::chunk {
                        background-color: #d9534f;
                        border-radius: 5px;
                    }
                """)
            elif paused_items > 0:
                # 有暫停項目時使用橙色
                self.total_progress.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #f0ad4e;
                        border-radius: 5px;
                        text-align: center;
                        background-color: #f5f5f5;
                        color: black;
                        font-weight: bold;
                        min-height: 25px;
                    }
                    QProgressBar::chunk {
                        background-color: #f0ad4e;
                        border-radius: 5px;
                    }
                """)
            elif active_items > 0:
                # 有活動項目時使用藍色
                self.total_progress.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #0078d7;
                        border-radius: 5px;
                        text-align: center;
                        background-color: #f5f5f5;
                        color: black;
                        font-weight: bold;
                        min-height: 25px;
                    }
                    QProgressBar::chunk {
                        background-color: #0078d7;
                        border-radius: 5px;
                    }
                """)
            elif completed_items == total_items:
                # 全部完成時使用綠色
                self.total_progress.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #5cb85c;
                        border-radius: 5px;
                        text-align: center;
                        background-color: #f5f5f5;
                        color: black;
                        font-weight: bold;
                        min-height: 25px;
                    }
                    QProgressBar::chunk {
                        background-color: #5cb85c;
                        border-radius: 5px;
                    }
                """)
            else:
                # 預設樣式
                self.total_progress.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #cccccc;
                        border-radius: 5px;
                        text-align: center;
                        background-color: #f5f5f5;
                        color: black;
                        font-weight: bold;
                        min-height: 25px;
                    }
                    QProgressBar::chunk {
                        background-color: #5cb85c;
                        border-radius: 5px;
                    }
                """)
        else:
            # 沒有下載項目
            self.total_progress.setValue(0)
            self.total_progress.setFormat("沒有進行中的下載")
            self.total_progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #f5f5f5;
                    color: #666666;
                    font-weight: bold;
                    min-height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #cccccc;
                    border-radius: 5px;
                                     }
                 """)
          # 已經在上面的條件分支中設置了格式，所以此行應該刪除
          # self.total_progress.setFormat(f"%p% ({completed_items}/{active_items + completed_items})")
    
    def clear_completed_downloads(self):
        """清除已完成的下載項目"""
        items_to_remove = []
        
        # 找出所有已完成的下載項目
        for filename, item_data in self.download_items.items():
            if 'progress' in item_data:
                progress_bar = item_data['progress']
                if progress_bar.value() == 100:
                    items_to_remove.append(filename)
        
        # 記錄已完成項目的URL，防止在下載頁面重新顯示
        if hasattr(self.parent, 'download_tab'):
            # 確保有存儲已完成URL的集合
            if not hasattr(self.parent.download_tab, '_completed_urls'):
                self.parent.download_tab._completed_urls = set()
                
            # 保存這些項目的URL
            for filename in items_to_remove:
                if 'url' in self.download_items[filename]:
                    url = self.download_items[filename]['url']
                    self.parent.download_tab._completed_urls.add(url)
        
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
        """添加一個下載項目到進度標籤頁"""
        # 如果項目已存在，不要重複添加
        if filename in self.download_items:
            return
            
        # 創建下載項目容器
        item_frame = QFrame()
        item_frame.setFrameStyle(QFrame.StyledPanel)
        item_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #f8f8f8;
            }
        """)
        
        # 建立網格佈局
        grid_layout = QGridLayout(item_frame)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(5)
        
        # 檔案名稱顯示
        filename_label = QLabel(f"<b>{filename}</b>")
        filename_label.setWordWrap(True)
        filename_label.setToolTip(filename)
        grid_layout.addWidget(filename_label, 0, 0, 1, 2)
        
        # URL 輸入框（顯示用）
        url_input = QLineEdit(url)
        url_input.setReadOnly(True)
        url_input.setStyleSheet("background-color: #f0f0f0; color: #666666;")
        grid_layout.addWidget(url_input, 1, 0, 1, 2)
        
        # 進度條
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setFormat("%p%")
        progress_bar.setTextVisible(True)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                background-color: #f5f5f5;
                color: black;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 5px;
            }
        """)
        grid_layout.addWidget(progress_bar, 2, 0, 1, 2)
        
        # 狀態資訊
        status_label = QLabel("狀態: 準備中...")
        grid_layout.addWidget(status_label, 3, 0)
        
        speed_label = QLabel("速度: --")
        grid_layout.addWidget(speed_label, 3, 1)
        
        eta_label = QLabel("剩餘時間: --")
        grid_layout.addWidget(eta_label, 4, 0)
        
        # 控制按鈕容器
        button_layout = QHBoxLayout()
        
        # 暫停/繼續按鈕
        pause_btn = QPushButton("暫停")
        pause_btn.setToolTip("暫停或繼續下載")
        pause_btn.setFixedWidth(80)
        pause_btn.clicked.connect(lambda: self.toggle_pause_item(filename))
        button_layout.addWidget(pause_btn)
        
        # 刪除按鈕
        delete_btn = QPushButton("刪除")
        delete_btn.setToolTip("取消並刪除下載")
        delete_btn.setFixedWidth(80)
        delete_btn.clicked.connect(lambda: self.delete_item(filename))
        button_layout.addWidget(delete_btn)
        
        # 外部下載按鈕 (開始時隱藏)
        external_btn = QPushButton("外部下載")
        external_btn.setToolTip("使用外部網站下載")
        external_btn.setFixedWidth(80)
        external_btn.setVisible(False)  # 初始隱藏
        external_btn.clicked.connect(lambda: self.open_external_download_site(filename, url))
        button_layout.addWidget(external_btn)
        
        grid_layout.addLayout(button_layout, 4, 1)
        
        # 將項目添加到佈局中
        # 在插入新項目之前先移除stretch
        if self.downloads_layout.count() > 0 and self.downloads_layout.itemAt(self.downloads_layout.count()-1).spacerItem():
            self.downloads_layout.removeItem(self.downloads_layout.itemAt(self.downloads_layout.count()-1))
            
        self.downloads_layout.addWidget(item_frame)
        self.downloads_layout.addStretch(1)  # 重新添加stretch以推高所有項目
        
        # 保存項目資訊和控制項的引用
        self.download_items[filename] = {
            'frame': item_frame,
            'url': url,
            'progress': progress_bar,
            'status': status_label,
            'speed': speed_label,
            'eta': eta_label,
            'pause_btn': pause_btn,
            'delete_btn': delete_btn,
            'external_btn': external_btn,
            'is_paused': False
        }
        
        # 保存線程引用
        if thread:
            self.download_threads[filename] = thread
            
        # 更新總進度
        self.update_total_progress()
        
        # 輸出日誌
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] 進度標籤頁添加下載項目: {filename}, URL: {url}")
        
        return item_frame
    
    def remove_item_from_ui(self, filename):
        """從UI中移除下載項目"""
        if filename in self.download_items:
            # 移除部件
            item_frame = self.download_items[filename]['frame']
            self.downloads_layout.removeWidget(item_frame)
            item_frame.setParent(None)
            item_frame.deleteLater()
            
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
                
    def update_task_status(self, filename, success, message, file_path):
        """更新任務狀態 - 增強版，提供更明確的完成狀態"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] 進度標籤頁更新任務狀態: {filename}, 成功: {success}")
        
        # 如果該任務不在進度標籤頁中，先添加它
        if filename not in self.download_items:
            url = ""
            # 嘗試從下載頁獲取URL
            if hasattr(self.parent, "download_tab") and hasattr(self.parent.download_tab, "download_items"):
                if filename in self.parent.download_tab.download_items:
                    url = self.parent.download_tab.download_items[filename].get("url", "")
            
            # 添加任務到進度頁
            if url:
                self.add_download_item(filename, url)
        
        # 如果任務已存在，更新其狀態
        if filename in self.download_items:
            item_data = self.download_items[filename]
            progress_bar = item_data.get('progress')
            status_label = item_data.get('status')
            
            if progress_bar and status_label:
                if success:
                    # 下載成功
                    progress_bar.setValue(100)
                    progress_bar.setFormat("100% - 完成!")
                    
                    # 使用明顯的綠色進度條顯示完成
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #5cb85c;
                            border-radius: 5px;
                            text-align: center;
                            background-color: #f5f5f5;
                            color: black;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: #5cb85c;
                            border-radius: 5px;
                        }
                    """)
                    
                    # 更新狀態標籤
                    status_label.setText("已完成下載 ✓")
                    status_label.setStyleSheet("color: green; font-weight: bold;")
                    
                    # 更新控制按鈕
                    if 'pause_btn' in item_data:
                        item_data['pause_btn'].setText("完成")
                        item_data['pause_btn'].setEnabled(False)
                        item_data['pause_btn'].setStyleSheet("""
                            QPushButton {
                                background-color: #5cb85c;
                                color: white;
                                border-radius: 3px;
                                padding: 3px 8px;
                            }
                        """)
                    
                    # 顯示檔案資訊
                    if file_path and os.path.exists(file_path):
                        try:
                            file_size = os.path.getsize(file_path)
                            size_str = self.format_file_size(file_size)
                            
                            # 更新ETA標籤顯示檔案大小
                            if 'eta_label' in item_data:
                                item_data['eta_label'].setText(f"檔案大小: {size_str}")
                            
                            # 更新速度標籤顯示完成時間
                            if 'speed_label' in item_data:
                                item_data['speed_label'].setText(f"完成時間: {timestamp.split()[1]}")
                                
                            # 顯示彈出通知
                            self.show_complete_notification(filename, file_path)
                        except Exception as e:
                            print(f"[{timestamp}] 獲取檔案大小失敗: {str(e)}")
                else:
                    # 下載失敗
                    progress_bar.setValue(0)
                    progress_bar.setFormat("0% - 失敗")
                    
                    # 使用紅色進度條顯示失敗
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #d9534f;
                            border-radius: 5px;
                            text-align: center;
                            background-color: #f5f5f5;
                            color: black;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: #d9534f;
                            border-radius: 5px;
                        }
                    """)
                    
                    # 更新狀態標籤
                    status_label.setText(f"下載失敗 ❌ 點擊「重試」按鈕")
                    status_label.setStyleSheet("color: red; font-weight: bold;")
                    
                    # 更新控制按鈕
                    if 'pause_btn' in item_data:
                        item_data['pause_btn'].setText("失敗")
                        item_data['pause_btn'].setEnabled(False)
                        item_data['pause_btn'].setStyleSheet("""
                            QPushButton {
                                background-color: #d9534f;
                                color: white;
                                border-radius: 3px;
                                padding: 3px 8px;
                            }
                        """)
                    
                    # 新增重試按鈕
                    if 'retry_btn' not in item_data:
                        retry_btn = QPushButton("重試")
                        retry_btn.setToolTip("重新嘗試下載")
                        retry_btn.setFixedWidth(80)
                        retry_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #5cb85c;
                                color: white;
                                border-radius: 3px;
                                padding: 3px 8px;
                            }
                            QPushButton:hover {
                                background-color: #449d44;
                            }
                        """)
                        retry_btn.clicked.connect(lambda: self.retry_download(filename))
                        item_data['retry_btn'] = retry_btn
                        
                        # 嘗試將按鈕添加到佈局
                        parent_frame = item_data.get('frame')
                        if parent_frame and hasattr(parent_frame, 'layout'):
                            layout = parent_frame.layout()
                            if layout:
                                # 尋找按鈕區域並添加重試按鈕
                                for i in range(layout.count()):
                                    item = layout.itemAt(i)
                                    if item and isinstance(item, QHBoxLayout):
                                        item.addWidget(retry_btn)
                                        break
                    else:
                        # 顯示已有的重試按鈕
                        item_data['retry_btn'].setVisible(True)
                    
                    # 顯示外部下載按鈕
                    if 'external_btn' in item_data:
                        item_data['external_btn'].setVisible(True)
                        
                    # 更新錯誤信息
                    if 'eta_label' in item_data:
                        item_data['eta_label'].setText("狀態: 下載失敗")
                    
                    if 'speed_label' in item_data:
                        item_data['speed_label'].setText(f"錯誤信息: {message[:30]}...")
                        
        # 更新總進度
        self.update_total_progress()
        
    def format_file_size(self, size_bytes):
        """格式化檔案大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            
    def show_complete_notification(self, filename, file_path):
        """顯示下載完成通知"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            from PySide6.QtWidgets import QMessageBox
            
            # 在當前標籤頁顯示通知，避免打斷用戶操作
            file_name = os.path.basename(file_path)
            msg = QMessageBox(self)
            msg.setWindowTitle("下載完成")
            msg.setText(f"檔案 {file_name} 已下載完成!")
            msg.setIcon(QMessageBox.Information)
            
            # 添加開啟檔案按鈕
            open_file_btn = msg.addButton("開啟檔案", QMessageBox.ActionRole)
            open_folder_btn = msg.addButton("開啟資料夾", QMessageBox.ActionRole)
            close_btn = msg.addButton("關閉", QMessageBox.RejectRole)
            
            # 非阻塞顯示（不會阻擋UI執行）
            msg.show()
            
            # 連接按鈕信號
            open_file_btn.clicked.connect(lambda: self.open_file(file_path))
            open_folder_btn.clicked.connect(lambda: self.open_folder(os.path.dirname(file_path)))
            
            # 幾秒後自動關閉
            from PySide6.QtCore import QTimer
            QTimer.singleShot(10000, msg.close)
            
            print(f"[{timestamp}] 顯示下載完成通知: {filename}")
        except Exception as e:
            print(f"[{timestamp}] 顯示下載完成通知失敗: {str(e)}")
            
    def open_file(self, file_path):
        """開啟檔案"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            import os, subprocess
            
            if os.path.exists(file_path):
                print(f"[{timestamp}] 開啟檔案: {file_path}")
                
                if sys.platform == "win32":
                    os.startfile(file_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", file_path])
        except Exception as e:
            print(f"[{timestamp}] 開啟檔案失敗: {str(e)}")
            
    def open_folder(self, folder_path):
        """開啟資料夾"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            import os, subprocess
            
            if os.path.exists(folder_path):
                print(f"[{timestamp}] 開啟資料夾: {folder_path}")
                
                if sys.platform == "win32":
                    os.startfile(folder_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", folder_path])
                else:  # Linux
                    subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            print(f"[{timestamp}] 開啟資料夾失敗: {str(e)}")
            
    def retry_download(self, filename):
        """重試下載"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            print(f"[{timestamp}] 重試下載: {filename}")
            
            # 檢查是否有原始URL
            if filename in self.download_items and 'url' in self.download_items[filename]:
                url = self.download_items[filename]['url']
                
                # 移除舊的下載項目
                self.remove_item_from_ui(filename)
                
                # 請求主程式重新下載
                if hasattr(self.parent, "download_tab"):
                    self.parent.download_tab.start_download_for_item(filename, url)
                    print(f"[{timestamp}] 已請求重新下載: {filename}")
            else:
                print(f"[{timestamp}] 無法重試，找不到原始URL: {filename}")
        except Exception as e:
            print(f"[{timestamp}] 重試下載失敗: {str(e)}") 

    def clear_all(self):
        """清空所有下載項目"""
        try:
            # 移除所有下載項目
            for filename in list(self.download_items.keys()):
                self.remove_item_from_ui(filename)
            
            # 清空集合
            self.download_items.clear()
            self.download_threads.clear()
            
            # 更新總進度
            self.update_total_progress()
            
            # 日誌記錄
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] 已清空所有下載項目")
        except Exception as e:
            # 日誌記錄
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] 清空所有下載項目失敗：{str(e)}")
            
    def open_external_download_site(self, filename, url):
        """開啟外部下載網站"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if not url:
                print(f"[{timestamp}] 錯誤: 無法開啟外部下載網站，URL為空")
                return
                
            print(f"[{timestamp}] 開啟外部下載網站: {url}")
            
            # 識別平台
            platform = "unknown"
            if "youtube" in url.lower() or "youtu.be" in url.lower():
                platform = "youtube"
            elif "tiktok" in url.lower() or "douyin" in url.lower():
                platform = "tiktok"
            elif "facebook" in url.lower() or "fb.com" in url.lower():
                platform = "facebook"
            elif "instagram" in url.lower():
                platform = "instagram"
            elif "twitter" in url.lower() or "x.com" in url.lower():
                platform = "twitter"
            
            # 載入外部網站設定
            external_urls = self.load_external_url_settings()
            
            if platform in external_urls and external_urls[platform]:
                # 替換URL
                external_url = external_urls[platform].replace("{url}", url)
                print(f"[{timestamp}] 使用外部網站: {external_url}")
                
                # 嘗試開啟瀏覽器
                import webbrowser
                webbrowser.open(external_url)
            else:
                # 直接開啟原始URL
                print(f"[{timestamp}] 未找到對應的外部網站設定，直接開啟原始URL")
                import webbrowser
                webbrowser.open(url)
        except Exception as e:
            print(f"[{timestamp}] 開啟外部下載網站失敗: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def load_external_url_settings(self):
        """載入外部網站設定"""
        try:
            # 預設外部網站
            default_urls = {
                "youtube": "https://publer.com/tools/youtube-shorts-downloader?url={url}",
                "instagram": "https://igram.io/?url={url}",
                "twitter": "https://twittervideodownloader.com/?url={url}",
                "tiktok": "https://tiktokio.com/zh_tw/?url={url}",
                "facebook": "https://fdown.net/?url={url}",
                "threads": "https://threadsdownloader.com/?url={url}"
            }
            
            # 嘗試從設定檔載入
            import os
            import json
            
            if hasattr(self, "parent") and hasattr(self.parent, "download_path"):
                settings_path = os.path.join(os.path.dirname(self.parent.download_path), "setup.json")
            else:
                settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "setup.json")
                
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    if "external_urls" in settings:
                        # 合併預設設定和用戶設定
                        urls = default_urls.copy()
                        urls.update(settings["external_urls"])
                        return urls
            
            # 如果沒有設定檔或沒有外部URL設定，返回預設值
            return default_urls
        except Exception as e:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] 載入外部網站設定失敗: {str(e)}")
            return {} 