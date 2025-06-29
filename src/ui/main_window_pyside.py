from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, 
                             QProgressBar, QComboBox, QFileDialog, QMessageBox,
                             QGroupBox, QGridLayout, QCheckBox, QMenu, QRadioButton, QButtonGroup, QSplitter, QListWidget)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QCloseEvent, QAction
import yt_dlp
import os
import ssl
import sys
import re
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_preferences import UserPreferences

def safe_filename(filename, max_length=100):
    """全域安全檔名函式：允許各國語言文字、數字、底線、減號、點，只過濾 Windows 不允許的字符"""
    # 只過濾掉Windows不允許的字符: \ / : * ? " < > |
    filename = re.sub(r'[\\\/\:\*\?\"\<\>\|]', '_', filename)
    filename = filename.strip(' .')
    if len(filename) > max_length:
        filename = filename[:max_length]
    if not filename:
        filename = "YouTube_Video"
    return filename

class DownloadThread(QThread):
    progress = Signal(str)
    finished = Signal(bool, str)
    formats_ready = Signal(list)
    
    def __init__(self, url, output_path, format_choice, resolution_choice, extract_audio_only, filename_prefix="", format_string=None, merge_output_format='mp4', fallback_to_webm=False, cookies_path=None):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_choice = format_choice
        self.resolution_choice = resolution_choice
        self.extract_audio_only = extract_audio_only
        self.filename_prefix = filename_prefix
        self.format_string = format_string
        self.merge_output_format = merge_output_format
        self.fallback_to_webm = fallback_to_webm
        self.cookies_path = cookies_path
        self.formats = []
        self.format_id_map = {}
    
    def run(self):
        try:
            self.progress.emit("正在獲取影片資訊...")
            import yt_dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'socket_timeout': 30,
                'retries': 3,
            }
            if self.cookies_path:
                ydl_opts['cookies'] = self.cookies_path
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.formats = info.get('formats', [])
                video_title = info.get('title', 'Unknown Video')
                safe_title = safe_filename(video_title)
                if self.filename_prefix:
                    safe_title = f"{safe_filename(self.filename_prefix)}{safe_title}"
                
                # 使用安全的檔名，保留各國語言字符
                download_opts = {
                    'outtmpl': os.path.join(self.output_path, f'{safe_title}.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'nocheckcertificate': True,
                    'ignoreerrors': False,
                    'socket_timeout': 30,
                    'retries': 3,
                }
                
                if self.extract_audio_only:
                    download_opts['format'] = 'bestaudio/best'
                    download_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3' if self.format_choice == "僅音訊 (MP3)" else 'wav',
                        'preferredquality': '192',
                    }]
                else:
                    # 根據解析度選擇格式
                    if self.resolution_choice == "最高品質":
                        download_opts['format'] = 'bestvideo+bestaudio/best'
                        self.progress.emit("使用最高品質模式 (分離視頻和音頻流)")
                    elif self.resolution_choice == "1080P (Full HD)" and any(fmt.get('height') == 1080 for fmt in self.formats):
                        download_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
                        self.progress.emit("使用 1080P 解析度")
                    elif self.resolution_choice == "720P (HD)" and any(fmt.get('height') == 720 for fmt in self.formats):
                        download_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
                        self.progress.emit("使用 720P 解析度")
                    else:
                        # 預設使用最佳可用格式
                        download_opts['format'] = 'bestvideo+bestaudio/best'
                        self.progress.emit("使用預設最佳解析度")
                    
                    download_opts['merge_output_format'] = self.merge_output_format
                
                self.progress.emit(f"開始下載: {video_title} ({download_opts['format']})")
                
                try:
                    # 嘗試下載
                    with yt_dlp.YoutubeDL(download_opts) as ydl:
                        ydl.download([self.url])
                    
                    # 檢查下載結果
                    ext = self.merge_output_format if not self.extract_audio_only else ('mp3' if self.format_choice == "僅音訊 (MP3)" else 'wav')
                    final_filename = f"{safe_title}.{ext}"
                    final_path = os.path.join(self.output_path, final_filename)
                    
                    if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                        self.finished.emit(True, f"下載完成！檔案名稱: {final_filename}")
                    else:
                        # 如果沒有找到預期的檔案，嘗試查找任何新下載的檔案
                        import glob
                        pattern = os.path.join(self.output_path, f"{safe_title}.*")
                        files = [f for f in glob.glob(pattern) if os.path.getsize(f) > 0]
                        
                        if not files:
                            # 嘗試查找任何新下載的檔案
                            all_files = os.listdir(self.output_path)
                            recent_files = [os.path.join(self.output_path, f) for f in all_files 
                                          if os.path.getmtime(os.path.join(self.output_path, f)) > time.time() - 60]
                            if recent_files:
                                files = sorted(recent_files, key=os.path.getmtime, reverse=True)
                        
                        if files:
                            actual_filename = os.path.basename(files[0])
                            self.progress.emit(f"<span style=\"color: green;\">✅ 已下載檔案：{actual_filename}</span>")
                            self.finished.emit(True, f"下載完成！檔案名稱: {actual_filename}")
                        else:
                            self.finished.emit(False, "下載失敗：檔案不存在或大小為0，可能是影片受限、已刪除或無法下載。建議升級 yt-dlp 或用 cookies。")
                
                except Exception as e:
                    self.progress.emit(f"下載失敗: {str(e)}")
                    
                    # 檢查是否是合併錯誤
                    if "Postprocessing" in str(e) and "Could not write header" in str(e):
                        self.progress.emit("合併視頻和音頻失敗，嘗試保留已下載的檔案...")
                        
                        # 查找已下載的檔案
                        import glob
                        pattern = os.path.join(self.output_path, f"{safe_title}.*")
                        files = [f for f in glob.glob(pattern) if os.path.getsize(f) > 0]
                        
                        if files:
                            # 找到最大的檔案（可能是視頻檔案）
                            largest_file = max(files, key=os.path.getsize)
                            actual_filename = os.path.basename(largest_file)
                            self.progress.emit(f"<span style=\"color: green;\">✅ 保留已下載的檔案：{actual_filename}</span>")
                            self.finished.emit(True, f"下載完成！檔案名稱: {actual_filename}")
                            return
                    
                    # 如果不是合併錯誤或找不到已下載檔案，嘗試使用備用格式
                    self.progress.emit("嘗試使用備用格式...")
                    
                    # 先嘗試使用單一高解析度格式
                    download_opts['format'] = 'best[height<=1080]/best[height<=720]/best'
                    try:
                        with yt_dlp.YoutubeDL(download_opts) as ydl:
                            ydl.download([self.url])
                        self.progress.emit("<span style=\"color: green;\">✅ 使用備用高解析度格式下載成功</span>")
                        
                        # 查找下載的檔案
                        import glob
                        pattern = os.path.join(self.output_path, f"{safe_title}.*")
                        files = [f for f in glob.glob(pattern) if os.path.getsize(f) > 0]
                        
                        if files:
                            actual_filename = os.path.basename(files[0])
                            self.finished.emit(True, f"下載完成！檔案名稱: {actual_filename}")
                            return
                    except Exception as e2:
                        self.progress.emit(f"備用高解析度格式失敗: {str(e2)}")
                    
                    # 如果高解析度格式也失敗，嘗試使用 18 格式（常見的 360p mp4 格式）
                    self.progress.emit("嘗試使用標準 360p 格式...")
                    download_opts['format'] = '18/best'
                    try:
                        with yt_dlp.YoutubeDL(download_opts) as ydl:
                            ydl.download([self.url])
                        self.progress.emit("<span style=\"color: green;\">✅ 使用標準 360p 格式下載成功</span>")
                        
                        # 查找下載的檔案
                        import glob
                        pattern = os.path.join(self.output_path, f"{safe_title}.*")
                        files = [f for f in glob.glob(pattern) if os.path.getsize(f) > 0]
                        
                        if files:
                            actual_filename = os.path.basename(files[0])
                            self.progress.emit(f"<span style=\"color: green;\">✅ 使用標準 360p 格式下載成功：{actual_filename}</span>")
                            self.finished.emit(True, f"下載完成！檔案名稱: {actual_filename}")
                        else:
                            self.finished.emit(False, "下載失敗：找不到下載的檔案")
                    except Exception as e3:
                        self.progress.emit(f"所有備用格式都失敗: {str(e3)}")
                        self.finished.emit(False, f"下載失敗: {str(e)}。建議升級 yt-dlp 或用 cookies。")
        except Exception as e:
            # 年齡限制自動提示
            if 'Sign in to confirm your age' in str(e) or 'Use --cookies-from-browser or --cookies' in str(e):
                self.progress.emit("❗ 此影片有年齡限制，請先登入 YouTube 並匯出 cookies.txt，再於下載選項中選擇 cookies 檔案！")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "需要 cookies 驗證", "此影片有年齡限制，請先登入 YouTube 並匯出 cookies.txt，再於下載選項中選擇 cookies 檔案！\n\n詳見 https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp")
            self.progress.emit(f"主要方法失敗: {str(e)}")
            self.finished.emit(False, f"下載失敗: {str(e)}。建議升級 yt-dlp 或用 cookies。")
    
    def filter_formats(self, formats):
        """過濾並排序可用格式"""
        available_formats = []
        
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                # 完整影片格式
                height = fmt.get('height', 0)
                if height > 0:
                    available_formats.append({
                        'format_id': fmt.get('format_id', ''),
                        'resolution': f"{height}p",
                        'filesize': fmt.get('filesize', 0),
                        'ext': fmt.get('ext', ''),
                        'description': f"{height}p - {fmt.get('ext', '')} - {self.format_filesize(fmt.get('filesize', 0))}"
                    })
        
        # 去重並排序
        unique_formats = []
        seen_resolutions = set()
        for fmt in sorted(available_formats, key=lambda x: int(x['resolution'].replace('p', '')), reverse=True):
            if fmt['resolution'] not in seen_resolutions:
                unique_formats.append(fmt)
                seen_resolutions.add(fmt['resolution'])
        
        return unique_formats
    
    def get_format_by_resolution(self, resolution):
        """根據解析度選擇格式"""
        if resolution == "自動選擇最佳":
            return 'best'
        elif resolution == "最高品質":
            return 'bestvideo+bestaudio/best'
        elif resolution == "1080P (Full HD)":
            target_height = 1080
        elif resolution == "720P (HD)":
            target_height = 720
        elif resolution == "480P":
            target_height = 480
        elif resolution == "360P":
            target_height = 360
        else:
            return 'best'
        
        # 找到最接近的格式
        best_format = None
        min_diff = float('inf')
        
        for fmt in self.formats:
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                height = fmt.get('height', 0)
                if height > 0:
                    diff = abs(height - target_height)
                    if diff < min_diff:
                        min_diff = diff
                        best_format = fmt.get('format_id', 'best')
        
        return best_format or 'best'
    
    def format_filesize(self, size):
        """格式化檔案大小"""
        if size == 0:
            return "未知大小"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
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
    
    def sanitize_filename(self, filename):
        # 廢棄，統一用 safe_filename
        return safe_filename(filename)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube 影片下載器 / YouTube Video Downloader")
        self.setMinimumSize(800, 600)
        self.resize(1000, 800)  # 設定預設大小
        
        # 初始化使用者偏好
        self.preferences = UserPreferences()
        
        # 設定視窗位置和大小
        self.setup_window_geometry()
        
        # --- 新增 QSplitter ---
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        # 左側操作區
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.splitter.addWidget(left_widget)

        # 右側日誌區
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.splitter.addWidget(right_widget)
        
        # 設置全局字體大小
        self.setStyleSheet("""
            QLabel, QCheckBox, QRadioButton, QComboBox, QLineEdit, QGroupBox { font-size: 11pt; }
            QPushButton { font-size: 11pt; }
            QTextEdit { font-size: 11pt; }
        """)

        # 標題和版本資訊
        title_label = QLabel("YouTube 影片下載器")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px;")
        left_layout.addWidget(title_label)
        
        # 版本資訊
        version = ""
        try:
            import sys, os
            # 支援 PyInstaller 打包後的相對路徑
            if hasattr(sys, '_MEIPASS'):
                version_path = os.path.join(sys._MEIPASS, 'VERSION')
            else:
                version_path = "VERSION"
            with open(version_path, "r", encoding="utf-8") as f:
                version = f.readline().strip()
        except Exception:
            version = "未偵測到版本"
        version_label = QLabel(f"版本：{version}")
        version_label.setAlignment(Qt.AlignRight)
        version_label.setStyleSheet("font-size: 12px; color: #888; margin: 5px;")
        left_layout.addWidget(version_label)
        
        # URL 輸入區域
        url_group = QGroupBox("影片資訊")
        url_layout = QVBoxLayout(url_group)
        url_input_layout = QVBoxLayout()  # 改為垂直佈局
        url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("請輸入 YouTube 影片網址...")
        self.url_input.setMinimumHeight(40)  # 增加高度
        self.url_input.setStyleSheet("font-size: 14px; padding: 5px;")  # 增加字體大小和內邊距
        # recent_urls_combo 只建立但不加到UI，避免程式錯誤
        self.recent_urls_combo = QComboBox()
        
        # 先添加標籤和輸入框
        url_label_layout = QHBoxLayout()
        url_label_layout.addWidget(url_label)
        url_input_layout.addLayout(url_label_layout)
        url_input_layout.addWidget(self.url_input)
        
        # 獲取資訊按鈕和檢查更新按鈕放在同一行
        button_layout = QHBoxLayout()
        
        # 獲取資訊按鈕
        self.fetch_button = QPushButton("獲取資訊")
        self.fetch_button.clicked.connect(self.fetch_video_info)
        self.fetch_button.setStyleSheet("font-size: 11pt; padding: 10px; background-color: #4CAF50; color: white;")
        
        # 檢查更新按鈕
        self.update_ytdlp_button = QPushButton("檢查更新")
        self.update_ytdlp_button.setStyleSheet("font-size: 11pt; padding: 10px; background-color: #2196F3; color: white;")
        self.update_ytdlp_button.clicked.connect(self.check_and_update_ytdlp)
        
        button_layout.addStretch()
        button_layout.addWidget(self.fetch_button)
        button_layout.addWidget(self.update_ytdlp_button)
        url_input_layout.addLayout(button_layout)
        
        url_layout.addLayout(url_input_layout)
        # 下載完成提醒設定
        self.show_completion_dialog = QCheckBox("下載完成後顯示提醒視窗")
        self.show_completion_dialog.setChecked(self.preferences.get_show_completion_dialog())
        self.show_completion_dialog.stateChanged.connect(self.on_completion_dialog_changed)
        url_layout.addWidget(self.show_completion_dialog)
        
        # 新增 fallback 提示 label
        self.fallback_info_label = QLabel()
        self.fallback_info_label.setStyleSheet("color: #388e3c; font-weight: bold; margin: 2px 0 0 0;")
        self.fallback_info_label.setVisible(False)
        url_layout.addWidget(self.fallback_info_label)
        left_layout.addWidget(url_group)
        
        # 下載選項區域
        options_group = QGroupBox("下載選項")
        options_layout = QGridLayout(options_group)
        
        # 下載類型（RadioButton）
        type_label = QLabel("下載類型:")
        self.radio_video = QRadioButton("影片")
        self.radio_audio_mp3 = QRadioButton("僅音訊 (MP3)")
        self.radio_audio_wav = QRadioButton("僅音訊 (WAV)")
        self.radio_video.setChecked(True)
        self.type_group = QButtonGroup()
        self.type_group.addButton(self.radio_video)
        self.type_group.addButton(self.radio_audio_mp3)
        self.type_group.addButton(self.radio_audio_wav)
        type_layout = QHBoxLayout()
        type_layout.addWidget(self.radio_video)
        type_layout.addWidget(self.radio_audio_mp3)
        type_layout.addWidget(self.radio_audio_wav)
        options_layout.addWidget(type_label, 0, 0)
        options_layout.addLayout(type_layout, 0, 1)
        
        # 解析度選擇 - 動態載入影片實際可用解析度
        resolution_label = QLabel("解析度:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "自動選擇最佳",
            "最高品質"
        ])
        # 預設為自動選擇最佳
        self.resolution_combo.setCurrentText("自動選擇最佳")
        options_layout.addWidget(resolution_label, 1, 0)
        options_layout.addWidget(self.resolution_combo, 1, 1)
        
        # 下載路徑選擇
        path_label = QLabel("下載路徑:")
        self.path_input = QLineEdit()
        self.path_input.setText(self.preferences.get_download_path())
        self.path_input.setReadOnly(True)
        self.browse_button = QPushButton("瀏覽...")
        self.browse_button.clicked.connect(self.browse_path)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        options_layout.addWidget(path_label, 2, 0)
        options_layout.addLayout(path_layout, 2, 1)

        # cookies.txt 選擇
        cookies_label = QLabel("Cookies 檔案:")
        self.cookies_input = QLineEdit()
        self.cookies_input.setPlaceholderText("選擇 cookies.txt (如需登入驗證)")
        self.cookies_input.setReadOnly(True)
        self.cookies_button = QPushButton("選擇...")
        self.cookies_button.clicked.connect(self.browse_cookies)
        cookies_layout = QHBoxLayout()
        cookies_layout.addWidget(self.cookies_input)
        cookies_layout.addWidget(self.cookies_button)
        options_layout.addWidget(cookies_label, 3, 0)
        options_layout.addLayout(cookies_layout, 3, 1)
        
        # 檔案名稱前綴設定 - 改為下拉組合框
        prefix_label = QLabel("檔案名稱前綴:")
        
        # 創建水平佈局來放置輸入框和下拉按鈕
        prefix_layout = QHBoxLayout()
        
        # 創建輸入框
        self.filename_prefix = QLineEdit()
        self.filename_prefix.setPlaceholderText("例如: TEST- (留空使用原檔名)")
        # 使用記住的前綴設定
        self.filename_prefix.setText(self.preferences.get_filename_prefix())
        self.filename_prefix.textChanged.connect(self.on_filename_prefix_changed)
        
        # 創建前綴歷史下拉框
        self.prefix_history_combo = QComboBox()
        self.prefix_history_combo.setFixedWidth(30)  # 設置為較窄的寬度
        self.prefix_history_combo.setToolTip("選擇歷史前綴")
        
        # 載入前綴歷史
        self.load_prefix_history()
        
        # 當選擇歷史前綴時更新輸入框
        self.prefix_history_combo.currentTextChanged.connect(self.on_prefix_history_selected)
        
        # 添加到佈局
        prefix_layout.addWidget(self.filename_prefix)
        prefix_layout.addWidget(self.prefix_history_combo)
        
        options_layout.addWidget(prefix_label, 4, 0)
        options_layout.addLayout(prefix_layout, 4, 1)
        

        
        left_layout.addWidget(options_group)
        
        # 下載控制按鈕
        button_layout = QHBoxLayout()
        
        # 下載按鈕
        self.download_button = QPushButton("開始下載")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setStyleSheet("font-size: 11pt; padding: 10px; background-color: #4CAF50; color: white;")
        button_layout.addWidget(self.download_button)
        
        # 停止下載按鈕
        self.stop_button = QPushButton("停止下載")
        self.stop_button.clicked.connect(self.stop_download)
        self.stop_button.setStyleSheet("font-size: 11pt; padding: 10px; background-color: #f44336; color: white;")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        left_layout.addLayout(button_layout)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # 右側：下載日誌
        log_group = QGroupBox("下載日誌")
        log_layout = QVBoxLayout(log_group)
        
        # 添加文字大小調整按鈕
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("文字大小:")
        font_size_layout.addWidget(font_size_label)
        
        self.decrease_font_button = QPushButton("-")
        self.decrease_font_button.setFixedSize(30, 25)
        self.decrease_font_button.clicked.connect(self.decrease_log_font_size)
        font_size_layout.addWidget(self.decrease_font_button)
        
        self.increase_font_button = QPushButton("+")
        self.increase_font_button.setFixedSize(30, 25)
        self.increase_font_button.clicked.connect(self.increase_log_font_size)
        font_size_layout.addWidget(self.increase_font_button)
        
        font_size_layout.addStretch()
        log_layout.addLayout(font_size_layout)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(16777215)  # 允許最大高度
        # 從用戶偏好中加載字體大小或使用預設值
        self.current_font_size = self.preferences.get("log_font_size", 11)
        self.log_output.setStyleSheet(f"font-size: {self.current_font_size}pt;")
        self.log_output.setAcceptRichText(True)  # 允許富文本顯示，支援HTML標籤
        log_layout.addWidget(self.log_output)
        
        right_layout.addWidget(log_group)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # 預設分割比例或還原上次分割比例
        splitter_sizes = self.preferences.get("splitter_sizes", None)
        if splitter_sizes and isinstance(splitter_sizes, list) and len(splitter_sizes) == 2:
            self.splitter.setSizes(splitter_sizes)
        else:
            self.splitter.setSizes([600, 400])  # 預設 6:4
        
        # 初始化下載線程
        self.download_thread = None
        self.video_info = None
        self.downloaded_file_path = None
        
        # 載入最近使用的 URL
        self.load_recent_urls()
        
        # 添加右鍵選單
        self.setup_context_menu()
        
        # 顯示版本資訊
        self.show_version_info()
        
        self.format_id_map = {}
        self.formats = []
    
    def setup_window_geometry(self):
        """設定視窗位置和大小"""
        x, y, width, height = self.preferences.get_window_geometry()
        if x is not None and y is not None:
            self.move(x, y)
        self.resize(width, height)
    
    def setup_context_menu(self):
        """設定右鍵選單"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """顯示右鍵選單"""
        context_menu = QMenu(self)
        
        # 設定選單
        settings_action = QAction("設定", self)
        settings_action.triggered.connect(self.show_settings)
        context_menu.addAction(settings_action)
        
        # 統計資訊選單
        stats_action = QAction("使用統計", self)
        stats_action.triggered.connect(self.show_statistics)
        context_menu.addAction(stats_action)
        
        # 下載歷史選單
        history_action = QAction("下載歷史", self)
        history_action.triggered.connect(self.show_download_history)
        context_menu.addAction(history_action)
        
        # 檢查更新選單
        update_action = QAction("檢查 yt-dlp 更新", self)
        update_action.triggered.connect(self.check_ytdlp_update)
        context_menu.addAction(update_action)
        
        context_menu.addSeparator()
        
        # 重置設定選單
        reset_action = QAction("重置設定", self)
        reset_action.triggered.connect(self.reset_settings)
        context_menu.addAction(reset_action)
        
        context_menu.exec_(self.mapToGlobal(position))
    
    def show_settings(self):
        """顯示設定對話框"""
        QMessageBox.information(self, "設定", "設定功能開發中...")
    
    def show_statistics(self):
        """顯示使用統計"""
        stats = self.preferences.get_statistics()
        stats_text = f"""
使用統計:
總下載次數: {stats['total_downloads']}
成功下載: {stats['successful_downloads']}
失敗下載: {stats['failed_downloads']}
成功率: {stats['success_rate']:.1f}%

最常用格式:
"""
        for format_name, count in stats['favorite_formats']:
            stats_text += f"  {format_name}: {count} 次\n"
        
        QMessageBox.information(self, "使用統計", stats_text)
    
    def show_download_history(self):
        """顯示下載歷史"""
        history = self.preferences.get_download_history()
        if not history:
            QMessageBox.information(self, "下載歷史", "尚無下載記錄")
            return
        
        history_text = "最近下載記錄:\n\n"
        for i, entry in enumerate(history[:10], 1):
            status = "✓" if entry.get('success') else "✗"
            title = entry.get('title', '未知標題')
            format_type = entry.get('format', '未知格式')
            timestamp = entry.get('timestamp', '')[:19]  # 只顯示日期和時間
            history_text += f"{i}. {status} {title}\n   格式: {format_type} | 時間: {timestamp}\n\n"
        
        QMessageBox.information(self, "下載歷史", history_text)
    
    def reset_settings(self):
        """重置設定"""
        reply = QMessageBox.question(self, "確認重置", 
                                   "確定要重置所有設定嗎？此操作無法復原。",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.preferences.reset_to_defaults()
            QMessageBox.information(self, "重置完成", "設定已重置為預設值")
    
    def load_recent_urls(self):
        """載入最近使用的 URL"""
        recent_urls = self.preferences.get_recent_urls()
        self.recent_urls_combo.clear()
        self.recent_urls_combo.addItem("最近使用的 URL")
        for url in recent_urls:
            self.recent_urls_combo.addItem(url)
    
    def on_recent_url_selected(self, url):
        """當選擇最近使用的 URL 時"""
        if url != "最近使用的 URL":
            self.url_input.setText(url)
    
    def on_format_changed(self, text):
        """當格式選擇改變時"""
        if "音訊" in text:
            self.resolution_combo.setEnabled(False)
        else:
            self.resolution_combo.setEnabled(True)
        
        # 記住格式選擇
        self.preferences.set_default_format(text)
    
    def fetch_video_info(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "錯誤", "請輸入 YouTube 影片網址")
            return
        self.fetch_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_output.append("正在獲取影片資訊...")
        import yt_dlp
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'socket_timeout': 30,
                'retries': 3,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                self.formats = formats  # 儲存所有格式供下載用
                resolutions = set()
                self.format_id_map = {}
                
                # 收集所有可用解析度
                for fmt in formats:
                    if fmt.get('vcodec') != 'none' and fmt.get('height'):
                        res = f"{fmt['height']}P"
                        resolutions.add(res)
                        self.format_id_map[res] = fmt['format_id']
                
                # 排序解析度
                resolutions = sorted(resolutions, key=lambda x: int(x.replace('P','')), reverse=True)
                
                # 清空並重新填充解析度下拉選單
                self.resolution_combo.clear()
                self.resolution_combo.addItem("最高品質")
                
                # 添加標準解析度選項
                standard_resolutions = ["1080P (Full HD)", "720P (HD)", "480P", "360P"]
                available_heights = [int(res.replace('P', '')) for res in resolutions]
                
                for res in standard_resolutions:
                    height = int(res.split('P')[0])
                    if any(h >= height for h in available_heights):
                        self.resolution_combo.addItem(res)
                
                # 添加所有實際可用解析度
                for res in resolutions:
                    height = int(res.replace('P', ''))
                    if height > 0:  # 確保有效的解析度
                        self.resolution_combo.addItem(f"{height}P")
                
                # 設定預設選擇
                self.resolution_combo.setCurrentText("最高品質")
                self.log_output.append(f"可用解析度: {', '.join(resolutions)}")
        except Exception as e:
            self.log_output.append(f"❌ 解析影片資訊失敗: {str(e)}")
            QMessageBox.critical(self, "錯誤", f"解析影片資訊失敗: {str(e)}")
        finally:
            self.fetch_button.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def start_download(self):
        try:
            self.fallback_info_label.clear()
            self.fallback_info_label.setVisible(False)
            self.log_output.clear()
            url = self.url_input.text().strip()
            if not url:
                QMessageBox.warning(self, "錯誤", "請輸入 YouTube 影片網址")
                return
                
            # 檢查輸出路徑是否存在
            output_path = self.path_input.text().strip()
            if not os.path.exists(output_path):
                try:
                    os.makedirs(output_path, exist_ok=True)
                    self.log_output.append(f"✓ 已創建輸出資料夾: {output_path}")
                except Exception as e:
                    QMessageBox.warning(self, "錯誤", f"無法創建輸出資料夾: {output_path}\n錯誤: {str(e)}")
                    return
            
            # 如果沒有先獲取資訊，直接使用簡單模式下載
            if not self.format_id_map:
                reply = QMessageBox.question(self, "操作提示", 
                                          "你尚未獲取影片資訊。是否要直接以最佳品質下載？",
                                          QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    self.log_output.append("請先按下『獲取資訊』，再進行下載！")
                    return
                else:
                    self.log_output.append("使用簡單模式下載...")
                    format_choice = self.get_format_choice()
                    resolution_choice = "最高品質"
                    extract_audio_only = "音訊" in format_choice
                    filename_prefix = self.filename_prefix.text().strip()
                    cookies_path = self.cookies_input.text().strip()
                    format_string = "bestvideo+bestaudio/best"  # 使用最高品質
                    self.log_output.append("使用最高品質模式下載")
                    merge_output_format = 'mp4'
                    fallback_to_webm = False
                    
                    self.download_thread = DownloadThread(
                        url,
                        output_path,
                        format_choice,
                        resolution_choice,
                        extract_audio_only,
                        filename_prefix,
                        format_string,
                        merge_output_format,
                        fallback_to_webm,
                        cookies_path
                    )
                    self.download_thread.progress.connect(self.update_progress)
                    self.download_thread.finished.connect(self.download_finished)
                    self.download_button.setEnabled(False)
                    self.stop_button.setEnabled(True)
                    self.progress_bar.setVisible(True)
                    self.download_thread.start()
                    return
            
            format_choice = self.get_format_choice()
            resolution_choice = self.resolution_combo.currentText()
            extract_audio_only = "音訊" in format_choice
            filename_prefix = self.filename_prefix.text().strip()
            cookies_path = self.cookies_input.text().strip()
            format_string = None
            merge_output_format = 'mp4'
            fallback_to_webm = False
            
            # 偵測只有一種流時，自動只下載該流
            video_streams = [f for f in self.formats if f.get('vcodec') != 'none']
            audio_streams = [f for f in self.formats if f.get('acodec') != 'none']
            if not extract_audio_only:
                if len(video_streams) == 1 and not audio_streams:
                    # 只有影像流
                    format_string = video_streams[0]['format_id']
                    merge_output_format = video_streams[0]['ext']
                    self.log_output.append("⚠️ 僅偵測到影像流，將只下載影像檔案。")
                elif len(audio_streams) == 1 and not video_streams:
                    # 只有音訊流
                    format_string = audio_streams[0]['format_id']
                    merge_output_format = audio_streams[0]['ext']
                    self.log_output.append("⚠️ 僅偵測到音訊流，將只下載音訊檔案。")
                else:
                    # 根據解析度選擇格式
                    self.log_output.append(f"選擇的解析度: {resolution_choice}")
                    
                    # 為避免合併問題，改用單一格式下載
                    if resolution_choice == "最高品質":
                        format_string = 'best'  # 使用單一最佳格式
                        self.log_output.append("使用最高品質單一格式 (避免合併問題)")
                    elif "1080P" in resolution_choice:
                        # 嘗試找到1080P的單一格式
                        format_string = 'best[height<=1080]/best'
                        self.log_output.append("使用 1080P 解析度 (單一格式)")
                    elif "720P" in resolution_choice:
                        format_string = 'best[height<=720]/best'
                        self.log_output.append("使用 720P 解析度 (單一格式)")
                    elif "480P" in resolution_choice:
                        format_string = 'best[height<=480]/best'
                        self.log_output.append("使用 480P 解析度 (單一格式)")
                    elif "360P" in resolution_choice:
                        format_string = 'best[height<=360]/best'
                        self.log_output.append("使用 360P 解析度 (單一格式)")
                    elif "P" in resolution_choice:
                        # 處理自定義解析度，例如 "720P"
                        height = resolution_choice.replace("P", "")
                        if height.isdigit():
                            format_string = f'best[height<={height}]/best'
                            self.log_output.append(f"使用 {height}P 解析度 (單一格式)")
                        else:
                            format_string = 'best'
                            self.log_output.append("無法解析解析度，使用最高品質單一格式")
                    else:
                        format_string = 'best'
                        self.log_output.append("使用預設最高品質單一格式")
                    
                    # 添加一個備用選項，如果單一格式失敗，則嘗試分離格式
                    self.log_output.append("如果單一格式失敗，將嘗試分離視頻和音頻流")
                    
                    merge_output_format = 'mp4'
            else:
                format_string = 'bestaudio/best'
            
            self.download_thread = DownloadThread(
                url,
                output_path,
                format_choice,
                resolution_choice,
                extract_audio_only,
                filename_prefix,
                format_string,
                merge_output_format,
                fallback_to_webm,
                cookies_path
            )
            self.download_thread.progress.connect(self.update_progress)
            self.download_thread.finished.connect(self.download_finished)
            self.download_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.download_thread.start()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "下載錯誤", f"下載時發生錯誤：{str(e)}")
    
    def update_progress(self, message):
        """更新進度"""
        # 檢查是否為錯誤訊息，使用紅色顯示
        if any(error_keyword in message for error_keyword in ["失敗", "錯誤", "ERROR", "error", "failed", "❌", "合併視頻和音頻失敗"]):
            self.log_output.append(f'<span style="color: red;">{message}</span>')
        else:
            self.log_output.append(message)
        # 自動滾動到底部
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
    
    def download_finished(self, success, message):
        """下載完成"""
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        if success:
            if "下載完成！檔案名稱:" in message:
                filename = message.split("下載完成！檔案名稱: ")[1]
                download_path = self.path_input.text()
                full_path = os.path.join(download_path, filename)
                completion_message = f"""<span style="color: green;">
✅ 下載完成！

📁 檔案位置: {download_path}
📄 檔案名稱: {filename}
完整路徑: {full_path}

您可以在檔案總管中開啟資料夾查看下載的檔案。
</span>"""
                self.log_output.append(completion_message)
                if self.show_completion_dialog.isChecked():
                    self.show_completion_dialog_with_options(download_path, filename, success=True)
                else:
                    QMessageBox.information(self, "下載完成", f"下載完成！\n\n檔案位置: {download_path}\n檔案名稱: {filename}")
            else:
                self.log_output.append(message)
                if self.show_completion_dialog.isChecked():
                    QMessageBox.information(self, "完成", "下載完成！")
        else:
            self.log_output.append(f'<span style="color: red;">❌ 下載失敗: {message}</span>')
            if self.show_completion_dialog.isChecked():
                self.show_completion_dialog_with_options(self.path_input.text(), "", success=False, fail_message=message)
            else:
                QMessageBox.critical(self, "錯誤", f"下載失敗: {message}")
        url = self.url_input.text().strip()
        title = "未知標題"
        format_choice = self.get_format_choice()
        self.preferences.add_download_history(url, title, format_choice, success)
    
    def closeEvent(self, event: QCloseEvent):
        """關閉視窗時儲存設定"""
        # 儲存視窗位置和大小
        self.preferences.save_window_geometry(
            self.x(), self.y(), self.width(), self.height()
        )
        # 儲存 splitter 分割比例
        self.preferences.set("splitter_sizes", self.splitter.sizes())
        event.accept()

    def show_version_info(self):
        """顯示版本資訊"""
        try:
            import yt_dlp
            yt_dlp_version = yt_dlp.version.__version__
        except:
            yt_dlp_version = "未知"
        
        try:
            import PySide6
            pyside_version = PySide6.__version__
        except:
            pyside_version = "未知"
        
        version_info = f"""
📋 版本資訊:

🎯 應用程式版本: 1.0.0
🔧 yt-dlp 版本: {yt_dlp_version}
🎨 PySide6 版本: {pyside_version}

💡 更新建議:
• 如果下載失敗，請先更新 yt-dlp:
  pip install -U yt-dlp

• 或使用命令列更新:
  yt-dlp -U

• 最新版本請查看:
  https://github.com/yt-dlp/yt-dlp/releases
"""
        self.log_output.append(version_info)
    
    def stop_download(self):
        """停止下載"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()
            self.log_output.append("⚠️ 下載已停止")
            self.download_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.progress_bar.setVisible(False)
    
    def analyze_download_error(self, error_message):
        """分析下載錯誤並提供解決建議"""
        analysis = "🔍 錯誤分析:\n\n"
        
        if "Failed to extract any player response" in error_message:
            analysis += """❌ 問題: yt-dlp 無法解析 YouTube 影片
💡 可能原因:
• yt-dlp 版本過舊
• YouTube 更新了防爬蟲機制
• 網路連線問題

🛠️ 解決方案:
1. 更新 yt-dlp: pip install -U yt-dlp
2. 檢查網路連線
3. 等待 yt-dlp 官方更新
4. 嘗試其他 YouTube 影片
"""
        elif "Video unavailable" in error_message:
            analysis += """❌ 問題: 影片無法使用
💡 可能原因:
• 影片已被刪除或設為私人
• 地區限制
• 年齡限制

🛠️ 解決方案:
1. 檢查影片是否仍可正常播放
2. 嘗試使用 VPN
3. 確認影片沒有年齡限制
"""
        elif "Sign in" in error_message or "login" in error_message:
            analysis += """❌ 問題: 需要登入
💡 可能原因:
• 影片需要登入才能觀看
• 私人影片

🛠️ 解決方案:
1. 確認影片是否為公開影片
2. 嘗試其他公開影片
"""
        elif "network" in error_message.lower() or "connection" in error_message.lower():
            analysis += """❌ 問題: 網路連線問題
💡 可能原因:
• 網路連線不穩定
• 防火牆阻擋
• DNS 問題

🛠️ 解決方案:
1. 檢查網路連線
2. 暫時關閉防火牆
3. 更換 DNS 伺服器
4. 使用 VPN
"""
        else:
            analysis += f"""❌ 未知錯誤: {error_message}
💡 建議:
1. 更新 yt-dlp: pip install -U yt-dlp
2. 檢查網路連線
3. 嘗試其他影片
4. 查看 yt-dlp 官方 issue
"""
        
        return analysis
    
    def on_completion_dialog_changed(self, state):
        """當下載完成提醒設定改變時"""
        self.preferences.set_show_completion_dialog(state == Qt.Checked)
    
    def open_file_directory(self, file_path):
        import subprocess, platform, os, sys
        file_path = os.path.normpath(file_path)
        folder = os.path.dirname(file_path)
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "錯誤", f"找不到檔案：{file_path}")
            self.log_output.append(f"❌ 找不到檔案：{file_path}")
            return
        try:
            if platform.system() == "Windows":
                try:
                    subprocess.run(['explorer', '/select,', file_path], check=True)
                except Exception:
                    try:
                        # fallback: 只開啟資料夾
                        subprocess.run(['explorer', os.path.abspath(folder)], check=True)
                    except Exception:
                        try:
                            # 最後 fallback: os.startfile
                            os.startfile(os.path.abspath(folder))
                        except Exception as e:
                            self.log_output.append(f"❌ 開啟檔案目錄失敗: {str(e)}")
                            QMessageBox.warning(self, "錯誤", f"開啟檔案目錄失敗: {str(e)}\n請手動到以下路徑尋找檔案：\n{os.path.abspath(folder)}")
                            return
                    QMessageBox.information(self, "提示", f"已開啟資料夾（但無法自動選取檔案），請手動尋找。\n路徑：{os.path.abspath(folder)}")
            elif platform.system() == "Darwin":
                subprocess.run(['open', '-R', file_path], check=True)
            else:
                subprocess.run(['xdg-open', folder], check=True)
            self.log_output.append(f"<span style=\"color: green;\">✅ 已開啟檔案目錄: {folder}</span>")
        except Exception as e:
            self.log_output.append(f"❌ 開啟檔案目錄失敗: {str(e)}")
            QMessageBox.warning(self, "錯誤", f"開啟檔案目錄失敗: {str(e)}\n請手動到以下路徑尋找檔案：\n{os.path.abspath(folder)}")
    
    def show_completion_dialog_with_options(self, download_path, filename, success=True, fail_message=None):
        """顯示下載完成對話框，包含開啟目錄選項"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        dialog = QDialog(self)
        dialog.setWindowTitle("下載完成" if success else "下載失敗")
        dialog.setModal(True)
        dialog.setFixedSize(400, 200)
        dialog.setStyleSheet("""
            QDialog { background-color: #f0f0f0; }
            QLabel { font-size: 12px; margin: 5px; }
            QPushButton { font-size: 12px; padding: 8px 16px; margin: 5px; border: 1px solid #ccc; border-radius: 4px; }
            QPushButton:hover { background-color: #e0e0e0; }
            QPushButton#openFolder { background-color: #4CAF50; color: white; border-color: #45a049; }
            QPushButton#openFolder:hover { background-color: #45a049; }
            QPushButton#close { background-color: #f44336; color: white; border-color: #da190b; }
            QPushButton#close:hover { background-color: #da190b; }
        """)
        layout = QVBoxLayout(dialog)
        if success:
            success_label = QLabel("✅ 下載完成！")
            success_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin: 10px;")
            layout.addWidget(success_label)
            info_label = QLabel(f"檔案位置: {download_path}\n檔案名稱: {filename}")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)
        else:
            fail_label = QLabel("❌ 下載失敗！")
            fail_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f44336; margin: 10px;")
            layout.addWidget(fail_label)
            info_label = QLabel(fail_message or "下載失敗，請檢查網路或影片狀態")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)
        button_layout = QHBoxLayout()
        if success:
            open_folder_button = QPushButton("開啟檔案目錄")
            open_folder_button.setObjectName("openFolder")
            open_folder_button.clicked.connect(lambda: self.open_file_directory(os.path.join(download_path, filename)))
            open_folder_button.clicked.connect(dialog.accept)
            button_layout.addWidget(open_folder_button)
        close_button = QPushButton("關閉")
        close_button.setObjectName("close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        dialog.exec_()

    def on_filename_prefix_changed(self, text):
        """當檔案名稱前綴變更時"""
        self.preferences.set_filename_prefix(text)
    
    def load_prefix_history(self):
        """載入前綴歷史"""
        self.prefix_history_combo.clear()
        self.prefix_history_combo.addItem("▼")  # 下拉指示符號
        
        # 添加歷史前綴
        prefix_history = self.preferences.get_prefix_history()
        if prefix_history:
            self.prefix_history_combo.addItems(prefix_history)
            # 添加刪除選項
            self.prefix_history_combo.addItem("刪除...")
    
    def on_prefix_history_selected(self, text):
        """當選擇歷史前綴時"""
        if not text or text == "▼":
            # 重置選擇
            self.prefix_history_combo.setCurrentIndex(0)
            return
            
        if text == "刪除...":
            # 顯示刪除對話框
            self.show_prefix_delete_dialog()
            # 重置選擇
            self.prefix_history_combo.setCurrentIndex(0)
            return
            
        # 設置所選前綴到輸入框
        self.filename_prefix.setText(text)
        # 重置選擇
        self.prefix_history_combo.setCurrentIndex(0)
    
    def show_prefix_delete_dialog(self):
        """顯示前綴刪除對話框"""
        prefix_history = self.preferences.get_prefix_history()
        if not prefix_history:
            QMessageBox.information(self, "前綴歷史", "沒有可刪除的前綴歷史")
            return
            
        # 創建對話框
        dialog = QDialog(self)
        dialog.setWindowTitle("刪除前綴歷史")
        dialog.setMinimumWidth(300)
        
        # 創建佈局
        layout = QVBoxLayout(dialog)
        
        # 添加說明
        layout.addWidget(QLabel("選擇要刪除的前綴:"))
        
        # 添加前綴列表
        prefix_list = QListWidget()
        prefix_list.addItems(prefix_history)
        layout.addWidget(prefix_list)
        
        # 添加按鈕
        button_layout = QHBoxLayout()
        delete_button = QPushButton("刪除")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(delete_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # 連接按鈕事件
        delete_button.clicked.connect(lambda: self.delete_prefix(prefix_list.currentItem().text(), dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        # 顯示對話框
        dialog.exec()
    
    def delete_prefix(self, prefix, dialog):
        """刪除前綴"""
        if prefix:
            self.preferences.remove_prefix_history(prefix)
            # 重新載入前綴歷史
            self.load_prefix_history()
            dialog.accept()

    def get_format_choice(self):
        if self.radio_video.isChecked():
            return "影片"
        elif self.radio_audio_mp3.isChecked():
            return "僅音訊 (MP3)"
        elif self.radio_audio_wav.isChecked():
            return "僅音訊 (WAV)"
        return "影片"

    def browse_path(self):
        """瀏覽下載路徑"""
        folder = QFileDialog.getExistingDirectory(self, "選擇下載資料夾")
        if folder:
            self.path_input.setText(folder)
            # 記住下載路徑
            self.preferences.set_download_path(folder)

    def browse_cookies(self):
        file, _ = QFileDialog.getOpenFileName(self, "選擇 cookies.txt", "", "Cookies (*.txt)")
        if file:
            self.cookies_input.setText(file)
    
    def increase_log_font_size(self):
        """增加日誌文字大小"""
        if self.current_font_size < 20:  # 設置最大字體大小限制
            self.current_font_size += 1
            self.log_output.setStyleSheet(f"font-size: {self.current_font_size}pt;")
            # 保存到用戶偏好
            self.preferences.set("log_font_size", self.current_font_size)
    
    def decrease_log_font_size(self):
        """減小日誌文字大小"""
        if self.current_font_size > 8:  # 設置最小字體大小限制
            self.current_font_size -= 1
            self.log_output.setStyleSheet(f"font-size: {self.current_font_size}pt;")
            # 保存到用戶偏好
            self.preferences.set("log_font_size", self.current_font_size)

    def check_ytdlp_update(self):
        """檢查 yt-dlp 更新"""
        self.log_output.append("正在檢查 yt-dlp 更新...")
        
        # 在背景線程中檢查更新
        def check_thread():
            try:
                import pkg_resources
                import urllib.request
                import json
                
                # 獲取當前版本
                try:
                    current_version = pkg_resources.get_distribution("yt-dlp").version
                    self.log_output.append(f"當前 yt-dlp 版本: {current_version}")
                except pkg_resources.DistributionNotFound:
                    self.log_output.append("❌ yt-dlp 未安裝")
                    return
                
                # 檢查網絡連接
                try:
                    urllib.request.urlopen("https://pypi.org/pypi/yt-dlp/json", timeout=3)
                except:
                    self.log_output.append("❌ 無法連接到網絡，跳過版本檢查")
                    return
                
                # 獲取最新版本
                try:
                    with urllib.request.urlopen("https://pypi.org/pypi/yt-dlp/json") as response:
                        data = json.loads(response.read().decode())
                        latest_version = data["info"]["version"]
                        self.log_output.append(f"最新 yt-dlp 版本: {latest_version}")
                        
                        # 比較版本
                        if latest_version != current_version:
                            # 在主線程中顯示對話框
                            from PySide6.QtCore import QMetaObject, Qt, Q_ARG
                            QMetaObject.invokeMethod(
                                self, 
                                "show_update_confirm_dialog", 
                                Qt.QueuedConnection,
                                Q_ARG(str, latest_version),
                                Q_ARG(str, current_version)
                            )
                        else:
                            self.log_output.append("✅ yt-dlp 已是最新版本")
                except Exception as e:
                    self.log_output.append(f"❌ 檢查版本時出錯: {e}")
            
            except Exception as e:
                self.log_output.append(f"❌ 版本檢查過程中出錯: {e}")
        
        # 啟動檢查線程
        import threading
        threading.Thread(target=check_thread).start()

    def check_and_update_ytdlp(self):
        """檢查並自動更新 yt-dlp"""
        self.log_output.append("正在檢查並自動更新 yt-dlp...")
        
        # 在背景線程中檢查並更新
        def check_update_thread():
            try:
                import pkg_resources
                import urllib.request
                import json
                import subprocess
                import sys
                from PySide6.QtCore import QTimer
                
                # 獲取當前版本
                try:
                    current_version = pkg_resources.get_distribution("yt-dlp").version
                    self.log_output.append(f"當前 yt-dlp 版本: {current_version}")
                except pkg_resources.DistributionNotFound:
                    self.log_output.append("❌ yt-dlp 未安裝")
                    # 嘗試安裝
                    self.log_output.append("正在安裝 yt-dlp...")
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
                        self.log_output.append("✅ yt-dlp 安裝成功")
                    except Exception as e:
                        self.log_output.append(f"❌ yt-dlp 安裝失敗: {e}")
                    return
                
                # 檢查網絡連接
                try:
                    urllib.request.urlopen("https://pypi.org/pypi/yt-dlp/json", timeout=3)
                except:
                    self.log_output.append("❌ 無法連接到網絡，跳過更新")
                    return
                
                # 獲取最新版本
                try:
                    with urllib.request.urlopen("https://pypi.org/pypi/yt-dlp/json") as response:
                        data = json.loads(response.read().decode())
                        latest_version = data["info"]["version"]
                        self.log_output.append(f"最新 yt-dlp 版本: {latest_version}")
                        
                        # 比較版本
                        if latest_version != current_version:
                            self.log_output.append(f"發現新版本，正在更新 yt-dlp 從 {current_version} 到 {latest_version}...")
                            
                            # 自動更新
                            try:
                                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
                                self.log_output.append(f"✅ yt-dlp 已成功更新到版本 {latest_version}")
                                
                                # 顯示成功訊息
                                QTimer.singleShot(0, lambda: QMessageBox.information(self, "更新成功", f"yt-dlp 已成功更新到版本 {latest_version}"))
                            except Exception as e:
                                self.log_output.append(f"❌ yt-dlp 更新失敗: {e}")
                                
                                # 顯示失敗訊息
                                QTimer.singleShot(0, lambda: QMessageBox.warning(self, "更新失敗", f"yt-dlp 更新失敗: {e}"))
                        else:
                            self.log_output.append("✅ yt-dlp 已是最新版本")
                            
                            # 顯示已是最新版本訊息
                            QTimer.singleShot(0, lambda: QMessageBox.information(self, "版本檢查", f"yt-dlp 已是最新版本 ({current_version})"))
                except Exception as e:
                    self.log_output.append(f"❌ 檢查版本時出錯: {e}")
            
            except Exception as e:
                self.log_output.append(f"❌ 更新過程中出錯: {e}")
        
        # 啟動檢查更新線程
        import threading
        threading.Thread(target=check_update_thread).start()
    
    def show_update_confirm_dialog(self, latest_version, current_version):
        """顯示更新確認對話框"""
        from PySide6.QtWidgets import QMessageBox
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("yt-dlp 更新")
        msg_box.setText(f"發現 yt-dlp 新版本: {latest_version}\n當前版本: {current_version}\n是否要更新？")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        
        if msg_box.exec() == QMessageBox.Yes:
            self.update_ytdlp(latest_version)
    
    def update_ytdlp(self, latest_version):
        """更新 yt-dlp"""
        self.log_output.append("正在更新 yt-dlp，請稍候...")
        
        # 使用線程避免凍結UI
        def update_thread():
            import subprocess
            import sys
            
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_output.append(f"✅ yt-dlp 已成功更新到版本 {latest_version}")
                    self.log_output.append("更新完成，重新啟動應用程式後生效")
                else:
                    self.log_output.append(f"❌ yt-dlp 更新失敗")
                    self.log_output.append(f"錯誤信息: {result.stderr}")
            except Exception as e:
                self.log_output.append(f"❌ 更新過程中出錯: {str(e)}")
        
        # 啟動更新線程
        import threading
        threading.Thread(target=update_thread).start()
    
 