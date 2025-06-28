#!/usr/bin/env python3
"""
修復版 YouTube 下載器 - 解決檔案名稱問題
Fixed YouTube Downloader - Filename Issue Resolution
修正版YouTubeダウンローダー - ファイル名問題解決
수정된 유튜브 다운로더 - 파일명 문제 해결
"""

import sys
import os
import ssl
import certifi
import re
import urllib3
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                               QTextEdit, QProgressBar, QComboBox, QFileDialog, 
                               QMessageBox, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal
import yt_dlp

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 修復 SSL 問題
def fix_ssl_issues():
    """修復 SSL 證書問題"""
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 設定全域 SSL 上下文
        ssl._create_default_https_context = lambda: ssl_context
        
        # 設定環境變數
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        
        ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
        
        print("✓ SSL 問題已修復")
        return True
        
    except Exception as e:
        print(f"✗ SSL 修復失敗: {e}")
        return False

class FixedDownloadThread(QThread):
    progress = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, url, output_path):
        super().__init__()
        self.url = url
        self.output_path = output_path
    
    def run(self):
        try:
            self.progress.emit("正在獲取影片資訊...")
            
            # 強化的資訊獲取選項
            info_opts = {
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'socket_timeout': 60,
                'retries': 5,
                'fragment_retries': 5,
                'extractor_retries': 5,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            }
            
            # 嘗試獲取影片資訊
            video_title = None
            try:
                with yt_dlp.YoutubeDL(info_opts) as ydl:
                    info = ydl.extract_info(self.url, download=False)
                    video_title = info.get('title', 'Unknown Video')
                    self.progress.emit(f"✓ 成功獲取影片標題: {video_title}")
            except Exception as e:
                self.progress.emit(f"⚠️ 獲取影片資訊失敗: {str(e)}")
                # 嘗試從 URL 提取 ID 並使用備用方法
                video_id = self.extract_video_id(self.url)
                if video_id:
                    video_title = f"YouTube_Video_{video_id}"
                else:
                    video_title = "YouTube_Video"
            
            # 清理檔案名稱
            safe_title = self.sanitize_filename(video_title)
            self.progress.emit(f"清理後的檔案名稱: {safe_title}")
            
            # 強化的下載選項
            ydl_opts = {
                'outtmpl': os.path.join(self.output_path, f'{safe_title}.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'format': 'best',
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'socket_timeout': 60,
                'retries': 5,
                'fragment_retries': 5,
                'extractor_retries': 5,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'live'],
                    }
                },
            }
            
            self.progress.emit(f"開始下載: {video_title}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            self.finished.emit(True, f"下載完成！檔案名稱: {safe_title}")
            
        except Exception as e:
            self.finished.emit(False, f"下載失敗: {str(e)}")
    
    def extract_video_id(self, url):
        """從 URL 提取影片 ID"""
        import re
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def sanitize_filename(self, filename):
        """清理檔案名稱，移除或替換不合法字符"""
        # 移除或替換不合法字符
        # Windows 不合法字符: < > : " | ? * \ /
        # 也移除其他可能造成問題的字符
        illegal_chars = r'[<>:"|?*\\/\n\r\t]'
        filename = re.sub(illegal_chars, '_', filename)
        
        # 移除開頭和結尾的空格和點
        filename = filename.strip(' .')
        
        # 限制檔案名稱長度 (Windows 限制為 255 字符，但我們設為 200 以留餘地)
        if len(filename) > 200:
            filename = filename[:200]
        
        # 如果檔案名稱為空，使用預設名稱
        if not filename:
            filename = "YouTube_Video"
        
        return filename
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024
                    self.progress.emit(f"下載中... {percent:.1f}% - 速度: {speed_mb:.1f} MB/s")
                else:
                    self.progress.emit(f"下載中... {percent:.1f}%")
            else:
                self.progress.emit("下載中...")
        elif d['status'] == 'finished':
            self.progress.emit("檔案下載完成，正在處理...")

class FixedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("修復版 YouTube 下載器 - 檔案名稱問題解決")
        self.setMinimumSize(800, 600)
        
        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 創建主佈局
        layout = QVBoxLayout(central_widget)
        
        # 標題
        title_label = QLabel("修復版 YouTube 下載器")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # URL 輸入區域
        url_group = QGroupBox("影片資訊")
        url_layout = QVBoxLayout(url_group)
        
        url_input_layout = QHBoxLayout()
        url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("請輸入 YouTube 影片網址...")
        # 預設填入測試 URL
        self.url_input.setText("https://www.youtube.com/watch?v=wa3f6E1qf-Y")
        url_input_layout.addWidget(url_label)
        url_input_layout.addWidget(self.url_input)
        url_layout.addLayout(url_input_layout)
        
        layout.addWidget(url_group)
        
        # 下載路徑選擇
        path_group = QGroupBox("下載設定")
        path_layout = QVBoxLayout(path_group)
        
        path_input_layout = QHBoxLayout()
        path_label = QLabel("下載路徑:")
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.expanduser("~/Downloads"))
        self.path_input.setReadOnly(True)
        self.browse_button = QPushButton("瀏覽...")
        self.browse_button.clicked.connect(self.browse_path)
        path_input_layout.addWidget(path_label)
        path_input_layout.addWidget(self.path_input)
        path_input_layout.addWidget(self.browse_button)
        path_layout.addLayout(path_input_layout)
        
        layout.addWidget(path_group)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        
        # 測試按鈕
        self.test_button = QPushButton("測試按鈕")
        self.test_button.clicked.connect(self.test_button_click)
        self.test_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: #2196F3; color: white;")
        button_layout.addWidget(self.test_button)
        
        # 下載按鈕
        self.download_button = QPushButton("開始下載")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")
        button_layout.addWidget(self.download_button)
        
        layout.addLayout(button_layout)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 日誌輸出
        log_group = QGroupBox("下載日誌")
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(200)
        log_layout.addWidget(self.log_output)
        
        layout.addWidget(log_group)
        
        # 初始化下載線程
        self.download_thread = None
        
        # 添加初始日誌
        self.log_output.append("修復版下載器已啟動")
        self.log_output.append("已預設填入測試 URL: https://www.youtube.com/watch?v=wa3f6E1qf-Y")
        self.log_output.append("預期檔案名稱: Podezřelý zloděj nebo vandal u zaparkovaného auta | Policie v akci")
    
    def test_button_click(self):
        """測試按鈕點擊事件"""
        self.log_output.append("✓ 測試按鈕被點擊了！")
        QMessageBox.information(self, "測試", "測試按鈕正常工作！")
    
    def browse_path(self):
        """瀏覽下載路徑"""
        folder = QFileDialog.getExistingDirectory(self, "選擇下載資料夾")
        if folder:
            self.path_input.setText(folder)
            self.log_output.append(f"下載路徑已設定為: {folder}")
    
    def start_download(self):
        """開始下載"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "請輸入 YouTube URL")
            self.log_output.append("✗ 請輸入 YouTube URL")
            return
        
        if not os.path.exists(self.path_input.text()):
            QMessageBox.warning(self, "警告", "下載路徑不存在")
            self.log_output.append("✗ 下載路徑不存在")
            return
        
        # 禁用下載按鈕
        self.download_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不確定進度
        
        # 清空日誌
        self.log_output.clear()
        self.log_output.append("開始下載...")
        
        # 創建下載線程
        self.download_thread = FixedDownloadThread(url, self.path_input.text())
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def update_progress(self, message):
        """更新進度"""
        self.log_output.append(message)
        # 自動滾動到底部
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
    
    def download_finished(self, success, message):
        """下載完成"""
        self.download_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.log_output.append(message)
        
        if success:
            QMessageBox.information(self, "完成", "下載完成！")
        else:
            QMessageBox.critical(self, "錯誤", f"下載失敗: {message}")

def main():
    # 修復 SSL 問題
    fix_ssl_issues()
    
    app = QApplication(sys.argv)
    window = FixedMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 