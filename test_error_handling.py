#!/usr/bin/env python3
"""
測試錯誤處理功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import QTimer

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("錯誤處理測試")
        self.setGeometry(100, 100, 400, 300)
        
        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 添加說明
        info_label = QLabel("點擊按鈕測試不同的錯誤處理場景")
        layout.addWidget(info_label)
        
        # 測試按鈕
        test_yt_dlp_failure_btn = QPushButton("測試 yt-dlp 失敗錯誤")
        test_yt_dlp_failure_btn.clicked.connect(self.test_yt_dlp_failure)
        layout.addWidget(test_yt_dlp_failure_btn)
        
        test_normal_error_btn = QPushButton("測試一般錯誤")
        test_normal_error_btn.clicked.connect(self.test_normal_error)
        layout.addWidget(test_normal_error_btn)
        
        test_x_platform_btn = QPushButton("測試 X.com 平台錯誤")
        test_x_platform_btn.clicked.connect(self.test_x_platform_error)
        layout.addWidget(test_x_platform_btn)
        
        # 添加間距
        layout.addStretch()
        
    def test_yt_dlp_failure(self):
        """測試 yt-dlp 失敗錯誤"""
        from tabbed_gui_demo import DownloadTab
        
        # 創建下載標籤頁實例
        download_tab = DownloadTab()
        
        # 模擬 yt-dlp 失敗錯誤
        error_message = "YT_DLP_FAILURE:X:ERROR: [twitter] 1624007411433611264: You are not authorized to view this protected tweet. Use --cookies, --cookies-from-browser, --username and --password, --netrc-cmd, or --netrc (twitter) to provide account credentials."
        
        # 顯示錯誤對話框
        download_tab.show_error_dialog("test_video.mp4", error_message)
        
    def test_normal_error(self):
        """測試一般錯誤"""
        from tabbed_gui_demo import DownloadTab
        
        # 創建下載標籤頁實例
        download_tab = DownloadTab()
        
        # 模擬一般錯誤
        error_message = "下載失敗：網路連接問題"
        
        # 顯示錯誤對話框
        download_tab.show_error_dialog("test_video.mp4", error_message)
        
    def test_x_platform_error(self):
        """測試 X.com 平台錯誤"""
        from tabbed_gui_demo import DownloadTab
        
        # 創建下載標籤頁實例
        download_tab = DownloadTab()
        
        # 模擬 X.com 平台錯誤
        error_message = "YT_DLP_FAILURE:X:ERROR: [twitter] 1939972916004684072: NSFW tweet requires authentication. Use --cookies, --cookies-from-browser, --username and --password, --netrc-cmd, or --netrc (twitter) to provide account credentials."
        
        # 顯示錯誤對話框
        download_tab.show_error_dialog("test_video.mp4", error_message)

def main():
    app = QApplication(sys.argv)
    
    # 創建測試視窗
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 