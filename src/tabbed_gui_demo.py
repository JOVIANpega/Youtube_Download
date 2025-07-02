#!/usr/bin/env python3
"""
YouTube 下載器 - 分頁式 GUI 演示
YouTube Downloader - Tabbed GUI Demo
YouTubeダウンローダー - タブ付きGUIデモ
유튜브 다운로더 - 탭 GUI 데모
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget,
                               QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTextEdit, QLineEdit, QProgressBar, QCheckBox,
                               QComboBox, QFileDialog, QGroupBox, QSplitter,
                               QListWidget, QGridLayout, QRadioButton,
                               QButtonGroup, QToolBar, QStatusBar, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QTimer
from PySide6.QtGui import QIcon, QAction, QFont

class DownloadTasksTab(QWidget):
    """下載任務標籤頁"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化用戶界面"""
        # 創建主佈局
        layout = QVBoxLayout(self)
        
        # URL輸入區域
        url_group = QGroupBox("貼入一個或多個YouTube網址")
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
        
        # 下載佇列區域
        queue_group = QGroupBox("下載佇列")
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
        total_layout.addWidget(QLabel("總進度：2/4 完成 | 總剩餘時間：約 15 分鐘"))
        total_layout.addStretch(1)
        layout.addLayout(total_layout)
        
        # 連接信號
        self.download_btn.clicked.connect(self.start_download)
        self.pause_btn.clicked.connect(self.pause_all)
        self.delete_btn.clicked.connect(self.delete_selected)
    
    def create_download_item(self, parent_layout, filename, progress, eta, speed, status):
        """創建下載項目"""
        item_layout = QVBoxLayout()
        
        # 檔案名稱和狀態
        name_layout = QHBoxLayout()
        status_icon = "▶️" if status == "進行中" else "⏸️" if status == "已暫停" else "⏳" if status == "等待中" else "❌"
        name_layout.addWidget(QLabel(f"{status_icon} {filename}"))
        name_layout.addStretch(1)
        item_layout.addLayout(name_layout)
        
        # 進度條
        progress_layout = QHBoxLayout()
        progress_bar = QProgressBar()
        progress_bar.setValue(progress)
        progress_layout.addWidget(progress_bar)
        item_layout.addLayout(progress_layout)
        
        # 詳細資訊
        if status == "進行中":
            info_label = QLabel(f"ETA: {eta} | 速度: {speed}")
            item_layout.addWidget(info_label)
        elif status == "已暫停":
            info_label = QLabel(f"狀態: {status}")
            item_layout.addWidget(info_label)
        elif status == "等待中":
            info_label = QLabel(f"狀態: {status}...")
            item_layout.addWidget(info_label)
        elif "錯誤" in status:
            error_layout = QHBoxLayout()
            error_layout.addWidget(QLabel(f"{status}"))
            retry_btn = QPushButton("重試")
            info_btn = QPushButton("詳情")
            error_layout.addWidget(retry_btn)
            error_layout.addWidget(info_btn)
            error_layout.addStretch(1)
            item_layout.addLayout(error_layout)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        
        parent_layout.addLayout(item_layout)
        parent_layout.addWidget(separator)
    
    def start_download(self):
        """開始下載"""
        urls = self.url_input.toPlainText().strip().split('\n')
        valid_urls = [url for url in urls if url.strip()]
        
        if not valid_urls:
            print("請輸入至少一個有效的YouTube網址")
            return
        
        print(f"開始下載 {len(valid_urls)} 個影片...")
    
    def pause_all(self):
        """暫停所有下載"""
        print("暫停所有下載任務")
    
    def delete_selected(self):
        """刪除選中的下載任務"""
        print("刪除選中的下載任務")

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
            "基本設定", "格式與品質", "網路設定", 
            "性能優化", "命名與整理", "界面設定",
            "整合與外掛", "備份與還原"
        ])
        self.categories.setCurrentRow(0)
        categories_layout.addWidget(self.categories)
        
        # 右側設定面板
        self.settings_stack = QStackedWidget()
        
        # 添加各設定頁面
        self.settings_stack.addWidget(self.create_basic_settings())
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
    """主視窗"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube下載器 V2.0 - 分頁式GUI演示")
        self.setMinimumSize(900, 700)
        self.init_ui()
    
    def init_ui(self):
        """初始化用戶界面"""
        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 創建主佈局
        layout = QVBoxLayout(central_widget)
        
        # 創建分頁部件
        self.tabs = QTabWidget()
        
        # 添加標籤頁
        self.download_tasks_tab = DownloadTasksTab()
        self.downloaded_files_tab = DownloadedFilesTab()
        self.settings_tab = SettingsTab()
        
        self.tabs.addTab(self.download_tasks_tab, "下載任務")
        self.tabs.addTab(self.downloaded_files_tab, "已下載項目")
        self.tabs.addTab(self.settings_tab, "設定")
        
        # 添加到主佈局
        layout.addWidget(self.tabs)
        
        # 創建狀態欄
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就緒")
        
        # 設定視窗大小
        self.resize(1024, 768)

def main():
    """主函數"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用Fusion風格，跨平台一致性更好
    
    # 設定應用程式資訊
    app.setApplicationName("YouTube下載器")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("YouTube Downloader")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 