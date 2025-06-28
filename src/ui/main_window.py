from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, 
                             QProgressBar, QComboBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import yt_dlp
import os

class DownloadThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, output_path, format_choice):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_choice = format_choice
    
    def run(self):
        try:
            # 設定下載選項
            ydl_opts = {
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            # 根據格式選擇設定
            if self.format_choice == "最高品質影片":
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            elif self.format_choice == "僅音訊 (MP3)":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif self.format_choice == "僅音訊 (WAV)":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }]
            else:  # 預設品質
                ydl_opts['format'] = 'best'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            self.finished.emit(True, "下載完成！")
            
        except Exception as e:
            self.finished.emit(False, f"下載失敗: {str(e)}")
    
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube 影片下載器 / YouTube Video Downloader / YouTube動画ダウンローダー / 유튜브 비디오 다운로더")
        self.setMinimumSize(900, 700)
        
        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 創建主佈局
        layout = QVBoxLayout(central_widget)
        
        # 標題
        title_label = QLabel("YouTube 影片下載器")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # URL 輸入區域
        url_layout = QHBoxLayout()
        url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("請輸入 YouTube 影片網址...")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # 格式選擇區域
        format_layout = QHBoxLayout()
        format_label = QLabel("下載格式:")
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "預設品質 / Default Quality / デフォルト品質 / 기본 품질",
            "最高品質影片 / Best Video Quality / 最高画質動画 / 최고 화질 비디오",
            "僅音訊 (MP3) / Audio Only (MP3) / 音声のみ (MP3) / 오디오만 (MP3)",
            "僅音訊 (WAV) / Audio Only (WAV) / 音声のみ (WAV) / 오디오만 (WAV)"
        ])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # 下載路徑選擇
        path_layout = QHBoxLayout()
        path_label = QLabel("下載路徑:")
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.expanduser("~/Downloads"))
        self.path_input.setReadOnly(True)
        self.browse_button = QPushButton("瀏覽...")
        self.browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)
        
        # 下載按鈕
        self.download_button = QPushButton("開始下載 / Start Download / ダウンロード開始 / 다운로드 시작")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")
        layout.addWidget(self.download_button)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 日誌輸出
        log_label = QLabel("下載日誌 / Download Log / ダウンロードログ / 다운로드 로그:")
        layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(300)
        layout.addWidget(self.log_output)
        
        # 初始化下載線程
        self.download_thread = None
    
    def browse_path(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇下載資料夾")
        if folder:
            self.path_input.setText(folder)
    
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "請輸入 YouTube URL")
            return
        
        if not os.path.exists(self.path_input.text()):
            QMessageBox.warning(self, "警告", "下載路徑不存在")
            return
        
        # 禁用下載按鈕
        self.download_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不確定進度
        
        # 清空日誌
        self.log_output.clear()
        self.log_output.append("開始下載...")
        
        # 創建下載線程
        format_choice = self.format_combo.currentText().split(" / ")[0]  # 取第一個語言
        self.download_thread = DownloadThread(url, self.path_input.text(), format_choice)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def update_progress(self, message):
        self.log_output.append(message)
        # 自動滾動到底部
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
    
    def download_finished(self, success, message):
        self.download_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.log_output.append(message)
        
        if success:
            QMessageBox.information(self, "完成", "下載完成！")
        else:
            QMessageBox.critical(self, "錯誤", f"下載失敗: {message}") 