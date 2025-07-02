#!/usr/bin/env python3
"""
YouTube 下載器 - 分頁式 GUI 演示
YouTube Downloader - Tabbed GUI Demo
YouTubeダウンローダー - タブ付きGUIデモ
유튜브 다운로더 - 탭 GUI 데모
"""

import sys
import os
import time
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget,
                               QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTextEdit, QLineEdit, QProgressBar, QCheckBox,
                               QComboBox, QFileDialog, QGroupBox, QSplitter,
                               QListWidget, QGridLayout, QRadioButton,
                               QButtonGroup, QToolBar, QStatusBar, QScrollArea, QFrame, QMessageBox, QSpinBox)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QTimer
from PySide6.QtGui import QIcon, QAction, QFont

# 設置日誌函數
def log(message):
    """輸出日誌"""
    print(f"[LOG] {message}")
    sys.stdout.flush()  # 強制輸出緩衝區

class DownloadTab(QWidget):
    """下載任務標籤頁"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.demo_downloads()  # 添加模擬下載項目
    
    def init_ui(self):
        """初始化用戶界面"""
        # 創建主佈局
        layout = QVBoxLayout(self)
        
        # URL輸入區域
        url_group = QGroupBox("貼入一個或多個YouTube網址")
        url_group.setObjectName("url_input_group")  # 添加對象名稱
        url_layout = QVBoxLayout(url_group)
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("在此處貼上一個或多個YouTube網址，每行一個...")
        self.url_input.setMinimumHeight(100)
        url_layout.addWidget(self.url_input)
        layout.addWidget(url_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        self.download_btn = QPushButton("開始下載")
        self.pause_btn = QPushButton("暫停所有")
        self.delete_btn = QPushButton("刪除選取")
        self.auto_merge_cb = QCheckBox("自動合併")
        self.auto_merge_cb.setChecked(True)
        
        buttons_layout.addWidget(self.download_btn)
        buttons_layout.addWidget(self.pause_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.auto_merge_cb)
        layout.addLayout(buttons_layout)
        
        # V1.55特色: 下載選項區域
        options_group = QGroupBox("下載選項")
        options_group.setObjectName("download_options_group")
        options_layout = QHBoxLayout(options_group)
        
        # 格式選項
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["最高品質", "僅影片", "僅音訊 (MP3)", "僅音訊 (WAV)"])
        format_layout.addWidget(self.format_combo)
        options_layout.addLayout(format_layout)
        
        # 解析度選項
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("解析度:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["自動選擇最佳", "4K", "1080P (Full HD)", "720P (HD)", "480P", "360P"])
        resolution_layout.addWidget(self.resolution_combo)
        options_layout.addLayout(resolution_layout)
        
        # 檔案名稱前綴
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("前綴:"))
        self.prefix_input = QLineEdit("TEST-")
        prefix_layout.addWidget(self.prefix_input)
        options_layout.addLayout(prefix_layout)
        
        layout.addWidget(options_group)
        
        # 下載佇列區域
        queue_group = QGroupBox("下載佇列")
        queue_group.setObjectName("download_queue_group")  # 添加對象名稱
        queue_layout = QVBoxLayout(queue_group)
        
        # 模擬下載項目
        self.create_download_item(queue_layout, "樂團現場演唱會.mp4", 65, "01:20", "5.2MB/s", "進行中")
        self.create_download_item(queue_layout, "實用教學影片.mp4", 32, "--:--", "--", "已暫停")
        self.create_download_item(queue_layout, "音樂MV合輯.mp4", 0, "--:--", "--", "等待中")
        self.create_download_item(queue_layout, "私人影片.mp4", 0, "--:--", "--", "錯誤: 年齡限制")
        
        queue_layout.addStretch(1)
        layout.addWidget(queue_group)
        
        # 總進度資訊
        total_layout = QHBoxLayout()
        total_progress_label = QLabel("總進度：0/0 完成 | 總剩餘時間：約 0 分鐘")
        total_progress_label.setObjectName("total_progress_label")  # 添加ID以便於查找
        total_layout.addWidget(total_progress_label)
        total_layout.addStretch(1)
        layout.addLayout(total_layout)
        
        # 連接信號
        self.download_btn.clicked.connect(self.start_download)
        self.pause_btn.clicked.connect(self.pause_all)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        self.resolution_combo.currentIndexChanged.connect(self.update_resolution_availability)
    
    def demo_downloads(self):
        """初始化示範用的下載項目"""
        # 下載佇列區域
        queue_group = self.findChild(QGroupBox, "download_queue_group")
        if queue_group:
            queue_layout = queue_group.layout()
            
            # 清空現有下載項目
            while queue_layout.count():
                item = queue_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 創建示範下載項目
            self.create_download_item(queue_layout, "樂團現場演唱會.mp4", 65, "01:20", "5.2MB/s", "進行中")
            self.create_download_item(queue_layout, "實用教學影片.mp4", 32, "--:--", "--", "已暫停")
            self.create_download_item(queue_layout, "音樂MV合輯.mp4", 0, "--:--", "--", "等待中")
            self.create_download_item(queue_layout, "私人影片.mp4", 0, "--:--", "--", "錯誤: 年齡限制")
            
            # 更新總進度標籤
            total_label = self.findChild(QLabel, "total_progress_label")
            if total_label:
                total_label.setText("總進度：0/4 完成 | 總剩餘時間：約 15 分鐘")
            
            # 添加間距
            queue_layout.addStretch(1)
    
    def create_download_item(self, parent_layout, filename, progress, eta, speed, status):
        """創建下載項目"""
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        # 狀態圖標
        status_icon = "▶" if status == "進行中" else "⏸" if status == "已暫停" else "⏳" if status == "等待中" else "❌"
        icon_label = QLabel(status_icon)
        icon_label.setMinimumWidth(15)
        item_layout.addWidget(icon_label)
        
        # 檔案名稱
        file_label = QLabel(filename)
        file_label.setMinimumWidth(200)
        item_layout.addWidget(file_label)
        
        # 進度條
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(progress)
        progress_bar.setMinimumWidth(200)
        progress_bar.setObjectName(f"progress_bar_{filename}")  # 添加唯一對象名稱
        item_layout.addWidget(progress_bar, 1)  # 進度條佔用更多空間
        
        # 進度資訊佈局
        progress_info = QVBoxLayout()
        
        # 狀態
        status_label = QLabel(status)
        status_label.setObjectName(f"status_label_{filename}")  # 添加唯一對象名稱
        progress_info.addWidget(status_label)
        
        # 速度
        speed_label = QLabel(speed)
        speed_label.setObjectName(f"speed_label_{filename}")  # 添加唯一對象名稱
        progress_info.addWidget(speed_label)
        
        item_layout.addLayout(progress_info)
        
        # 操作按鈕區域
        buttons_layout = QHBoxLayout()
        
        # 暫停/繼續按鈕
        pause_btn = QPushButton("暫停" if status != "已暫停" else "繼續")
        pause_btn.setObjectName(f"pause_btn_{filename}")  # 添加唯一對象名稱
        buttons_layout.addWidget(pause_btn)
        
        # 刪除按鈕
        delete_btn = QPushButton("刪除")
        delete_btn.setObjectName(f"delete_btn_{filename}")  # 添加唯一對象名稱
        buttons_layout.addWidget(delete_btn)
        
        item_layout.addLayout(buttons_layout)
        
        # 添加到父布局
        parent_layout.addWidget(item_widget)
        
        # 連接按鈕信號
        pause_btn.clicked.connect(lambda: self.toggle_pause_item(filename))
        delete_btn.clicked.connect(lambda: self.delete_item(filename))
        
        return item_widget

    def toggle_pause_item(self, filename):
        """暫停/繼續特定下載項目"""
        pause_btn = self.findChild(QPushButton, f"pause_btn_{filename}")
        status_label = self.findChild(QLabel, f"status_label_{filename}")
        icon_label = None
        
        # 找到對應的圖標標籤
        item_widget = pause_btn.parent()
        while item_widget and not isinstance(item_widget, QWidget):
            item_widget = item_widget.parent()
        
        if item_widget:
            layout = item_widget.layout()
            if layout and layout.count() > 0:
                icon_label = layout.itemAt(0).widget()
        
        if pause_btn.text() == "暫停":
            pause_btn.setText("繼續")
            if status_label:
                status_label.setText("已暫停")
            if icon_label:
                icon_label.setText("⏸")
        else:
            pause_btn.setText("暫停")
            if status_label:
                status_label.setText("進行中")
            if icon_label:
                icon_label.setText("▶")
            
    def delete_item(self, filename):
        """刪除特定下載項目"""
        progress_bar = self.findChild(QProgressBar, f"progress_bar_{filename}")
        if progress_bar:
            item_widget = progress_bar.parent()
            while item_widget and not isinstance(item_widget, QWidget):
                item_widget = item_widget.parent()
            
            if item_widget:
                item_widget.deleteLater()
                print(f"已刪除下載項目: {filename}")

    def start_download(self):
        """開始下載"""
        # 獲取下載URLs
        urls_text = self.url_input.toPlainText().strip()
        if not urls_text:
            log("請輸入YouTube網址")
            return
        
        # 獲取用戶選項
        format_option = self.format_combo.currentText()
        resolution = self.resolution_combo.currentText()
        prefix = self.prefix_input.text()
        auto_merge = self.auto_merge_cb.isChecked()
        
        # 解析多個URLs（每行一個）
        urls = urls_text.split('\n')
        valid_urls = [url.strip() for url in urls if url.strip()]
        
        if not valid_urls:
            log("沒有有效的網址")
            return
        
        # 輸出下載資訊
        log(f"套用設定")
        log(f"開始下載 {len(valid_urls)} 個影片...")
        log(f"格式選項: {format_option}")
        log(f"解析度: {resolution}")
        log(f"檔案前綴: {prefix}")
        log(f"自動合併: {'是' if auto_merge else '否'}")
        
        # 獲取第一個下載任務的控件
        first_file = "樂團現場演唱會.mp4"  # 第一個下載項目的檔名
        progress_bar = self.findChild(QProgressBar, f"progress_bar_{first_file}")
        status_label = self.findChild(QLabel, f"status_label_{first_file}")
        speed_label = self.findChild(QLabel, f"speed_label_{first_file}")
        
        log(f"找到進度條控件: {progress_bar is not None}")
        log(f"找到狀態標籤控件: {status_label is not None}")
        log(f"找到速度標籤控件: {speed_label is not None}")
        
        if not progress_bar or not status_label or not speed_label:
            # 如果找不到控件，刷新下載列表後重試
            log("控件未找到，重新初始化下載列表")
            self.demo_downloads()
            progress_bar = self.findChild(QProgressBar, f"progress_bar_{first_file}")
            status_label = self.findChild(QLabel, f"status_label_{first_file}")
            speed_label = self.findChild(QLabel, f"speed_label_{first_file}")
            
            log(f"重新初始化後找到進度條控件: {progress_bar is not None}")
            log(f"重新初始化後找到狀態標籤控件: {status_label is not None}")
            log(f"重新初始化後找到速度標籤控件: {speed_label is not None}")
        
        if progress_bar and status_label and speed_label:
            # 重置進度條
            progress_bar.setValue(0)
            status_label.setText("進行中")
            speed_label.setText("計算中...")
            log("已重置進度條和狀態")
            
            # 創建計時器來模擬進度更新
            self.progress_timer = QTimer()
            self.progress_value = 0
            
            def update_progress():
                self.progress_value += 1
                if self.progress_value <= 100:
                    progress_bar.setValue(self.progress_value)
                    
                    # 更新速度和ETA
                    speed = f"{5.0 + (self.progress_value / 20):.1f}MB/s"
                    eta = f"{100 - self.progress_value:02d}:{(100-self.progress_value) * 3 % 60:02d}"
                    
                    status_label.setText(f"進行中 - ETA: {eta}")
                    speed_label.setText(speed)
                    
                    # 每隔10次更新輸出一次日誌
                    if self.progress_value % 10 == 0:
                        log(f"下載進度: {self.progress_value}%, 速度: {speed}, ETA: {eta}")
                    
                    # 更新總進度標籤
                    total_label = self.findChild(QLabel, "total_progress_label")
                    if total_label:
                        if self.progress_value >= 100:
                            total_label.setText(f"總進度：1/4 完成 | 總剩餘時間：約 12 分鐘")
                        else:
                            remaining_time = (100 - self.progress_value) // 10 + 5
                            total_label.setText(f"總進度：0/4 完成 | 總剩餘時間：約 {remaining_time} 分鐘")
                else:
                    # 完成下載
                    status_label.setText("已完成")
                    speed_label.setText("--")
                    self.progress_timer.stop()
                    log(f"下載完成: {first_file}")
                    
                    # 顯示下載完成對話框（V1.55特色功能）
                    self.show_download_complete_dialog(first_file)
                
            self.progress_timer.timeout.connect(update_progress)
            log("開始下載進度計時器...")
            self.progress_timer.start(50)  # 每50毫秒更新一次，使動畫更流暢
        else:
            log("無法找到下載項目控件，下載無法開始")
        
        # 如果有V1.55的SSL問題修復功能，自動應用
        self.apply_ssl_fix()
        
        # 如果使用V1.55的檔案名稱處理功能，添加前綴
        if prefix:
            log(f"應用檔案名稱前綴: {prefix}")

    def show_download_complete_dialog(self, filename):
        """顯示下載完成對話框（V1.55特色功能）"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("下載完成")
        msg_box.setText(f"'{filename}' 已下載完成！")
        msg_box.setInformativeText("您想要現在打開此檔案嗎？")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.addButton("開啟檔案", QMessageBox.AcceptRole)
        msg_box.addButton("開啟資料夾", QMessageBox.ActionRole)
        msg_box.addButton("關閉", QMessageBox.RejectRole)
        
        # 這裡只是示範，不實際執行打開操作
        result = msg_box.exec()
        if result == 0:  # 開啟檔案
            print(f"模擬開啟檔案: {filename}")
        elif result == 1:  # 開啟資料夾
            print(f"模擬開啟包含 {filename} 的資料夾")

    def apply_ssl_fix(self):
        """應用SSL修復（V1.55特色功能）"""
        log("自動套用SSL證書修復...")
        # 這裡是模擬SSL修復的代碼
        try:
            import ssl
            # 模擬SSL設定
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            log("SSL證書驗證已停用，這可以解決某些SSL錯誤")
        except Exception as e:
            log(f"SSL修復遇到問題: {e}")

    def pause_all(self):
        """暫停所有下載任務"""
        log("暫停所有下載任務")
        
        # 獲取所有暫停按鈕
        pause_buttons = self.findChildren(QPushButton)
        for button in pause_buttons:
            if button.objectName().startswith("pause_btn_") and button.text() == "暫停":
                filename = button.objectName().replace("pause_btn_", "")
                log(f"暫停下載項目: {filename}")
                self.toggle_pause_item(filename)
        
        # 如果正在進行模擬下載，停止計時器
        if hasattr(self, 'progress_timer') and self.progress_timer.isActive():
            self.progress_timer.stop()
            log("已停止下載進度計時器")

    def delete_selected(self):
        """刪除選中的下載任務"""
        log("刪除選中的下載任務")
        
        # 在實際應用中，這裡應該獲取被選中的項目
        # 在此演示中，我們將簡單地刪除第一個項目
        
        # 獲取所有進度條
        progress_bars = self.findChildren(QProgressBar)
        
        if progress_bars:
            # 獲取第一個進度條
            first_progress_bar = progress_bars[0]
            if first_progress_bar and first_progress_bar.objectName().startswith("progress_bar_"):
                filename = first_progress_bar.objectName().replace("progress_bar_", "")
                log(f"刪除下載項目: {filename}")
                self.delete_item(filename)
        else:
            log("沒有可刪除的下載項目")

    def on_format_changed(self, index):
        """當格式選擇改變時更新解析度下拉選單"""
        format_text = self.format_combo.currentText()
        
        # 如果選擇的是音訊格式，禁用解析度選擇
        if "僅音訊" in format_text:
            self.resolution_combo.setEnabled(False)
            self.resolution_combo.setCurrentText("自動選擇最佳")
        else:
            self.resolution_combo.setEnabled(True)

    def update_resolution_availability(self):
        """更新解析度可用性（模擬根據影片實際可用解析度）"""
        current_resolution = self.resolution_combo.currentText()
        log(f"已選擇解析度: {current_resolution}")

class DownloadedFilesTab(QWidget):
    """已下載項目標籤頁"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化用戶界面"""
        # 創建主佈局
        layout = QVBoxLayout(self)
        
        # 搜尋和過濾區域
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜尋...")
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("排序:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["最近下載", "檔案名稱", "檔案大小", "影片長度"])
        filter_layout.addWidget(self.sort_combo)
        
        filter_layout.addWidget(QLabel("顯示:"))
        self.view_grid_btn = QPushButton("網格")
        self.view_list_btn = QPushButton("列表")
        filter_layout.addWidget(self.view_grid_btn)
        filter_layout.addWidget(self.view_list_btn)
        
        filter_layout.addStretch(1)
        layout.addLayout(filter_layout)
        
        # 檔案網格視圖 (簡化版)
        files_layout = QGridLayout()
        
        # 模擬檔案項目
        self.create_file_item(files_layout, 0, 0, "影片1", "1080p", "20分鐘", "2024-12-31")
        self.create_file_item(files_layout, 0, 1, "影片2", "720p", "5分鐘", "2024-12-30")
        self.create_file_item(files_layout, 0, 2, "音訊1", "MP3", "3分鐘", "2024-12-29")
        self.create_file_item(files_layout, 0, 3, "影片3", "4K", "15分鐘", "2024-12-28")
        
        files_group = QGroupBox("已下載檔案")
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)
        
        # 檔案操作按鈕
        actions_layout = QHBoxLayout()
        self.open_folder_btn = QPushButton("開啟所在資料夾")
        self.delete_selected_btn = QPushButton("刪除選取")
        self.merge_selected_btn = QPushButton("合併選取的影片和音訊")
        
        actions_layout.addWidget(self.open_folder_btn)
        actions_layout.addWidget(self.delete_selected_btn)
        actions_layout.addWidget(self.merge_selected_btn)
        actions_layout.addStretch(1)
        layout.addLayout(actions_layout)
        
        # 檔案詳情區域
        details_group = QGroupBox("檔案詳情")
        details_layout = QVBoxLayout(details_group)
        details_layout.addWidget(QLabel("檔案名稱：影片1.mp4"))
        details_layout.addWidget(QLabel("影片解析度：1920x1080 (1080p)"))
        details_layout.addWidget(QLabel("檔案大小：235.4 MB"))
        details_layout.addWidget(QLabel("下載時間：2024-12-31 15:42:30"))
        details_layout.addWidget(QLabel("原始連結：https://youtube.com/watch?v=xxxxxxxxxxx"))
        layout.addWidget(details_group)
        
        # 連接信號
        self.open_folder_btn.clicked.connect(self.open_folder)
        self.delete_selected_btn.clicked.connect(self.delete_selected)
        self.merge_selected_btn.clicked.connect(self.merge_selected)
    
    def create_file_item(self, layout, row, col, name, quality, duration, date):
        """創建檔案項目"""
        file_widget = QGroupBox()
        file_layout = QVBoxLayout(file_widget)
        
        icon_type = "▶" if "影片" in name else "♫"
        file_layout.addWidget(QLabel(f"{icon_type} {name}"))
        file_layout.addWidget(QLabel(quality))
        file_layout.addWidget(QLabel(duration))
        file_layout.addWidget(QLabel(date))
        
        layout.addWidget(file_widget, row, col)
    
    def open_folder(self):
        """開啟所在資料夾"""
        print("開啟檔案所在資料夾")
    
    def delete_selected(self):
        """刪除選中的檔案"""
        print("刪除選中的檔案")
    
    def merge_selected(self):
        """合併選中的檔案"""
        print("合併選中的影片和音訊檔案")

class SettingsTab(QWidget):
    """設定標籤頁"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化用戶界面"""
        # 創建主佈局 (左右分割)
        layout = QHBoxLayout(self)
        
        # 左側設定類別列表
        categories_widget = QWidget()
        categories_layout = QVBoxLayout(categories_widget)
        
        self.categories = QListWidget()
        self.categories.addItems([
            "基本設定", 
            "格式與品質", 
            "網路設定", 
            "性能優化", 
            "命名與整理", 
            "界面設定",
            "整合與外掛", 
            "備份與還原"
        ])
        self.categories.setCurrentRow(0)
        categories_layout.addWidget(self.categories)
        
        # 右側設定面板
        self.settings_stack = QStackedWidget()
        
        # 添加各設定頁面
        self.settings_stack.addWidget(self.create_basic_settings())
        self.settings_stack.addWidget(self.create_format_settings())
        self.settings_stack.addWidget(self.create_network_settings())
        self.settings_stack.addWidget(self.create_performance_settings())
        self.settings_stack.addWidget(self.create_naming_settings())
        # 其他設定頁面可以在這裡添加
        
        # 添加到主佈局
        layout.addWidget(categories_widget, 1)
        layout.addWidget(self.settings_stack, 3)
        
        # 連接信號
        self.categories.currentRowChanged.connect(self.settings_stack.setCurrentIndex)
    
    def create_basic_settings(self):
        """創建基本設定頁面"""
        basic_widget = QWidget()
        basic_layout = QVBoxLayout(basic_widget)
        
        # 下載設定組
        download_group = QGroupBox("下載設定")
        download_layout = QVBoxLayout(download_group)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("下載資料夾:"))
        self.folder_input = QLineEdit()
        self.folder_input.setText(str(Path.home() / "Downloads"))
        folder_layout.addWidget(self.folder_input)
        self.browse_btn = QPushButton("瀏覽")
        folder_layout.addWidget(self.browse_btn)
        download_layout.addLayout(folder_layout)
        
        concurrent_layout = QHBoxLayout()
        concurrent_layout.addWidget(QLabel("同時下載數量:"))
        self.concurrent_combo = QComboBox()
        self.concurrent_combo.addItems(["1", "2", "3", "4", "5"])
        self.concurrent_combo.setCurrentIndex(1)  # 預設為2
        concurrent_layout.addWidget(self.concurrent_combo)
        concurrent_layout.addStretch(1)
        download_layout.addLayout(concurrent_layout)
        
        download_layout.addWidget(QLabel("下載完成時:"))
        self.notify_cb = QCheckBox("顯示通知")
        self.notify_cb.setChecked(True)
        self.sound_cb = QCheckBox("播放提示音")
        self.sound_cb.setChecked(True)
        self.open_folder_cb = QCheckBox("自動開啟資料夾")
        self.open_folder_cb.setChecked(False)
        download_layout.addWidget(self.notify_cb)
        download_layout.addWidget(self.sound_cb)
        download_layout.addWidget(self.open_folder_cb)
        
        download_layout.addWidget(QLabel("檔案已存在時:"))
        file_exists_group = QButtonGroup(basic_widget)
        self.ask_radio = QRadioButton("詢問處理方式")
        self.rename_radio = QRadioButton("自動重新命名")
        self.overwrite_radio = QRadioButton("覆寫現有檔案")
        file_exists_group.addButton(self.ask_radio)
        file_exists_group.addButton(self.rename_radio)
        file_exists_group.addButton(self.overwrite_radio)
        self.rename_radio.setChecked(True)
        download_layout.addWidget(self.ask_radio)
        download_layout.addWidget(self.rename_radio)
        download_layout.addWidget(self.overwrite_radio)
        
        basic_layout.addWidget(download_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        self.apply_btn = QPushButton("套用")
        self.cancel_btn = QPushButton("取消")
        self.reset_btn = QPushButton("重設為預設值")
        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.reset_btn)
        basic_layout.addLayout(buttons_layout)
        
        # 連接信號
        self.browse_btn.clicked.connect(self.browse_folder)
        self.apply_btn.clicked.connect(self.apply_settings)
        self.cancel_btn.clicked.connect(self.cancel_changes)
        self.reset_btn.clicked.connect(self.reset_settings)
        
        return basic_widget
    
    def browse_folder(self):
        """瀏覽下載資料夾"""
        folder = QFileDialog.getExistingDirectory(
            self, "選擇下載資料夾", self.folder_input.text()
        )
        if folder:
            self.folder_input.setText(folder)
    
    def apply_settings(self):
        """套用設定"""
        print("套用設定")
    
    def cancel_changes(self):
        """取消更改"""
        print("取消更改")
    
    def reset_settings(self):
        """重設為預設值"""
        print("重設為預設值")

    def create_format_settings(self):
        """創建格式與品質設定頁面"""
        format_widget = QWidget()
        format_layout = QVBoxLayout(format_widget)
        
        # 格式設定組
        format_group = QGroupBox("預設格式與品質")
        format_inner_layout = QVBoxLayout(format_group)
        
        # 預設格式
        default_format_layout = QHBoxLayout()
        default_format_layout.addWidget(QLabel("預設格式:"))
        self.default_format_combo = QComboBox()
        self.default_format_combo.addItems(["最高品質", "僅影片", "僅音訊 (MP3)", "僅音訊 (WAV)"])
        default_format_layout.addWidget(self.default_format_combo)
        default_format_layout.addStretch(1)
        format_inner_layout.addLayout(default_format_layout)
        
        # 預設解析度
        default_resolution_layout = QHBoxLayout()
        default_resolution_layout.addWidget(QLabel("預設解析度:"))
        self.default_resolution_combo = QComboBox()
        self.default_resolution_combo.addItems(["自動選擇最佳", "4K", "1080P (Full HD)", "720P (HD)", "480P", "360P"])
        default_resolution_layout.addWidget(self.default_resolution_combo)
        default_resolution_layout.addStretch(1)
        format_inner_layout.addLayout(default_resolution_layout)
        
        # 音訊品質
        audio_quality_layout = QHBoxLayout()
        audio_quality_layout.addWidget(QLabel("MP3音訊品質:"))
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps"])
        self.audio_quality_combo.setCurrentIndex(2)  # 預設192kbps
        audio_quality_layout.addWidget(self.audio_quality_combo)
        audio_quality_layout.addStretch(1)
        format_inner_layout.addLayout(audio_quality_layout)
        
        format_layout.addWidget(format_group)
        
        # 高解析度設定 (V1.55特色)
        hd_group = QGroupBox("高解析度設定")
        hd_layout = QVBoxLayout(hd_group)
        
        self.prefer_av1_cb = QCheckBox("優先使用AV1編碼格式（如果可用）")
        self.prefer_av1_cb.setChecked(False)
        hd_layout.addWidget(self.prefer_av1_cb)
        
        self.fallback_to_webm_cb = QCheckBox("無法下載MP4時自動嘗試WebM格式")
        self.fallback_to_webm_cb.setChecked(True)
        hd_layout.addWidget(self.fallback_to_webm_cb)
        
        format_layout.addWidget(hd_group)
        
        # 合併設定
        merge_group = QGroupBox("合併設定")
        merge_layout = QVBoxLayout(merge_group)
        
        self.auto_merge_cb = QCheckBox("自動合併影片與音訊")
        self.auto_merge_cb.setChecked(True)
        merge_layout.addWidget(self.auto_merge_cb)
        
        self.keep_separate_files_cb = QCheckBox("保留未合併的原始檔案")
        self.keep_separate_files_cb.setChecked(False)
        merge_layout.addWidget(self.keep_separate_files_cb)
        
        format_layout.addWidget(merge_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        apply_btn = QPushButton("套用")
        cancel_btn = QPushButton("取消")
        reset_btn = QPushButton("重設為預設值")
        buttons_layout.addWidget(apply_btn)
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(reset_btn)
        format_layout.addLayout(buttons_layout)
        
        return format_widget

    def create_network_settings(self):
        """創建網路設定頁面 (包含SSL修復，V1.55特色)"""
        network_widget = QWidget()
        network_layout = QVBoxLayout(network_widget)
        
        # SSL證書設定
        ssl_group = QGroupBox("SSL證書設定")
        ssl_layout = QVBoxLayout(ssl_group)
        
        self.ssl_verification_cb = QCheckBox("啟用SSL證書驗證")
        self.ssl_verification_cb.setChecked(False)
        ssl_layout.addWidget(self.ssl_verification_cb)
        
        self.auto_fix_ssl_cb = QCheckBox("自動修復SSL證書問題")
        self.auto_fix_ssl_cb.setChecked(True)
        ssl_layout.addWidget(self.auto_fix_ssl_cb)
        
        ssl_fix_btn = QPushButton("立即修復SSL證書問題")
        ssl_layout.addWidget(ssl_fix_btn)
        
        network_layout.addWidget(ssl_group)
        
        # 代理伺服器設定
        proxy_group = QGroupBox("代理伺服器設定")
        proxy_layout = QVBoxLayout(proxy_group)
        
        self.use_proxy_cb = QCheckBox("使用代理伺服器")
        self.use_proxy_cb.setChecked(False)
        proxy_layout.addWidget(self.use_proxy_cb)
        
        proxy_address_layout = QHBoxLayout()
        proxy_address_layout.addWidget(QLabel("代理伺服器位址:"))
        self.proxy_address_input = QLineEdit()
        self.proxy_address_input.setEnabled(False)
        proxy_address_layout.addWidget(self.proxy_address_input)
        proxy_layout.addLayout(proxy_address_layout)
        
        network_layout.addWidget(proxy_group)
        
        # 連接設定
        connection_group = QGroupBox("連接設定")
        connection_layout = QVBoxLayout(connection_group)
        
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel("重試次數:"))
        self.retry_spin = QSpinBox()
        self.retry_spin.setMinimum(0)
        self.retry_spin.setMaximum(10)
        self.retry_spin.setValue(3)
        retry_layout.addWidget(self.retry_spin)
        retry_layout.addStretch(1)
        connection_layout.addLayout(retry_layout)
        
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("連接超時 (秒):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(5)
        self.timeout_spin.setMaximum(120)
        self.timeout_spin.setValue(30)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch(1)
        connection_layout.addLayout(timeout_layout)
        
        network_layout.addWidget(connection_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        apply_btn = QPushButton("套用")
        cancel_btn = QPushButton("取消")
        reset_btn = QPushButton("重設為預設值")
        buttons_layout.addWidget(apply_btn)
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(reset_btn)
        network_layout.addLayout(buttons_layout)
        
        # 連接信號
        self.use_proxy_cb.toggled.connect(self.proxy_address_input.setEnabled)
        
        return network_widget

    def create_performance_settings(self):
        """創建性能優化設定頁面"""
        performance_widget = QWidget()
        performance_layout = QVBoxLayout(performance_widget)
        
        # 下載性能
        download_group = QGroupBox("下載性能")
        download_layout = QVBoxLayout(download_group)
        
        concurrent_layout = QHBoxLayout()
        concurrent_layout.addWidget(QLabel("同時下載數量:"))
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setMinimum(1)
        self.concurrent_spin.setMaximum(10)
        self.concurrent_spin.setValue(2)
        concurrent_layout.addWidget(self.concurrent_spin)
        concurrent_layout.addStretch(1)
        download_layout.addLayout(concurrent_layout)
        
        speed_limit_layout = QHBoxLayout()
        speed_limit_layout.addWidget(QLabel("下載速度限制 (KB/s):"))
        self.speed_limit_spin = QSpinBox()
        self.speed_limit_spin.setMinimum(0)
        self.speed_limit_spin.setMaximum(100000)
        self.speed_limit_spin.setValue(0)
        self.speed_limit_spin.setSpecialValueText("無限制")
        speed_limit_layout.addWidget(self.speed_limit_spin)
        speed_limit_layout.addStretch(1)
        download_layout.addLayout(speed_limit_layout)
        
        performance_layout.addWidget(download_group)
        
        # 執行緒設定
        thread_group = QGroupBox("執行緒設定")
        thread_layout = QVBoxLayout(thread_group)
        
        self.use_multithreading_cb = QCheckBox("使用多執行緒下載")
        self.use_multithreading_cb.setChecked(True)
        thread_layout.addWidget(self.use_multithreading_cb)
        
        thread_number_layout = QHBoxLayout()
        thread_number_layout.addWidget(QLabel("每個檔案的執行緒數:"))
        self.thread_number_spin = QSpinBox()
        self.thread_number_spin.setMinimum(1)
        self.thread_number_spin.setMaximum(16)
        self.thread_number_spin.setValue(4)
        thread_number_layout.addWidget(self.thread_number_spin)
        thread_number_layout.addStretch(1)
        thread_layout.addLayout(thread_number_layout)
        
        performance_layout.addWidget(thread_group)
        
        # 記憶體使用
        memory_group = QGroupBox("記憶體使用")
        memory_layout = QVBoxLayout(memory_group)
        
        buffer_layout = QHBoxLayout()
        buffer_layout.addWidget(QLabel("緩衝大小 (MB):"))
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setMinimum(1)
        self.buffer_spin.setMaximum(1024)
        self.buffer_spin.setValue(32)
        buffer_layout.addWidget(self.buffer_spin)
        buffer_layout.addStretch(1)
        memory_layout.addLayout(buffer_layout)
        
        performance_layout.addWidget(memory_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        apply_btn = QPushButton("套用")
        cancel_btn = QPushButton("取消")
        reset_btn = QPushButton("重設為預設值")
        buttons_layout.addWidget(apply_btn)
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(reset_btn)
        performance_layout.addLayout(buttons_layout)
        
        return performance_widget

    def create_naming_settings(self):
        """創建命名與整理設定頁面 (包含檔案名稱前綴，V1.55特色)"""
        naming_widget = QWidget()
        naming_layout = QVBoxLayout(naming_widget)
        
        # 檔案名稱設定
        filename_group = QGroupBox("檔案名稱設定")
        filename_layout = QVBoxLayout(filename_group)
        
        # 檔案名稱前綴 (V1.55特色)
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("預設檔案名稱前綴:"))
        self.default_prefix_input = QLineEdit("TEST-")
        prefix_layout.addWidget(self.default_prefix_input)
        filename_layout.addLayout(prefix_layout)
        
        # 前綴歷史記錄
        prefix_history_layout = QVBoxLayout()
        prefix_history_layout.addWidget(QLabel("前綴歷史記錄:"))
        self.prefix_history_list = QListWidget()
        self.prefix_history_list.addItems(["TEST-", "VIDEO-", "YT-", "DOWNLOAD-"])
        prefix_history_layout.addWidget(self.prefix_history_list)
        
        prefix_buttons_layout = QHBoxLayout()
        self.use_selected_prefix_btn = QPushButton("使用選中的前綴")
        self.remove_prefix_btn = QPushButton("移除選中的前綴")
        prefix_buttons_layout.addWidget(self.use_selected_prefix_btn)
        prefix_buttons_layout.addWidget(self.remove_prefix_btn)
        prefix_history_layout.addLayout(prefix_buttons_layout)
        
        filename_layout.addLayout(prefix_history_layout)
        
        # 檔案名稱模板
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("檔案名稱模板:"))
        self.filename_template_input = QLineEdit("%(title)s.%(ext)s")
        template_layout.addWidget(self.filename_template_input)
        filename_layout.addLayout(template_layout)
        
        # 檔案名稱處理選項
        self.sanitize_filename_cb = QCheckBox("清理檔案名稱中的特殊字符")
        self.sanitize_filename_cb.setChecked(True)
        filename_layout.addWidget(self.sanitize_filename_cb)
        
        self.add_timestamp_cb = QCheckBox("添加時間戳到檔案名稱")
        self.add_timestamp_cb.setChecked(False)
        filename_layout.addWidget(self.add_timestamp_cb)
        
        self.truncate_filename_cb = QCheckBox("截斷過長的檔案名稱")
        self.truncate_filename_cb.setChecked(True)
        filename_layout.addWidget(self.truncate_filename_cb)
        
        max_length_layout = QHBoxLayout()
        max_length_layout.addWidget(QLabel("最大檔案名稱長度:"))
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setMinimum(10)
        self.max_length_spin.setMaximum(500)
        self.max_length_spin.setValue(200)
        max_length_layout.addWidget(self.max_length_spin)
        max_length_layout.addStretch(1)
        filename_layout.addLayout(max_length_layout)
        
        naming_layout.addWidget(filename_group)
        
        # 目錄結構設定
        directory_group = QGroupBox("目錄結構設定")
        directory_layout = QVBoxLayout(directory_group)
        
        self.create_subfolders_cb = QCheckBox("為每個下載工作創建子資料夾")
        self.create_subfolders_cb.setChecked(False)
        directory_layout.addWidget(self.create_subfolders_cb)
        
        self.organize_by_date_cb = QCheckBox("按日期整理檔案")
        self.organize_by_date_cb.setChecked(False)
        directory_layout.addWidget(self.organize_by_date_cb)
        
        naming_layout.addWidget(directory_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        apply_btn = QPushButton("套用")
        cancel_btn = QPushButton("取消")
        reset_btn = QPushButton("重設為預設值")
        buttons_layout.addWidget(apply_btn)
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(reset_btn)
        naming_layout.addLayout(buttons_layout)
        
        return naming_widget

class QStackedWidget(QWidget):
    """自定義堆疊小部件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.widgets = []
        self.current_index = 0
    
    def addWidget(self, widget):
        """添加小部件"""
        self.widgets.append(widget)
        self.layout.addWidget(widget)
        widget.setVisible(len(self.widgets) == 1)
        return len(self.widgets) - 1
    
    def setCurrentIndex(self, index):
        """設置當前索引"""
        if 0 <= index < len(self.widgets):
            self.widgets[self.current_index].setVisible(False)
            self.widgets[index].setVisible(True)
            self.current_index = index

class MainWindow(QMainWindow):
    """主視窗類"""
    
    def __init__(self):
        """初始化"""
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化用戶界面"""
        self.setWindowTitle("YouTube下載器 V2.0 - 分頁式界面")
        self.setGeometry(100, 100, 900, 700)
        
        # 創建主佈局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 創建標籤頁小部件
        self.tabs = QTabWidget()
        
        # 添加標籤頁
        self.download_tab = DownloadTab()
        self.downloaded_files_tab = DownloadedFilesTab()
        self.settings_tab = SettingsTab()
        
        self.tabs.addTab(self.download_tab, "下載任務")
        self.tabs.addTab(self.downloaded_files_tab, "已下載項目")
        self.tabs.addTab(self.settings_tab, "設定")
        
        layout.addWidget(self.tabs)
        
        # 顯示主視窗
        self.show()

def main():
    """主函數"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用Fusion風格，跨平台一致性更好
    
    # 設定應用程式資訊
    app.setApplicationName("YouTube下載器")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("YouTube Downloader")
    
    # 設置應用字體
    font = QFont()
    font.setPointSize(9)
    app.setFont(font)
    
    log("啟動YouTube下載器 V2.0 - 分頁式界面")
    
    window = MainWindow()
    window.show()
    
    log("程式初始化完成")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 