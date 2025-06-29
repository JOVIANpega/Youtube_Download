from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, 
                             QProgressBar, QComboBox, QFileDialog, QMessageBox,
                             QGroupBox, QGridLayout, QCheckBox, QMenu, QRadioButton, QButtonGroup, QSplitter, QListWidget, QTextBrowser)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QCloseEvent, QAction
import yt_dlp
import os
import ssl
import sys
import re
import time
import subprocess
import platform
import shutil
import zipfile
import urllib.request
import threading
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_preferences import UserPreferences

# 新增 FFmpeg 下載和管理功能
def get_ffmpeg_dir():
    """獲取 FFmpeg 存放目錄"""
    # 在應用程式目錄下創建 ffmpeg_bin 資料夾
    if hasattr(sys, '_MEIPASS'):  # PyInstaller 打包後的路徑
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    ffmpeg_dir = os.path.join(base_dir, "ffmpeg_bin")
    os.makedirs(ffmpeg_dir, exist_ok=True)
    return ffmpeg_dir

def get_ffmpeg_path():
    """獲取 FFmpeg 可執行檔案路徑"""
    ffmpeg_dir = get_ffmpeg_dir()
    
    # 根據作業系統確定 FFmpeg 檔案名稱
    if platform.system() == "Windows":
        ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    else:
        ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg")
    
    return ffmpeg_path

def is_ffmpeg_downloaded():
    """檢查 FFmpeg 是否已下載"""
    ffmpeg_path = get_ffmpeg_path()
    return os.path.exists(ffmpeg_path) and os.path.getsize(ffmpeg_path) > 1000000  # 確保檔案大小合理

def download_ffmpeg(progress_callback=None):
    """下載 FFmpeg 並解壓到指定目錄"""
    ffmpeg_dir = get_ffmpeg_dir()
    ffmpeg_path = get_ffmpeg_path()
    
    # 如果已經下載，則不重複下載
    if is_ffmpeg_downloaded():
        if progress_callback:
            progress_callback("FFmpeg 已存在，無需重複下載")
        return ffmpeg_path
    
    if progress_callback:
        progress_callback("正在下載 FFmpeg...")
    
    # 根據作業系統選擇下載連結
    if platform.system() == "Windows":
        # Windows 版本 (選擇體積較小的 essentials 版本)
        url = "https://github.com/GyanD/codexffmpeg/releases/download/6.1.1/ffmpeg-6.1.1-essentials_build.zip"
        zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
        
        # 下載 FFmpeg
        try:
            if progress_callback:
                progress_callback("下載 FFmpeg 中，請稍候...")
            
            # 使用 urllib 下載檔案
            urllib.request.urlretrieve(url, zip_path)
            
            if progress_callback:
                progress_callback("FFmpeg 下載完成，正在解壓...")
            
            # 解壓縮檔案
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(ffmpeg_dir)
            
            # 找到解壓後的 ffmpeg.exe 路徑
            extracted_dir = None
            for item in os.listdir(ffmpeg_dir):
                if os.path.isdir(os.path.join(ffmpeg_dir, item)) and "ffmpeg" in item.lower():
                    extracted_dir = os.path.join(ffmpeg_dir, item)
                    break
            
            if extracted_dir:
                # 移動 ffmpeg.exe 到根目錄
                bin_dir = os.path.join(extracted_dir, "bin")
                if os.path.exists(bin_dir):
                    for file in os.listdir(bin_dir):
                        if file.lower() in ["ffmpeg.exe", "ffprobe.exe"]:
                            src = os.path.join(bin_dir, file)
                            dst = os.path.join(ffmpeg_dir, file)
                            shutil.copy2(src, dst)
                
                # 清理解壓目錄
                shutil.rmtree(extracted_dir)
            
            # 刪除 zip 檔
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            if progress_callback:
                progress_callback("FFmpeg 設置完成")
            
            return ffmpeg_path
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"下載 FFmpeg 失敗: {str(e)}")
            return None
    else:
        # Linux/macOS 版本 - 建議使用系統包管理器安裝
        if progress_callback:
            progress_callback("非 Windows 系統請使用系統包管理器安裝 FFmpeg")
        return None

def test_ffmpeg(ffmpeg_path):
    """測試 FFmpeg 是否可用"""
    try:
        result = subprocess.run([ffmpeg_path, "-version"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)

def find_ffmpeg_executable():
    """尋找 FFmpeg 可執行文件路徑，優先使用下載的版本"""
    # 檢查是否有下載的 FFmpeg
    ffmpeg_path = get_ffmpeg_path()
    if is_ffmpeg_downloaded():
        is_working, _ = test_ffmpeg(ffmpeg_path)
        if is_working:
            return ffmpeg_path
    
    # 如果下載的版本不可用，嘗試系統路徑
    try:
        # 先嘗試直接執行 ffmpeg 命令
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # 確認 ffmpeg 命令確實可用
            return 'ffmpeg'  # 在 PATH 中找到
    except:
        pass
    
    # 嘗試在常見位置查找
    system = platform.system().lower()
    possible_paths = []
    
    if system == 'windows':
        possible_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Programs\ffmpeg\bin\ffmpeg.exe'),
            os.path.join(os.environ.get('APPDATA', ''), r'ffmpeg\bin\ffmpeg.exe')
        ]
    elif system == 'darwin':  # macOS
        possible_paths = [
            '/usr/local/bin/ffmpeg',
            '/usr/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg'
        ]
    else:  # Linux
        possible_paths = [
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            '/opt/ffmpeg/bin/ffmpeg'
        ]
    
    # 檢查可能的路徑
    for path in possible_paths:
        if os.path.isfile(path):
            try:
                result = subprocess.run([path, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                pass
    
    return None  # 未找到 FFmpeg

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
    
    def cleanup_fragment_files(self, base_filename):
        """清理下載過程中產生的碎片文件"""
        import glob
        import os
        
        # 查找所有可能的碎片文件
        pattern = os.path.join(self.output_path, f"{base_filename}.*")
        all_files = glob.glob(pattern)
        
        # 找出主要文件（通常是最大的文件）
        main_file = None
        main_size = 0
        for f in all_files:
            try:
                size = os.path.getsize(f)
                if size > main_size:
                    main_size = size
                    main_file = f
            except:
                pass
        
        if not main_file:
            return
        
        # 刪除所有碎片文件，保留主文件
        for f in all_files:
            if f != main_file:
                # 檢查文件名是否包含碎片標識
                basename = os.path.basename(f)
                if any(marker in basename for marker in ['.f', '.part', '.temp', '.tmp', '.webm', '.m4a']) or '.part' in basename:
                    try:
                        os.remove(f)
                        self.progress.emit(f"<span style=\"color: orange;\">🗑️ 已刪除碎片檔案: {os.path.basename(f)}</span>")
                    except:
                        pass
    
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
                'keepvideo': True,  # 保留部分下載的視頻檔案
                'nopart': False,    # 允許部分下載
                'abort_on_error': False,  # 不因錯誤中止
            }
            
            # 檢查並設置 FFmpeg 路徑
            # 優先使用下載的 FFmpeg
            if is_ffmpeg_downloaded():
                ffmpeg_path = get_ffmpeg_path()
                is_working, _ = test_ffmpeg(ffmpeg_path)
                if is_working:
                    self.progress.emit(f"<span style=\"color: green;\">✓ 使用下載的 FFmpeg: {ffmpeg_path}</span>")
                    ydl_opts['ffmpeg_location'] = ffmpeg_path
                else:
                    self.progress.emit("<span style=\"color: orange;\">⚠️ 下載的 FFmpeg 無法使用，嘗試尋找系統安裝的版本</span>")
                    ffmpeg_path = find_ffmpeg_executable()
                    if ffmpeg_path:
                        self.progress.emit(f"<span style=\"color: green;\">✓ 已找到系統 FFmpeg: {ffmpeg_path}</span>")
                        ydl_opts['ffmpeg_location'] = ffmpeg_path
                    else:
                        self.progress.emit("<span style=\"color: orange;\">⚠️ 未找到 FFmpeg，將使用單一格式下載</span>")
            else:
                # 如果沒有下載的版本，嘗試尋找系統安裝的版本
                ffmpeg_path = find_ffmpeg_executable()
                if ffmpeg_path:
                    self.progress.emit(f"<span style=\"color: green;\">✓ 已找到系統 FFmpeg: {ffmpeg_path}</span>")
                    ydl_opts['ffmpeg_location'] = ffmpeg_path
                else:
                    self.progress.emit("<span style=\"color: orange;\">⚠️ 未找到 FFmpeg，將使用單一格式下載</span>")
            
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
                    'keepvideo': True,  # 保留部分下載的視頻檔案
                    'nopart': False,    # 允許部分下載
                    'abort_on_error': False,  # 不因錯誤中止
                }
                
                # 設置 FFmpeg 路徑
                if ffmpeg_path:
                    download_opts['ffmpeg_location'] = ffmpeg_path
                
                if self.extract_audio_only:
                    download_opts['format'] = 'bestaudio/best'
                    download_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3' if self.format_choice == "僅音訊 (MP3)" else 'wav',
                        'preferredquality': '192',
                    }]
                else:
                    # 根據是否有 FFmpeg 決定下載策略
                    if ffmpeg_path:
                        # 有 FFmpeg，嘗試使用分離流
                        if self.resolution_choice == "最高品質":
                            # 優先使用分離流以獲得最高品質
                            download_opts['format'] = 'bestvideo+bestaudio/best'
                            self.progress.emit("使用最高品質模式 (分離視頻和音頻流)")
                        elif self.resolution_choice == "1080P (Full HD)" and any(fmt.get('height') == 1080 for fmt in self.formats):
                            # 使用高品質的1080P分離流
                            download_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                            self.progress.emit("使用 1080P 解析度 (分離視頻和音頻流)")
                        elif self.resolution_choice == "720P (HD)" and any(fmt.get('height') == 720 for fmt in self.formats):
                            # 使用高品質的720P分離流
                            download_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                            self.progress.emit("使用 720P 解析度 (分離視頻和音頻流)")
                        else:
                            # 預設使用最佳可用格式
                            download_opts['format'] = 'bestvideo+bestaudio/best'
                            self.progress.emit("使用預設最佳解析度 (分離視頻和音頻流)")
                    else:
                        # 沒有 FFmpeg，直接使用單一格式
                        if self.resolution_choice == "最高品質":
                            download_opts['format'] = 'best'
                            self.progress.emit("使用最高品質模式 (單一格式)")
                        elif self.resolution_choice == "1080P (Full HD)":
                            download_opts['format'] = 'best[height<=1080]'
                            self.progress.emit("使用 1080P 解析度 (單一格式)")
                        elif self.resolution_choice == "720P (HD)":
                            download_opts['format'] = 'best[height<=720]'
                            self.progress.emit("使用 720P 解析度 (單一格式)")
                        else:
                            download_opts['format'] = 'best'
                            self.progress.emit("使用預設最佳解析度 (單一格式)")
                    
                                    # 設置合併格式，優先使用 mp4
                    download_opts['merge_output_format'] = self.merge_output_format
                    
                    # 添加更穩定的 FFmpeg 參數
                    if ffmpeg_path:
                        download_opts['postprocessor_args'] = [
                            '-c:v', 'copy',
                            '-c:a', 'aac',  # 使用 AAC 音頻編碼，更兼容
                            '-strict', 'experimental',
                            '-movflags', '+faststart',  # 優化 MP4 檔案結構
                            '-max_muxing_queue_size', '9999'  # 增加隊列大小，避免合併錯誤
                        ]
                        
                        # 設置更多選項以提高穩定性
                        download_opts['external_downloader_args'] = {
                            'ffmpeg': ['-hide_banner', '-loglevel', 'warning']
                        }
                    
                    # 禁用部分後處理，以便在合併失敗時保留原始檔案
                    download_opts['keepvideo'] = True  # 保留原始視頻檔案
                    download_opts['keep_fragments'] = True  # 保留所有下載的片段
                
                self.progress.emit(f"開始下載: {video_title} ({download_opts['format']})")
                
                try:
                    # 保存原始下載目錄內容，用於比較
                    import glob
                    import time
                    before_files = set(glob.glob(os.path.join(self.output_path, "*")))
                    
                    # 嘗試下載
                    try:
                        with yt_dlp.YoutubeDL(download_opts) as ydl:
                            ydl.download([self.url])
                    except Exception as e:
                        # 捕獲下載錯誤，但繼續檢查是否有部分檔案下載
                        self.progress.emit(f"<span style=\"color: orange;\">⚠️ 下載過程中出現錯誤: {str(e)}</span>")
                        
                        # 檢查是否有 FFmpeg 相關錯誤
                        if "ffmpeg" in str(e).lower():
                            self.progress.emit("<span style=\"color: orange;\">⚠️ 檢測到 FFmpeg 相關錯誤，嘗試直接下載分離的視頻和音頻檔案...</span>")
                            
                            # 等待一下確保文件寫入完成
                            time.sleep(1)
                            
                            # 先嘗試直接下載視頻部分
                            self.progress.emit("<span style=\"color: blue;\">ℹ️ 嘗試下載高畫質視頻檔案...</span>")
                            video_opts = download_opts.copy()
                            video_opts['format'] = 'bestvideo/best'
                            video_opts['postprocessor_args'] = []
                            
                            try:
                                with yt_dlp.YoutubeDL(video_opts) as ydl:
                                    ydl.download([self.url])
                                
                                # 檢查下載目錄中的新檔案
                                after_files = set(glob.glob(os.path.join(self.output_path, "*")))
                                new_files = list(after_files - before_files)
                                
                                # 顯示所有新檔案
                                if new_files:
                                    self.progress.emit("<span style=\"color: blue;\">ℹ️ 找到新下載的檔案：</span>")
                                    for f in new_files:
                                        file_size = os.path.getsize(f) / (1024 * 1024)  # 轉換為 MB
                                        self.progress.emit(f"<span style=\"color: blue;\">- {os.path.basename(f)} ({file_size:.1f} MB)</span>")
                                
                                # 找出最大的檔案（可能是高畫質視頻）
                                best_file = max(new_files, key=os.path.getsize)
                                best_filename = os.path.basename(best_file)
                                best_filesize = os.path.getsize(best_file) / (1024 * 1024)
                                
                                self.progress.emit(f"<span style=\"color: green;\">✅ 成功下載高畫質視頻: {best_filename} ({best_filesize:.1f} MB)</span>")
                                self.finished.emit(True, f"下載完成！保留高畫質視頻檔案: {best_filename}")
                                return
                            except Exception as e2:
                                self.progress.emit(f"<span style=\"color: red;\">❌ 高畫質視頻下載失敗: {str(e2)}</span>")
                            
                            # 檢查下載目錄中的新檔案
                            after_files = set(glob.glob(os.path.join(self.output_path, "*")))
                            new_files = list(after_files - before_files)
                            
                            # 顯示所有新檔案
                            if new_files:
                                self.progress.emit("<span style=\"color: blue;\">ℹ️ 找到新下載的檔案：</span>")
                                for f in new_files:
                                    file_size = os.path.getsize(f) / (1024 * 1024)  # 轉換為 MB
                                    self.progress.emit(f"<span style=\"color: blue;\">- {os.path.basename(f)} ({file_size:.1f} MB)</span>")
                            
                            # 找到與影片標題相關的檔案
                            video_files = []
                            audio_files = []
                            
                            for f in new_files:
                                basename = os.path.basename(f).lower()
                                # 判斷是視頻還是音頻
                                if ("video" in basename or 
                                    os.path.splitext(basename)[1] in ['.mp4', '.webm', '.mkv', '.avi', '.flv', '.mov']):
                                    video_files.append(f)
                                elif ("audio" in basename or 
                                      os.path.splitext(basename)[1] in ['.m4a', '.mp3', '.ogg', '.wav', '.aac']):
                                    audio_files.append(f)
                                else:
                                    # 如果無法判斷，根據檔案大小猜測
                                    if os.path.getsize(f) > 5 * 1024 * 1024:  # 大於 5MB 可能是視頻
                                        video_files.append(f)
                                    else:
                                        audio_files.append(f)
                            
                            # 顯示找到的檔案
                            if video_files:
                                self.progress.emit("<span style=\"color: green;\">✅ 已找到視頻檔案：</span>")
                                for i, file in enumerate(video_files):
                                    file_size = os.path.getsize(file) / (1024 * 1024)  # 轉換為 MB
                                    file_name = os.path.basename(file)
                                    self.progress.emit(f"<span style=\"color: green;\">{i+1}. {file_name} ({file_size:.1f} MB)</span>")
                            
                            if audio_files:
                                self.progress.emit("<span style=\"color: blue;\">ℹ️ 已找到音頻檔案：</span>")
                                for i, file in enumerate(audio_files):
                                    file_size = os.path.getsize(file) / (1024 * 1024)  # 轉換為 MB
                                    file_name = os.path.basename(file)
                                    self.progress.emit(f"<span style=\"color: blue;\">{i+1}. {file_name} ({file_size:.1f} MB)</span>")
                            
                            # 如果找到視頻檔案，保留視頻檔案並刪除音頻檔案
                            if video_files:
                                # 找出最大的視頻檔案（可能是最高畫質）
                                best_video = max(video_files, key=os.path.getsize)
                                best_video_name = os.path.basename(best_video)
                                best_video_size = os.path.getsize(best_video) / (1024 * 1024)
                                
                                self.progress.emit(f"<span style=\"color: green;\">✅ 保留最高畫質視頻檔案: {best_video_name} ({best_video_size:.1f} MB)</span>")
                                
                                # 刪除其他視頻檔案
                                for file in video_files:
                                    if file != best_video:
                                        try:
                                            os.remove(file)
                                            self.progress.emit(f"<span style=\"color: orange;\">🗑️ 已刪除多餘視頻檔案: {os.path.basename(file)}</span>")
                                        except:
                                            pass
                                
                                # 刪除所有音頻檔案
                                for file in audio_files:
                                    try:
                                        os.remove(file)
                                        self.progress.emit(f"<span style=\"color: orange;\">🗑️ 已刪除音頻檔案: {os.path.basename(file)}</span>")
                                    except:
                                        pass
                                
                                # 清理可能的碎片文件
                                self.cleanup_fragment_files(safe_title)
                                
                                # 返回成功訊息
                                self.finished.emit(True, f"下載完成！保留高畫質視頻檔案: {best_video_name}")
                                return
                            else:
                                # 如果找不到視頻檔案，但有音頻檔案，保留最大的音頻檔案
                                if audio_files:
                                    best_audio = max(audio_files, key=os.path.getsize)
                                    best_audio_name = os.path.basename(best_audio)
                                    best_audio_size = os.path.getsize(best_audio) / (1024 * 1024)
                                    
                                    self.progress.emit(f"<span style=\"color: blue;\">ℹ️ 只找到音頻檔案，保留最高品質音頻: {best_audio_name} ({best_audio_size:.1f} MB)</span>")
                                    
                                    # 刪除其他音頻檔案
                                    for file in audio_files:
                                        if file != best_audio:
                                            try:
                                                os.remove(file)
                                                self.progress.emit(f"<span style=\"color: orange;\">🗑️ 已刪除多餘音頻檔案: {os.path.basename(file)}</span>")
                                            except:
                                                pass
                                    
                                    # 返回成功訊息
                                    self.finished.emit(True, f"下載完成！保留音頻檔案: {best_audio_name}")
                                    return
                            
                            # 如果找不到相關檔案，繼續執行備用下載方案
                            self.progress.emit("<span style=\"color: orange;\">⚠️ 找不到已下載的檔案，嘗試使用單一格式下載...</span>")
                            
                            # 使用單一格式下載
                            download_opts['format'] = '22/18/best'  # 優先使用 YouTube 標準格式 (22=720p MP4, 18=360p MP4)
                            download_opts.pop('postprocessor_args', None)  # 移除 FFmpeg 參數
                            download_opts['keepvideo'] = False  # 不需要保留原始視頻
                            
                            try:
                                with yt_dlp.YoutubeDL(download_opts) as ydl:
                                    ydl.download([self.url])
                                self.progress.emit("<span style=\"color: green;\">✅ 使用單一格式下載成功</span>")
                                
                                # 檢查下載目錄中的新檔案
                                after_files = set(glob.glob(os.path.join(self.output_path, "*")))
                                new_files = list(after_files - before_files)
                                
                                if new_files:
                                    # 找到最新下載的檔案
                                    latest_file = max(new_files, key=os.path.getmtime)
                                    latest_filename = os.path.basename(latest_file)
                                    file_size = os.path.getsize(latest_file) / (1024 * 1024)  # 轉換為 MB
                                    
                                    self.progress.emit(f"<span style=\"color: green;\">✅ 下載成功: {latest_filename} ({file_size:.1f} MB)</span>")
                                    self.finished.emit(True, f"下載完成！檔案名稱: {latest_filename}")
                                    return
                                else:
                                    self.progress.emit("<span style=\"color: orange;\">⚠️ 找不到下載的檔案，嘗試啟動備用下載...</span>")
                                    self.finished.emit(True, "START_FALLBACK")
                                    return
                            except Exception as e2:
                                self.progress.emit(f"<span style=\"color: red;\">單一格式下載失敗: {str(e2)}</span>")
                                self.finished.emit(True, "START_FALLBACK")
                                return
                    
                    # 檢查下載結果
                    ext = self.merge_output_format if not self.extract_audio_only else ('mp3' if self.format_choice == "僅音訊 (MP3)" else 'wav')
                    final_filename = f"{safe_title}.{ext}"
                    final_path = os.path.join(self.output_path, final_filename)
                    
                    if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                        # 找出並刪除所有碎片文件
                        self.cleanup_fragment_files(safe_title)
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
                            # 找出最大的文件（可能是完整的影片）
                            main_file = max(files, key=os.path.getsize)
                            actual_filename = os.path.basename(main_file)
                            
                            # 清理其他碎片文件
                            for f in files:
                                if f != main_file and os.path.basename(f).startswith(safe_title):
                                    try:
                                        os.remove(f)
                                        self.progress.emit(f"<span style=\"color: orange;\">🗑️ 已刪除碎片檔案: {os.path.basename(f)}</span>")
                                    except:
                                        pass
                            
                            self.progress.emit(f"<span style=\"color: green;\">✅ 已下載檔案：{actual_filename}</span>")
                            self.finished.emit(True, f"下載完成！檔案名稱: {actual_filename}")
                        else:
                            self.finished.emit(False, "下載失敗：檔案不存在或大小為0，可能是影片受限、已刪除或無法下載。建議升級 yt-dlp 或用 cookies。")
                
                except Exception as e:
                    self.progress.emit(f"<span style=\"color: red;\">下載失敗: {str(e)}</span>")
                    
                    # 檢查是否是合併錯誤或 FFmpeg 相關錯誤
                    if "Postprocessing" in str(e) or "Could not write header" in str(e) or "ffmpeg is not installed" in str(e) or "ffmpeg" in str(e).lower():
                        self.progress.emit("<span style=\"color: orange;\">⚠️ 合併視頻和音頻失敗，保留高畫質視頻檔案...</span>")
                        
                        # 查找已下載的檔案
                        import glob, time
                        
                        # 先等待 1 秒，確保檔案寫入完成
                        time.sleep(1)
                        
                        # 搜尋所有可能的檔案
                        pattern1 = os.path.join(self.output_path, f"{safe_title}.*")
                        pattern2 = os.path.join(self.output_path, f"*{safe_title.split(' ')[0]}*")  # 使用標題的第一個單詞
                        
                        files1 = [f for f in glob.glob(pattern1) if os.path.getsize(f) > 0]
                        files2 = [f for f in glob.glob(pattern2) if os.path.getsize(f) > 0]
                        
                        # 合併檔案列表並去重
                        all_files = list(set(files1 + files2))
                        
                        # 篩選出視頻檔案和音頻檔案
                        video_files = []
                        audio_files = []
                        
                        for file in all_files:
                            file_ext = os.path.splitext(file)[1].lower()
                            # 檢查檔案名稱中是否包含視頻或音頻標識
                            if "video" in file.lower() or file_ext in ['.mp4', '.webm', '.mkv', '.avi', '.flv', '.mov']:
                                video_files.append(file)
                            elif "audio" in file.lower() or file_ext in ['.m4a', '.mp3', '.ogg', '.wav', '.aac']:
                                audio_files.append(file)
                        
                        # 顯示找到的檔案
                        if video_files:
                            self.progress.emit("<span style=\"color: green;\">✅ 已找到視頻檔案：</span>")
                            for i, file in enumerate(video_files):
                                file_size = os.path.getsize(file) / (1024 * 1024)  # 轉換為 MB
                                file_name = os.path.basename(file)
                                self.progress.emit(f"<span style=\"color: green;\">{i+1}. {file_name} ({file_size:.1f} MB)</span>")
                        
                        if audio_files:
                            self.progress.emit("<span style=\"color: blue;\">ℹ️ 已找到音頻檔案：</span>")
                            for i, file in enumerate(audio_files):
                                file_size = os.path.getsize(file) / (1024 * 1024)  # 轉換為 MB
                                file_name = os.path.basename(file)
                                self.progress.emit(f"<span style=\"color: blue;\">{i+1}. {file_name} ({file_size:.1f} MB)</span>")
                        
                        # 如果找到視頻檔案，保留視頻檔案並刪除音頻檔案
                        if video_files:
                            # 找出最大的視頻檔案（可能是最高畫質）
                            best_video = max(video_files, key=os.path.getsize)
                            best_video_name = os.path.basename(best_video)
                            best_video_size = os.path.getsize(best_video) / (1024 * 1024)
                            
                            self.progress.emit(f"<span style=\"color: green;\">✅ 保留最高畫質視頻檔案: {best_video_name} ({best_video_size:.1f} MB)</span>")
                            
                            # 刪除其他視頻檔案
                            for file in video_files:
                                if file != best_video:
                                    try:
                                        os.remove(file)
                                        self.progress.emit(f"<span style=\"color: orange;\">🗑️ 已刪除多餘視頻檔案: {os.path.basename(file)}</span>")
                                    except:
                                        pass
                            
                            # 刪除所有音頻檔案
                            for file in audio_files:
                                try:
                                    os.remove(file)
                                    self.progress.emit(f"<span style=\"color: orange;\">🗑️ 已刪除音頻檔案: {os.path.basename(file)}</span>")
                                except:
                                    pass
                            
                            # 返回成功訊息
                            self.finished.emit(True, f"下載完成！保留高畫質視頻檔案: {best_video_name}")
                            return
                        
                        # 如果沒有找到視頻檔案，嘗試單一格式下載
                        self.progress.emit("<span style=\"color: orange;\">⚠️ 未找到可用的視頻檔案，嘗試使用單一格式下載...</span>")
                        
                        # 使用單一格式下載
                        download_opts['format'] = '22/18/best'  # 優先使用 YouTube 標準格式 (22=720p MP4, 18=360p MP4)
                        download_opts.pop('postprocessor_args', None)  # 移除 FFmpeg 參數
                        download_opts['keepvideo'] = False  # 不需要保留原始視頻
                        
                        try:
                            with yt_dlp.YoutubeDL(download_opts) as ydl:
                                ydl.download([self.url])
                            self.progress.emit("<span style=\"color: green;\">✅ 使用單一格式下載成功</span>")
                            
                            # 查找下載的檔案
                            import glob
                            pattern = os.path.join(self.output_path, f"{safe_title}.*")
                            files = [f for f in glob.glob(pattern) if os.path.getsize(f) > 0]
                            
                            if files:
                                actual_filename = os.path.basename(files[0])
                                self.finished.emit(True, f"下載完成！檔案名稱: {actual_filename}")
                                return
                            else:
                                self.progress.emit("<span style=\"color: orange;\">⚠️ 找不到下載的檔案，嘗試啟動備用下載...</span>")
                                self.finished.emit(True, "START_FALLBACK")
                                return
                        except Exception as e2:
                            self.progress.emit(f"<span style=\"color: red;\">單一格式下載失敗: {str(e2)}</span>")
                            self.finished.emit(True, "START_FALLBACK")
                            return
                    
                    # 嘗試使用單一高解析度格式
                    self.progress.emit("<span style=\"color: orange;\">⚠️ 嘗試使用高解析度單一格式...</span>")
                    download_opts['format'] = 'best[height>=720]/best'  # 優先使用720P或更高的單一格式
                    download_opts.pop('postprocessor_args', None)  # 移除 FFmpeg 參數
                    
                    try:
                        with yt_dlp.YoutubeDL(download_opts) as ydl:
                            ydl.download([self.url])
                        self.progress.emit("<span style=\"color: green;\">✅ 使用高解析度單一格式下載成功</span>")
                        
                        # 查找下載的檔案
                        import glob
                        pattern = os.path.join(self.output_path, f"{safe_title}.*")
                        files = [f for f in glob.glob(pattern) if os.path.getsize(f) > 0]
                        
                        if files:
                            actual_filename = os.path.basename(files[0])
                            self.finished.emit(True, f"下載完成！檔案名稱: {actual_filename}")
                            return
                    except Exception as e2:
                        self.progress.emit(f"<span style=\"color: red;\">高解析度單一格式下載失敗: {str(e2)}</span>")
                    
                    # 如果以上方法都失敗，嘗試使用 360p 格式
                    self.progress.emit("<span style=\"color: orange;\">⚠️ 嘗試使用標準 360p 格式...</span>")
                    download_opts['format'] = '18/best'  # 18 是 360p MP4 格式
                    
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
                        self.progress.emit(f"<span style=\"color: red;\">所有備用格式都失敗: {str(e3)}</span>")
                        self.finished.emit(False, f"下載失敗: {str(e)}。建議升級 yt-dlp 或用 cookies。")
        except Exception as e:
            # 檢查是否有 FFmpeg 相關錯誤
            if "ffmpeg" in str(e).lower() or "ffmpeg is not installed" in str(e):
                self.progress.emit("<span style=\"color: orange;\">⚠️ 檢測到 FFmpeg 相關錯誤，檢查是否有部分下載的檔案...</span>")
                
                # 檢查下載目錄中是否有新檔案
                import glob
                pattern = os.path.join(self.output_path, f"{safe_title}.*")
                files = [f for f in glob.glob(pattern) if os.path.getsize(f) > 0]
                
                if files:
                    # 找到部分下載的檔案
                    self.progress.emit("<span style=\"color: green;\">✅ 找到部分下載的檔案：</span>")
                    for file in files:
                        file_size = os.path.getsize(file) / (1024 * 1024)  # 轉換為 MB
                        self.progress.emit(f"<span style=\"color: green;\">- {os.path.basename(file)} ({file_size:.1f} MB)</span>")
                    
                    # 將檔案列表傳遞給主視窗，顯示選擇對話框
                    self.finished.emit(True, f"MULTI_FILES:{','.join(files)}")
                    return
            
            # 年齡限制自動提示
            elif 'Sign in to confirm your age' in str(e) or 'Use --cookies-from-browser or --cookies' in str(e):
                self.progress.emit("<span style=\"color: orange;\">❗ 此影片有年齡限制，請先登入 YouTube 並匯出 cookies.txt，再於下載選項中選擇 cookies 檔案！</span>")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "需要 cookies 驗證", "此影片有年齡限制，請先登入 YouTube 並匯出 cookies.txt，再於下載選項中選擇 cookies 檔案！\n\n詳見 https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp")
            
            self.progress.emit(f"<span style=\"color: red;\">主要方法失敗: {str(e)}</span>")
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
            # 顯示當前下載的檔案類型（視頻或音頻）
            filename = d.get('filename', '')
            if filename:
                # 判斷是視頻還是音頻
                file_type = ""
                if "video" in filename.lower():
                    file_type = "[視頻] "
                elif "audio" in filename.lower():
                    file_type = "[音頻] "
                
                # 提取檔案名稱（不含路徑）
                basename = os.path.basename(filename)
                
                # 只在第一次顯示檔案名稱
                if not hasattr(self, '_shown_files') or basename not in self._shown_files:
                    if not hasattr(self, '_shown_files'):
                        self._shown_files = set()
                    self._shown_files.add(basename)
                    self.progress.emit(f"{file_type}正在下載: {basename}")
            
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
            filename = d.get('filename', '')
            if filename:
                basename = os.path.basename(filename)
                # 判斷是視頻還是音頻
                file_type = ""
                if "video" in filename.lower():
                    file_type = "[視頻] "
                elif "audio" in filename.lower():
                    file_type = "[音頻] "
                self.progress.emit(f"{file_type}檔案下載完成: {basename}")
            else:
                self.progress.emit("檔案下載完成，正在處理...")
    
    def sanitize_filename(self, filename):
        # 廢棄，統一用 safe_filename
        return safe_filename(filename)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 設定視窗標題和大小
        self.setWindowTitle("YouTube 下載器")
        
        # 初始化 ffmpeg_path 屬性
        self.ffmpeg_path = None
        
        # 載入用戶偏好設定
        self.preferences = UserPreferences()
        
        # 設定視窗大小和位置
        self.setup_window_geometry()
        
        # 設定介面字體大小
        self.ui_font_size = self.preferences.get("ui_font_size", 10)  # 預設字體大小為 10
        self.apply_ui_font_size()
        
        # 初始化日誌去重
        self.log_messages = set()  # 用於記錄已顯示的日誌訊息
        
        # 檢查和設置 FFmpeg (在初始化 UI 之前)
        self.setup_ffmpeg()
        
        # 初始化 UI 元件
        self.init_ui()
        
        # 載入最近使用的 URL
        self.load_recent_urls()
        
        # 設定右鍵選單
        self.setup_context_menu()
        
        # 初始化下載線程
        self.download_thread = None
        
        # 顯示版本資訊
        self.show_version_info()
    
    def apply_ui_font_size(self):
        """應用介面字體大小設定"""
        # 設定全局樣式表，調整所有元件的字體大小
        self.setStyleSheet(f"""
            QLabel, QCheckBox, QRadioButton, QComboBox, QLineEdit, QGroupBox {{ font-size: {self.ui_font_size}pt; }}
            QPushButton {{ font-size: {self.ui_font_size}pt; }}
            QTextEdit {{ font-size: {self.ui_font_size}pt; }}
            QToolTip {{ font-size: {self.ui_font_size}pt; }}
            QMenuBar, QMenu {{ font-size: {self.ui_font_size}pt; }}
            QStatusBar {{ font-size: {self.ui_font_size}pt; }}
            QHeaderView {{ font-size: {self.ui_font_size}pt; }}
            QTabBar {{ font-size: {self.ui_font_size}pt; }}
        """)
    
    def increase_ui_font_size(self):
        """增加介面字體大小"""
        if self.ui_font_size < 18:  # 設置最大字體大小限制
            self.ui_font_size += 1
            self.preferences.set("ui_font_size", self.ui_font_size)
            self.apply_ui_font_size()
            self.append_log(f"介面字體大小已調整為: {self.ui_font_size}pt")
    
    def decrease_ui_font_size(self):
        """減小介面字體大小"""
        if self.ui_font_size > 8:  # 設置最小字體大小限制
            self.ui_font_size -= 1
            self.preferences.set("ui_font_size", self.ui_font_size)
            self.apply_ui_font_size()
            self.append_log(f"介面字體大小已調整為: {self.ui_font_size}pt")
    
    def setup_ffmpeg(self):
        """檢查並設置 FFmpeg"""
        # 初始化一個標誌，用於記錄 FFmpeg 狀態
        self.ffmpeg_status_message = ""
        
        # 先檢查是否已下載 FFmpeg
        if is_ffmpeg_downloaded():
            self.ffmpeg_path = get_ffmpeg_path()
            is_working, output = test_ffmpeg(self.ffmpeg_path)
            if is_working:
                self.ffmpeg_status_message = f"<span style=\"color: green;\">✓ FFmpeg 已找到並可用: {self.ffmpeg_path}</span>"
                return
        
        # 檢查系統中是否有 FFmpeg
        self.ffmpeg_path = find_ffmpeg_executable()
        
        if self.ffmpeg_path:
            # 驗證 FFmpeg 是否真的可用
            try:
                result = subprocess.run([self.ffmpeg_path, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.ffmpeg_status_message = f"<span style=\"color: green;\">✓ FFmpeg 已找到並可用: {self.ffmpeg_path}</span>"
                    return
                else:
                    self.ffmpeg_path = None
            except Exception:
                self.ffmpeg_path = None
        
        # 如果沒有找到可用的 FFmpeg，記錄狀態
        self.ffmpeg_status_message = "<span style=\"color: orange;\">⚠️ 未找到可用的 FFmpeg，請使用自動下載按鈕</span>"
    
    def show_ffmpeg_help_dialog(self):
        """顯示 FFmpeg 安裝幫助對話框"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextBrowser
        from PySide6.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle("FFmpeg 安裝幫助")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 標題
        title_label = QLabel("安裝 FFmpeg 以解決合併失敗問題")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2196F3;")
        layout.addWidget(title_label)
        
        # 說明文字
        help_text = QTextBrowser()
        help_text.setOpenExternalLinks(True)
        help_text.setHtml("""
        <h3>為什麼需要 FFmpeg?</h3>
        <p>FFmpeg 是用於處理音頻和視頻的強大工具。YouTube 下載器需要它來合併高品質的視頻和音頻流。</p>
        <p>如果沒有安裝 FFmpeg，您將只能下載較低品質的單一格式視頻，或者可能會遇到「合併失敗」的錯誤。</p>
        
        <h3>自動下載 FFmpeg:</h3>
        <p>您可以點擊下方的「自動下載 FFmpeg」按鈕，程式將自動下載並設置 FFmpeg。</p>
        <p><b>注意:</b> 自動下載的 FFmpeg 將存放在程式目錄下的 ffmpeg_bin 資料夾中，不會影響系統設置。</p>
        
        <h3>手動安裝 FFmpeg:</h3>
        
        <h4>Windows:</h4>
        <ol>
            <li>訪問 <a href="https://ffmpeg.org/download.html">FFmpeg 官方網站</a> 或 <a href="https://github.com/BtbN/FFmpeg-Builds/releases">GitHub 發布頁面</a></li>
            <li>下載 Windows 版本 (選擇 "ffmpeg-git-full.7z" 檔案)</li>
            <li>解壓縮檔案</li>
            <li>將解壓縮後的 bin 資料夾路徑 (例如 C:\\ffmpeg\\bin) 添加到系統環境變數 PATH 中</li>
            <li>重新啟動電腦</li>
        </ol>
        
        <h4>macOS:</h4>
        <ol>
            <li>安裝 <a href="https://brew.sh/">Homebrew</a> (如果尚未安裝)</li>
            <li>打開終端機</li>
            <li>執行指令: <code>brew install ffmpeg</code></li>
        </ol>
        
        <h4>Linux:</h4>
        <ol>
            <li>Ubuntu/Debian: <code>sudo apt update && sudo apt install ffmpeg</code></li>
            <li>Fedora: <code>sudo dnf install ffmpeg</code></li>
            <li>Arch Linux: <code>sudo pacman -S ffmpeg</code></li>
        </ol>
        
        <h3>安裝後:</h3>
        <p>安裝完成後，請重新啟動此應用程式。應用程式將自動偵測 FFmpeg 並使用它來提供更高品質的下載。</p>
        """)
        layout.addWidget(help_text)
        
        # 按鈕
        button_layout = QHBoxLayout()
        
        # 自動下載按鈕
        auto_download_button = QPushButton("自動下載 FFmpeg")
        auto_download_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        auto_download_button.clicked.connect(lambda: self.auto_download_ffmpeg_from_dialog(dialog))
        button_layout.addWidget(auto_download_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("關閉")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def auto_download_ffmpeg_from_dialog(self, parent_dialog=None):
        """從對話框中自動下載 FFmpeg"""
        # 關閉幫助對話框
        if parent_dialog:
            parent_dialog.accept()
        
        # 顯示下載進度對話框
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
        from PySide6.QtCore import Qt
        
        download_dialog = QDialog(self)
        download_dialog.setWindowTitle("下載 FFmpeg")
        download_dialog.setFixedSize(400, 150)
        download_dialog.setWindowFlags(download_dialog.windowFlags() | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(download_dialog)
        
        status_label = QLabel("準備下載 FFmpeg...")
        layout.addWidget(status_label)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # 不確定進度
        layout.addWidget(progress_bar)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(download_dialog.reject)
        layout.addWidget(cancel_button)
        
        # 顯示對話框
        download_dialog.show()
        
        # 更新下載進度的回調函數
        def update_download_status(message):
            status_label.setText(message)
            self.update_progress(f"<span style=\"color: blue;\">{message}</span>")
        
        # 在背景線程中下載 FFmpeg
        def download_thread_func():
            try:
                ffmpeg_path = download_ffmpeg(update_download_status)
                
                # 下載完成後關閉對話框
                download_dialog.accept()
                
                if ffmpeg_path and os.path.exists(ffmpeg_path):
                    self.ffmpeg_path = ffmpeg_path
                    is_working, _ = test_ffmpeg(ffmpeg_path)
                    if is_working:
                        self.update_progress(f"<span style=\"color: green;\">✓ FFmpeg 已成功下載並可用: {ffmpeg_path}</span>")
                        
                        # 更新 UI 上的 FFmpeg 狀態
                        if hasattr(self, 'ffmpeg_status_label'):
                            self.ffmpeg_status_label.setText("✅ FFmpeg 已安裝")
                            self.ffmpeg_status_label.setStyleSheet("font-size: 12px; color: green; margin: 5px;")
                        
                        # 顯示成功訊息
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.information(self, "FFmpeg 安裝成功", 
                                             "FFmpeg 已成功下載並設置完成！\n現在您可以下載並合併高品質影片了。")
                    else:
                        self.update_progress("<span style=\"color: red;\">❌ 下載的 FFmpeg 無法正常工作</span>")
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "FFmpeg 安裝失敗", 
                                         "下載的 FFmpeg 無法正常工作，請嘗試手動安裝。")
                else:
                    self.update_progress("<span style=\"color: red;\">❌ FFmpeg 下載失敗</span>")
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "FFmpeg 下載失敗", 
                                     "無法下載 FFmpeg，請檢查網絡連接或嘗試手動安裝。")
            except Exception as e:
                self.update_progress(f"<span style=\"color: red;\">❌ FFmpeg 下載過程中出錯: {str(e)}</span>")
                download_dialog.reject()
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "FFmpeg 下載錯誤", 
                                 f"下載 FFmpeg 時出錯: {str(e)}\n請嘗試手動安裝。")
        
        # 啟動下載線程
        threading.Thread(target=download_thread_func, daemon=True).start()
    
    def init_ui(self):
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
        
        # FFmpeg 狀態提示
        self.ffmpeg_status_label = QLabel()
        self.ffmpeg_status_label.setAlignment(Qt.AlignCenter)
        
        ffmpeg_layout = QHBoxLayout()
        
        if self.ffmpeg_path:
            self.ffmpeg_status_label.setText("✅ FFmpeg 已安裝")
            self.ffmpeg_status_label.setStyleSheet("font-size: 12px; color: green; margin: 5px;")
            ffmpeg_layout.addWidget(self.ffmpeg_status_label)
            
            # 即使已安裝，也提供重新下載選項
            self.ffmpeg_download_button = QPushButton("重新下載")
            self.ffmpeg_download_button.setStyleSheet("font-size: 10px; padding: 2px 5px; background-color: #4CAF50; color: white;")
            self.ffmpeg_download_button.clicked.connect(self.auto_download_ffmpeg_from_dialog)
            ffmpeg_layout.addWidget(self.ffmpeg_download_button)
        else:
            self.ffmpeg_status_label.setText("⚠️ 未找到 FFmpeg")
            self.ffmpeg_status_label.setStyleSheet("font-size: 12px; color: orange; font-weight: bold; margin: 5px;")
            ffmpeg_layout.addWidget(self.ffmpeg_status_label)
            
            # 添加 FFmpeg 自動下載按鈕
            self.ffmpeg_download_button = QPushButton("自動下載")
            self.ffmpeg_download_button.setStyleSheet("font-size: 10px; padding: 2px 5px; background-color: #4CAF50; color: white;")
            self.ffmpeg_download_button.clicked.connect(self.auto_download_ffmpeg_from_dialog)
            ffmpeg_layout.addWidget(self.ffmpeg_download_button)
            
            # 添加 FFmpeg 安裝幫助按鈕
            self.ffmpeg_help_button = QPushButton("安裝幫助")
            self.ffmpeg_help_button.setStyleSheet("font-size: 10px; padding: 2px 5px; background-color: #2196F3; color: white;")
            self.ffmpeg_help_button.clicked.connect(self.show_ffmpeg_help_dialog)
            ffmpeg_layout.addWidget(self.ffmpeg_help_button)
        
        left_layout.addLayout(ffmpeg_layout)
        
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
        
        # 獲取資訊按鈕
        info_button_layout = QHBoxLayout()
        self.fetch_button = QPushButton("獲取資訊")
        self.fetch_button.clicked.connect(self.fetch_video_info)
        self.fetch_button.setStyleSheet("font-size: 11pt; padding: 10px; background-color: #4CAF50; color: white;")
        info_button_layout.addStretch()
        info_button_layout.addWidget(self.fetch_button)
        url_input_layout.addLayout(info_button_layout)
        
        # 更新相關按鈕放在單獨的區域
        update_group = QGroupBox("更新選項")
        update_layout = QHBoxLayout(update_group)
        
        # 檢查更新按鈕
        self.update_ytdlp_button = QPushButton("檢查 yt-dlp 更新")
        self.update_ytdlp_button.setStyleSheet("font-size: 11pt; padding: 8px; background-color: #2196F3; color: white;")
        self.update_ytdlp_button.clicked.connect(self.check_and_update_ytdlp)
        
        # 重新下載 yt-dlp 按鈕
        self.reinstall_ytdlp_button = QPushButton("重新安裝 yt-dlp")
        self.reinstall_ytdlp_button.setStyleSheet("font-size: 11pt; padding: 8px; background-color: #FF9800; color: white;")
        self.reinstall_ytdlp_button.clicked.connect(self.reinstall_ytdlp)
        
        update_layout.addWidget(self.update_ytdlp_button)
        update_layout.addWidget(self.reinstall_ytdlp_button)
        
        # 添加更新選項區域到 UI
        left_layout.addWidget(update_group)
        
        url_layout.addLayout(url_input_layout)
        # 下載完成提醒設定
        self.show_completion_dialog = QCheckBox("下載完成後顯示提醒視窗")
        # 預設值為 False (不顯示提醒視窗)
        self.show_completion_dialog.setChecked(False)
        # 連接狀態變更事件
        self.show_completion_dialog.stateChanged.connect(self.on_completion_dialog_changed)
        url_layout.addWidget(self.show_completion_dialog)
        # 在日誌中顯示當前狀態
        self.log_output_ready = False  # 標記日誌區域是否已準備好
        
        # 新增 fallback 提示 label
        self.fallback_info_label = QLabel()
        self.fallback_info_label.setStyleSheet("color: #388e3c; font-weight: bold; margin: 2px 0 0 0;")
        self.fallback_info_label.setVisible(False)
        url_layout.addWidget(self.fallback_info_label)
        left_layout.addWidget(url_group)
        
        # 下載選項區域
        options_group = QGroupBox("下載選項")
        options_layout = QGridLayout(options_group)
        
        # 下載類型（簡化為只有影片模式）
        type_label = QLabel("下載類型:")
        self.download_type_label = QLabel("影片 (最佳品質)")
        self.download_type_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        options_layout.addWidget(type_label, 0, 0)
        options_layout.addWidget(self.download_type_label, 0, 1)
        
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
        
        # 檔案名稱前綴設定 - 使用下拉選單
        prefix_label = QLabel("檔案名稱前綴:")
        
        # 創建水平佈局來放置下拉選單和輸入框
        prefix_layout = QHBoxLayout()
        
        # 創建前綴下拉選單
        self.prefix_combo = QComboBox()
        self.prefix_combo.addItems([
            "Per best-",
            "Per best2-",
            "Per best3-",
            "Per Nice-",
            "Per Nice2-",
            "自訂..."
        ])
        
        # 創建輸入框
        self.filename_prefix = QLineEdit()
        self.filename_prefix.setPlaceholderText("輸入自訂前綴")
        
        # 設定預設前綴
        default_prefix = self.preferences.get_filename_prefix()
        if not default_prefix:
            default_prefix = "Per best-"  # 預設值
            self.preferences.set_filename_prefix(default_prefix)
        
        # 如果預設前綴在列表中，選擇它
        index = self.prefix_combo.findText(default_prefix)
        if index >= 0:
            self.prefix_combo.setCurrentIndex(index)
            self.filename_prefix.setText("")  # 清空自訂輸入框
            self.filename_prefix.setVisible(False)  # 隱藏自訂輸入框
        else:
            # 如果不在列表中，選擇"自訂..."並顯示在輸入框
            self.prefix_combo.setCurrentText("自訂...")
            self.filename_prefix.setText(default_prefix)
            self.filename_prefix.setVisible(True)
        
        # 當選擇前綴時更新
        self.prefix_combo.currentTextChanged.connect(self.on_prefix_selected)
        self.filename_prefix.textChanged.connect(self.on_custom_prefix_changed)
        
        # 添加到佈局
        prefix_layout.addWidget(self.prefix_combo)
        prefix_layout.addWidget(self.filename_prefix)
        
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
        
        # 日誌文字大小調整
        font_size_label = QLabel("日誌文字:")
        font_size_layout.addWidget(font_size_label)
        
        self.decrease_font_button = QPushButton("-")
        self.decrease_font_button.setFixedSize(30, 25)
        self.decrease_font_button.clicked.connect(self.decrease_log_font_size)
        font_size_layout.addWidget(self.decrease_font_button)
        
        self.increase_font_button = QPushButton("+")
        self.increase_font_button.setFixedSize(30, 25)
        self.increase_font_button.clicked.connect(self.increase_log_font_size)
        font_size_layout.addWidget(self.increase_font_button)
        
        font_size_layout.addSpacing(20)  # 間隔
        
        # 介面字體大小調整
        ui_font_label = QLabel("介面字體:")
        font_size_layout.addWidget(ui_font_label)
        
        self.decrease_ui_font_button = QPushButton("-")
        self.decrease_ui_font_button.setFixedSize(30, 25)
        self.decrease_ui_font_button.clicked.connect(self.decrease_ui_font_size)
        font_size_layout.addWidget(self.decrease_ui_font_button)
        
        self.increase_ui_font_button = QPushButton("+")
        self.increase_ui_font_button.setFixedSize(30, 25)
        self.increase_ui_font_button.clicked.connect(self.increase_ui_font_size)
        font_size_layout.addWidget(self.increase_ui_font_button)
        
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
        
        # 標記日誌區域已準備好
        self.log_output_ready = True
        
        # 顯示下載完成提醒設置狀態
        show_dialog = self.preferences.get_show_completion_dialog()
        self.log_output.append(f"{'✅' if show_dialog else '❌'} 下載完成提醒已{'開啟' if show_dialog else '關閉'}")
        
        # 顯示 FFmpeg 狀態訊息
        if hasattr(self, 'ffmpeg_status_message') and self.ffmpeg_status_message:
            self.append_log(self.ffmpeg_status_message)
            
        # 顯示所有待處理的訊息
        if hasattr(self, 'pending_messages') and self.pending_messages:
            for message in self.pending_messages:
                if any(error_keyword in message for error_keyword in ["失敗", "錯誤", "ERROR", "error", "failed", "❌", "合併視頻和音頻失敗"]):
                    self.log_output.append(f'<span style="color: red;">{message}</span>')
                else:
                    self.log_output.append(message)
            self.pending_messages = []
    
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
        
        # 清空日誌區域，避免混淆
        self.log_output.clear()
        self.log_output.append("正在獲取影片資訊...")
        
        # 確保滾動到底部
        self.scroll_log_to_bottom()
        
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
                    extract_audio_only = False  # 簡化為只有影片模式
                    filename_prefix = self.get_current_prefix()
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
            extract_audio_only = False  # 簡化為只有影片模式
            filename_prefix = self.get_current_prefix()
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
        # 檢查 log_output 是否已初始化
        if not hasattr(self, 'log_output') or not self.log_output:
            # 如果尚未初始化，將訊息保存到狀態訊息中
            if not hasattr(self, 'pending_messages'):
                self.pending_messages = []
            self.pending_messages.append(message)
            return
        
        # 避免重複訊息
        if hasattr(self, 'last_message') and self.last_message == message:
            return
        self.last_message = message
        
        # 過濾進度百分比訊息，只保留最新的
        if "下載中... " in message and "%" in message:
            # 找到並移除之前的進度訊息
            cursor = self.log_output.textCursor()
            cursor.movePosition(cursor.Start)
            found = self.log_output.find("下載中... ", cursor)
            if found:
                cursor = self.log_output.textCursor()
                cursor.select(cursor.LineUnderCursor)
                selected_text = cursor.selectedText()
                if "%" in selected_text:
                    cursor.removeSelectedText()
                    
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
        """下載完成時的處理"""
        # 移除進度條
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        # 啟用按鈕
        self.fetch_button.setEnabled(True)
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.download_button.setText("開始下載")
        
        # 如果下載成功，清除 URL 輸入框
        if success:
            # 先保存 URL 到最近使用的 URL 列表
            url = self.url_input.text().strip()
            if url:
                self.preferences.add_recent_url(url)
                self.load_recent_urls()  # 重新載入 URL 列表
            # 清空輸入框
            self.url_input.clear()
        # 如果下載失敗，保留 URL 不變
        
        # 處理多檔案選擇情況
        if success and message.startswith("MULTI_FILES:"):
            files = message.replace("MULTI_FILES:", "").split(",")
            self.show_file_selection_dialog(files)
            return
            
        # 處理直接開始備用下載的情況
        if success and message == "START_FALLBACK":
            self.update_progress("<span style=\"color: blue;\">ℹ️ 直接開始下載備用版本...</span>")
            self.start_fallback_download()
            return
        
        # 處理保留高畫質視頻檔案的情況
        if success and message.startswith("下載完成！保留高畫質視頻檔案:"):
            filename = message.replace("下載完成！保留高畫質視頻檔案:", "").strip()
            self.update_progress(f"<span style=\"color: green;\">✅ {message}</span>")
            
            # 顯示完成對話框
            if self.show_completion_dialog.isChecked():
                self.show_completion_dialog_with_options(self.path_input.text(), filename)
            return
        
        # 顯示結果
        if success:
            self.update_progress(f"<span style=\"color: green;\">✅ {message}</span>")
            
            # 提取檔案路徑和檔名
            parts = message.split("檔案名稱: ")
            if len(parts) > 1:
                filename = parts[1]
                file_path = os.path.join(self.path_input.text(), filename)
                
                # 檢查檔案是否存在
                if os.path.exists(file_path):
                    # 顯示完成對話框
                    if self.show_completion_dialog.isChecked():
                        self.show_completion_dialog_with_options(self.path_input.text(), filename)
                else:
                    self.update_progress("<span style=\"color: orange;\">⚠️ 警告：找不到下載的檔案，可能已被移動或重命名</span>")
            else:
                self.log_output.append(message)
                # 直接使用 UI 元素的狀態，而不是偏好設定
                if self.show_completion_dialog.isChecked():
                    QMessageBox.information(self, "完成", "下載完成！")
        else:
            self.update_progress(f"<span style=\"color: red;\">❌ {message}</span>")
            self.analyze_download_error(message)
            
            # 如果勾選了顯示完成對話框，則顯示失敗對話框
            if self.show_completion_dialog.isChecked():
                self.show_completion_dialog_with_options(self.path_input.text(), "", success=False, fail_message=message)
        
        # 記錄下載歷史
        url = self.url_input.text().strip()
        title = "未知標題"
        format_choice = self.get_format_choice()
        self.preferences.add_download_history(url, title, format_choice, success)
    
    def show_file_selection_dialog(self, files):
        """顯示檔案選擇對話框"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("選擇要保留的檔案")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # 說明標籤
        label = QLabel("合併視頻和音頻失敗，請選擇要保留的檔案：")
        layout.addWidget(label)
        
        # 檔案列表
        file_list = QListWidget()
        for file in files:
            file_size = os.path.getsize(file) / (1024 * 1024)  # 轉換為 MB
            file_list.addItem(f"{os.path.basename(file)} ({file_size:.1f} MB)")
        layout.addWidget(file_list)
        
        # 按鈕
        button_layout = QHBoxLayout()
        
        keep_all_button = QPushButton("全部保留")
        keep_all_button.clicked.connect(lambda: self.handle_file_selection(files, None, dialog))
        
        select_button = QPushButton("保留選擇的檔案")
        select_button.clicked.connect(lambda: self.handle_file_selection(files, file_list.currentRow(), dialog))
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(keep_all_button)
        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 顯示對話框
        dialog.exec()
    
    def handle_file_selection(self, files, selected_index, dialog):
        """處理檔案選擇結果"""
        try:
            dialog.accept()
            
            if selected_index is None:
                # 全部保留
                self.update_progress("<span style=\"color: green;\">✅ 已保留所有檔案</span>")
                
                # 顯示檔案列表
                for file in files:
                    try:
                        file_size = os.path.getsize(file) / (1024 * 1024)  # 轉換為 MB
                        self.update_progress(f"<span style=\"color: green;\">- {os.path.basename(file)} ({file_size:.1f} MB)</span>")
                    except:
                        self.update_progress(f"<span style=\"color: orange;\">- {os.path.basename(file)} (無法獲取大小)</span>")
                
                try:
                    # 找到最大的檔案作為主要結果
                    largest_file = max(files, key=lambda f: os.path.getsize(f) if os.path.exists(f) else 0)
                    filename = os.path.basename(largest_file)
                except:
                    filename = os.path.basename(files[0]) if files else "未知檔案"
                
                # 同時開始下載較低解析度的完整版本
                try:
                    self.start_fallback_download()
                except Exception as e:
                    self.update_progress(f"<span style=\"color: red;\">❌ 啟動備用下載失敗: {str(e)}</span>")
                
                # 顯示完成對話框
                if self.show_completion_dialog.isChecked():
                    self.show_completion_dialog_with_options(self.path_input.text(), filename)
            
            elif 0 <= selected_index < len(files):
                # 保留選擇的檔案
                selected_file = files[selected_index]
                filename = os.path.basename(selected_file)
                
                self.update_progress(f"<span style=\"color: green;\">✅ 已保留檔案：{filename}</span>")
                
                # 刪除其他檔案
                for file in files:
                    if file != selected_file:
                        try:
                            os.remove(file)
                            self.update_progress(f"<span style=\"color: orange;\">🗑️ 已刪除：{os.path.basename(file)}</span>")
                        except:
                            self.update_progress(f"<span style=\"color: red;\">❌ 無法刪除：{os.path.basename(file)}</span>")
                
                # 同時開始下載較低解析度的完整版本
                try:
                    self.start_fallback_download()
                except Exception as e:
                    self.update_progress(f"<span style=\"color: red;\">❌ 啟動備用下載失敗: {str(e)}</span>")
                
                # 顯示完成對話框
                if self.show_completion_dialog.isChecked():
                    self.show_completion_dialog_with_options(self.path_input.text(), filename)
        except Exception as e:
            self.update_progress(f"<span style=\"color: red;\">❌ 處理檔案選擇時出錯: {str(e)}</span>")
    
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
        self.append_log(version_info)
    
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
        from PySide6.QtCore import Qt
        is_checked = state == Qt.Checked
        # 確保設定被正確保存
        result = self.preferences.set_show_completion_dialog(is_checked)
        # 立即保存偏好設定到檔案
        self.preferences.save_preferences()
        self.log_output.append(f"{'✅' if is_checked else '❌'} 下載完成提醒已{'開啟' if is_checked else '關閉'} {'(設定已保存)' if result else '(設定保存失敗)'}")
    
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
        from PySide6.QtCore import Qt
        
        # 記錄對話框顯示
        self.log_output.append(f"{'✅' if success else '❌'} 顯示{'下載完成' if success else '下載失敗'}提醒對話框")
        
        dialog = QDialog(self)
        dialog.setWindowTitle("下載完成" if success else "下載失敗")
        dialog.setModal(True)
        dialog.setFixedSize(400, 200)
        # 設置視窗置頂
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
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

    # 移除不再需要的前綴歷史相關方法

    def get_format_choice(self):
        """獲取下載格式選擇 (簡化為只有影片)"""
        return "影片"

    def browse_path(self):
        """瀏覽下載路徑"""
        folder = QFileDialog.getExistingDirectory(self, "選擇下載資料夾")
        if folder:
            # 確保路徑格式正確
            folder = os.path.normpath(folder)
            # 更新 UI 顯示
            self.path_input.setText(folder)
            # 記住下載路徑
            self.preferences.set_download_path(folder)
            # 在日誌中顯示所選路徑
            self.log_output.append(f"<span style=\"color: green;\">✅ 已選擇下載路徑: {folder}</span>")

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
    
    def start_fallback_download(self):
        """開始下載較低解析度的備用影片"""
        try:
            url = self.url_input.text().strip()
            if not url:
                self.update_progress("<span style=\"color: red;\">❌ 無法開始備用下載：URL 為空</span>")
                return
            
            # 創建一個備用檔名前綴
            original_prefix = self.filename_prefix.text().strip()
            fallback_prefix = original_prefix + "備用_" if original_prefix else "備用_"
            
            # 使用較低解析度
            output_path = self.path_input.text().strip()
            format_choice = self.get_format_choice()
            resolution_choice = "480P"  # 使用 480P 作為備用解析度
            extract_audio_only = False
            cookies_path = self.cookies_input.text().strip()
            
            # 使用單一格式下載，避免需要合併
            # 使用更可靠的格式選項，優先選擇已合併的格式
            format_string = '22/18/best'  # 22=720p MP4, 18=360p MP4
            merge_output_format = 'mp4'
            
            self.update_progress("<span style=\"color: blue;\">ℹ️ 開始下載備用版本 (單一格式)...</span>")
            self.fallback_info_label.setText("⚠️ 正在下載備用版本 (單一格式)...")
            self.fallback_info_label.setVisible(True)
            
            # 使用延遲啟動，避免與主下載線程競爭
            from PySide6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self._start_delayed_fallback_download(url, output_path, format_choice, resolution_choice, extract_audio_only, fallback_prefix, format_string, merge_output_format, cookies_path))
        except Exception as e:
            self.update_progress(f"<span style=\"color: red;\">❌ 備用下載初始化失敗: {str(e)}</span>")
    
    def _start_delayed_fallback_download(self, url, output_path, format_choice, resolution_choice, extract_audio_only, fallback_prefix, format_string, merge_output_format, cookies_path):
        """延遲啟動備用下載，避免與主下載線程競爭"""
        try:
            if not url:
                return
                
            # 創建新的下載線程
            self.fallback_thread = DownloadThread(
                url,
                output_path,
                format_choice,
                resolution_choice,
                extract_audio_only,
                fallback_prefix,
                format_string,
                merge_output_format,
                False,
                cookies_path
            )
            
            # 連接信號
            self.fallback_thread.progress.connect(self.update_fallback_progress)
            self.fallback_thread.finished.connect(self.fallback_download_finished)
            
            # 開始下載
            self.fallback_thread.start()
        except Exception as e:
            self.update_progress(f"<span style=\"color: red;\">❌ 備用下載啟動失敗: {str(e)}</span>")
    
    def update_fallback_progress(self, message):
        """更新備用下載進度"""
        self.update_progress(f"<span style=\"color: blue;\">[備用] {message}</span>")
    
    def fallback_download_finished(self, success, message):
        """備用下載完成時的處理"""
        if success:
            self.update_progress(f"<span style=\"color: green;\">[備用] ✅ {message}</span>")
            self.fallback_info_label.setText("✅ 備用 720P 版本下載完成")
        else:
            self.update_progress(f"<span style=\"color: orange;\">[備用] ⚠️ {message}</span>")
            self.fallback_info_label.setText("⚠️ 備用版本下載失敗")
        
        # 不顯示完成對話框，因為主下載已經顯示了
    
    def scroll_log_to_bottom(self):
        """確保日誌滾動到底部"""
        if hasattr(self, 'log_output') and self.log_output:
            # 使用 QTimer 確保在 UI 更新後滾動
            from PySide6.QtCore import QTimer
            QTimer.singleShot(50, lambda: self.log_output.verticalScrollBar().setValue(
                self.log_output.verticalScrollBar().maximum()
            ))

    def reinstall_ytdlp(self):
        """重新安裝 yt-dlp"""
        self.log_output.clear()
        self.log_output.append("正在重新安裝 yt-dlp...")
        self.scroll_log_to_bottom()
        
        # 在背景線程中執行安裝
        def install_thread():
            try:
                import subprocess
                import sys
                
                # 先嘗試卸載
                try:
                    self.log_output.append("正在卸載現有的 yt-dlp...")
                    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "yt-dlp"])
                    self.log_output.append("✅ yt-dlp 已成功卸載")
                except:
                    self.log_output.append("⚠️ 卸載 yt-dlp 時出現警告，將繼續安裝")
                
                # 安裝最新版本
                self.log_output.append("正在安裝最新版本的 yt-dlp...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
                
                # 檢查安裝後的版本
                try:
                    import yt_dlp
                    version = yt_dlp.version.__version__
                    self.log_output.append(f"✅ yt-dlp v{version} 已成功安裝")
                    
                    # 顯示成功訊息
                    from PySide6.QtWidgets import QMessageBox
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: QMessageBox.information(self, "安裝成功", f"yt-dlp v{version} 已成功安裝"))
                except:
                    self.log_output.append("⚠️ 無法確認 yt-dlp 版本，但安裝過程已完成")
                
                self.scroll_log_to_bottom()
                
            except Exception as e:
                self.log_output.append(f"❌ 重新安裝 yt-dlp 失敗: {str(e)}")
                self.scroll_log_to_bottom()
                
                # 顯示錯誤訊息
                from PySide6.QtWidgets import QMessageBox
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "安裝失敗", f"重新安裝 yt-dlp 失敗: {str(e)}"))
        
        # 啟動安裝線程
        import threading
        threading.Thread(target=install_thread, daemon=True).start()
    
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

    def on_prefix_selected(self, text):
        """當從下拉選單選擇前綴時"""
        if text == "自訂...":
            # 顯示自訂輸入框
            self.filename_prefix.setVisible(True)
            self.filename_prefix.setFocus()
        else:
            # 隱藏自訂輸入框並使用選擇的前綴
            self.filename_prefix.setVisible(False)
            # 保存選擇的前綴
            self.preferences.set_filename_prefix(text)
            self.append_log(f"已設定檔案名稱前綴: {text}")
    
    def on_custom_prefix_changed(self, text):
        """當自訂前綴文字變更時"""
        if self.prefix_combo.currentText() == "自訂...":
            # 只有在「自訂...」模式下才保存
            self.preferences.set_filename_prefix(text)
    
    def get_current_prefix(self):
        """獲取當前使用的前綴"""
        if self.prefix_combo.currentText() == "自訂...":
            return self.filename_prefix.text().strip()
        else:
            return self.prefix_combo.currentText()

    def append_log(self, message):
        """添加日誌訊息，避免重複顯示"""
        # 檢查訊息是否已經顯示過
        if message in self.log_messages:
            return
            
        # 將訊息添加到已顯示集合中
        self.log_messages.add(message)
        
        # 顯示訊息
        self.log_output.append(message)
        
        # 自動滾動到底部
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

 