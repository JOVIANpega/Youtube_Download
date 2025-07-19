#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多平台影片下載器 - 主程式
"""

import os
import sys
import time
import webbrowser
import re
import json
import subprocess
import platform
import traceback
import datetime
import shutil
import tempfile
import glob
import ssl
import threading
import random
import yt_dlp
from pathlib import Path

# 添加當前目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 導入自定義模組（這些函數都在本檔案中定義）
# from src.utils import log, get_system_info, create_error_log, apply_ssl_fix, format_size, format_time, sanitize_filename, identify_platform, get_supported_platforms
# from src.download_thread import DownloadThread

# 導入PySide6
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize, QUrl, QRect, QPoint, QMutex, QWaitCondition
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices, QColor, QPalette, QFont, QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QProgressBar, QComboBox,
    QTabWidget, QScrollArea, QFrame, QSpinBox, QCheckBox,
    QMessageBox, QFileDialog, QDialog, QGroupBox, QRadioButton,
    QListWidget, QListWidgetItem, QSplitter, QMenu, QSystemTrayIcon,
    QSlider, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QToolButton, QSizePolicy, QSpacerItem, QColorDialog, QFontDialog,
    QButtonGroup, QGridLayout, QFormLayout, QStyledItemDelegate
)

def get_settings_path():
    """獲取設定檔路徑"""
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_dir, 'setup.json')

def get_system_info():
    """獲取系統信息"""
    try:
        info = {
            "platform": sys.platform,
            "python_version": sys.version,
            "os_name": os.name,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "yt_dlp_version": getattr(yt_dlp.version, "__version__", "未知")
        }
        
        # 獲取更多詳細的系統信息
        if hasattr(sys, "getwindowsversion") and callable(sys.getwindowsversion):
            try:
                win_ver = sys.getwindowsversion()
                info["windows_version"] = f"{win_ver.major}.{win_ver.minor}.{win_ver.build}"
            except:
                pass
        
        # 獲取 CPU 和記憶體信息
        try:
            import psutil
            info["cpu_count"] = psutil.cpu_count(logical=False)
            info["cpu_logical_count"] = psutil.cpu_count(logical=True)
            mem = psutil.virtual_memory()
            info["total_memory_gb"] = round(mem.total / (1024**3), 2)
            info["available_memory_gb"] = round(mem.available / (1024**3), 2)
        except ImportError:
            # psutil 模組不可用
            pass
        
        return info
    except Exception as e:
        log(f"獲取系統信息失敗: {str(e)}")
        return {"error": str(e)}

def create_error_log(error_info, url, format_option, resolution, output_path):
    """創建錯誤日誌"""
    try:
        # 確保日誌目錄存在
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 創建錯誤報告
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        error_log_file = os.path.join(log_dir, f"error_log_{timestamp}.txt")
        
        # 系統信息
        system_info = get_system_info()
        
        # 下載設定
        download_settings = {
            "url": url,
            "format": format_option,
            "resolution": resolution,
            "output_path": output_path
        }
        
        # 寫入錯誤日誌
        with open(error_log_file, "w", encoding="utf-8") as f:
            f.write("=== YouTube 下載器錯誤報告 ===\n\n")
            f.write(f"時間: {timestamp}\n\n")
            
            f.write("=== 系統信息 ===\n")
            for key, value in system_info.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            f.write("=== 下載設定 ===\n")
            for key, value in download_settings.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            f.write("=== 錯誤信息 ===\n")
            f.write(f"{error_info}\n\n")
            
            f.write("=== 完整錯誤追蹤 ===\n")
            f.write(traceback.format_exc())
            
            # 附加診斷信息
            f.write("\n=== 網路診斷 ===\n")
            try:
                f.write("正在檢查網絡連接...\n")
                # 嘗試連接到 YouTube
                response = urllib.request.urlopen("https://www.youtube.com", timeout=5)
                f.write(f"YouTube 網站可訪問，狀態碼: {response.getcode()}\n")
            except Exception as e:
                f.write(f"無法連接到 YouTube: {str(e)}\n")
            
            f.write("\n=== FFmpeg 診斷 ===\n")
            try:
                ffmpeg_path = "ffmpeg"
                result = subprocess.run([ffmpeg_path, "-version"], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE, 
                                        text=True, 
                                        timeout=5)
                f.write(f"FFmpeg 版本: {result.stdout.splitlines()[0] if result.stdout else '未知'}\n")
            except Exception as e:
                f.write(f"FFmpeg 診斷失敗: {str(e)}\n")
            
        return error_log_file
    except Exception as e:
        print(f"創建錯誤日誌失敗: {str(e)}")
        return None

# 日誌函數
def log(message):
    """記錄日誌"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# SSL修復函數
def apply_ssl_fix():
    """應用SSL修復（V1.73特色功能）"""
    log("自動套用SSL證書修復...")
    try:
        # 更安全的SSL設定
        import ssl
        
        # 創建SSL上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 設置為默認HTTPS上下文
        ssl._create_default_https_context = lambda: ssl_context
        
        # 嘗試使用urllib3禁用警告，但不依賴其他設定
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except:
            pass  # 如果urllib3不可用，直接忽略
        
        log("SSL證書驗證已停用，這可以解決某些SSL錯誤")
        return True
    except Exception as e:
        log(f"SSL修復遇到問題: {e}")
        # 嘗試最基本的SSL設定
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            ssl._create_default_https_context = lambda: ssl_context
            log("使用基本SSL設定")
            return True
        except Exception as e2:
            log(f"基本SSL設定也失敗: {e2}")
            return False

# 應用SSL修復
apply_ssl_fix()

# 平台識別函數
def identify_platform(url):
    """識別影片平台"""
    url_lower = url.lower()
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return "YouTube"
    elif 'tiktok.com' in url_lower or 'douyin.com' in url_lower:
        return "TikTok"
    elif 'facebook.com' in url_lower or 'fb.com' in url_lower or 'fb.watch' in url_lower:
        return "Facebook"
    elif 'instagram.com' in url_lower:
        return "Instagram"
    elif 'bilibili.com' in url_lower or 'b23.tv' in url_lower:
        return "Bilibili"
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return "X"
    elif 'threads.net' in url_lower:
        return "Threads"
    else:
        return "未知平台"

# 支援平台列表
def get_supported_platforms():
    """獲取支援的平台列表"""
    return ["YouTube", "TikTok", "抖音", "Facebook", "Instagram", "Bilibili", "X", "Twitter"]

# 檔案大小格式化
def format_size(bytes):
    """格式化檔案大小"""
    if bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while bytes >= 1024 and i < len(size_names) - 1:
        bytes /= 1024.0
        i += 1
    return f"{bytes:.1f} {size_names[i]}"

# 時間格式化
def format_time(seconds):
    """格式化時間"""
    if seconds < 0:
        return "--:--"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

# 檔案名稱清理
def sanitize_filename(filename):
    """清理檔案名稱，移除非法字符"""
    # 移除或替換非法字符
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    
    # 移除開頭和結尾的空格和點
    filename = filename.strip(' .')
    
    # 限制長度
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename

class DownloadThread(QThread):
    """下載線程類"""
    progress = Signal(str, int, str, str)  # 訊息, 進度百分比, 速度, ETA
    finished = Signal(bool, str, str)  # 成功/失敗, 訊息, 檔案路徑
    platform_detected = Signal(str, str)  # 平台名稱, URL
    
    def __init__(self, url, output_path, format_option, resolution, prefix, auto_merge):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_option = format_option
        self.resolution = resolution
        self.prefix = prefix
        self.auto_merge = auto_merge
        self.is_cancelled = False
        self.is_paused = False
        self.pause_condition = QWaitCondition()
        self.pause_mutex = QMutex()
        self.retry_count = 0
        self.max_retries = 3
        self.last_error = None
        self.last_error_traceback = None
        self.last_progress_time = time.time()  # 記錄最後一次進度更新的時間
        self.progress_timeout = 30  # 進度超時時間（秒）
        self.download_speed_history = []  # 記錄下載速度歷史
        self.stall_check_timer = QTimer()  # 添加定時器檢查下載是否卡住
        self.stall_check_timer.timeout.connect(self.check_download_stall)
        self.stall_check_timer.start(5000)  # 每5秒檢查一次
        self.platform_info = None  # 存儲平台信息
    
    def run(self):
        """執行下載任務"""
        try:
            # 設置開始時間
            self.start_time = time.time()
            self.last_progress_time = time.time()
            self.last_progress = 0
            self.progress.emit(f"正在獲取影片資訊...", 0, "--", "--")
            
            # 嘗試套用SSL修復
            apply_ssl_fix()
            
            # 識別平台
            platform_name = identify_platform(self.url)
            
            # 發送平台識別信號
            self.platform_detected.emit(platform_name, self.url)
            
            # 檢查是否為未知平台
            if platform_name == "未知":
                raise Exception("無法辨識或不支援此平台，請確認URL格式是否正確")
            
            # 在日誌中顯示平台信息
            log(f"識別到平台: {platform_name}, URL: {self.url}")
            
            # 在日誌中明確顯示使用的前綴
            log(f"應用檔案名稱前綴: {self.prefix}")
            
            # 獲取下載選項
            ydl_opts = self.get_ydl_options()
            
            # 執行下載
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 獲取影片信息
                self.progress.emit("正在獲取影片資訊...", 0, "--", "--")
                info = ydl.extract_info(self.url, download=False)
                
                if info is None:
                    raise Exception("無法獲取影片資訊，可能是無效連結或該影片已被移除")
                
                # 獲取影片標題
                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"開始下載: {title}", 0, "--", "--")
                
                # 檢查是否需要暫停
                self.check_pause()
                
                # 檢查是否已取消
                if self.is_cancelled:
                    self.finished.emit(False, "下載已取消", "")
                    return
                
                # 開始下載
                ydl.download([self.url])
                
                # 構建下載的檔案路徑
                file_ext = info.get('ext', 'mp4')
                if "僅音訊 (MP3)" in self.format_option:
                    file_ext = 'mp3'
                elif "僅音訊 (WAV)" in self.format_option:
                    file_ext = 'wav'
                    
                safe_title = self.sanitize_filename(title)
                file_path = os.path.join(self.output_path, f'{self.prefix}{safe_title}.{file_ext}')
                
                # 檢查檔案是否存在
                if not os.path.exists(file_path):
                    # 嘗試查找可能的檔案名
                    files = os.listdir(self.output_path)
                    for file in files:
                        if file.startswith(f"{self.prefix}{safe_title}"):
                            file_path = os.path.join(self.output_path, file)
                            break
                
                self.finished.emit(True, f"下載完成: {title}", file_path)
        except Exception as e:
            error_message = str(e)
            log(f"下載失敗: {error_message}")
            
            # 檢查是否是年齡限制錯誤
            is_age_restricted = False
            if ("age-restricted" in error_message.lower() or 
                "sign in to confirm your age" in error_message.lower() or 
                "confirm your age" in error_message.lower()):
                is_age_restricted = True
                self.progress.emit("檢測到年齡限制，需要使用 cookies 進行驗證", 0, "--", "--")
                log("檢測到年齡限制影片，需要使用 cookies 進行驗證")
                
                # 直接返回年齡限制錯誤，不嘗試備用方法
                if is_age_restricted:
                    self.finished.emit(False, error_message, "")
                    return
            
            # 嘗試備用下載方法
            if self.retry_count < 2:
                self.retry_count += 1
                self.progress.emit(f"第 {self.retry_count} 次重試，使用備用方法...", 0, "--", "--")
                try:
                    success = self.fallback_download_method()
                    if success:
                        return
                except Exception as fallback_error:
                    error_message += f"\n\n備用方法也失敗: {str(fallback_error)}"
            
            # 如果重試次數達到上限，嘗試分段下載
            if self.retry_count >= 2:
                self.progress.emit("嘗試分段下載方法...", 0, "--", "--")
                try:
                    success = self.try_segment_download()
                    if success:
                        return
                except Exception as segment_error:
                    error_message += f"\n\n分段下載也失敗: {str(segment_error)}"
            
            self.finished.emit(False, error_message, "")
        finally:
            # 確保清理資源
            self.is_cancelled = True
            self.is_paused = False
    
    def get_ydl_options(self):
        """獲取下載選項，根據重試次數調整設定"""
        # 確保前綴不為None
        prefix = self.prefix if self.prefix else ""
        
        # 在日誌中明確顯示使用的前綴
        log(f"應用檔案名稱前綴: {prefix}")
        
        ydl_opts = {
            'outtmpl': os.path.join(self.output_path, f'{prefix}%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'socket_timeout': 30 + (self.retry_count * 10),  # 逐漸增加超時時間
            'retries': 5 + (self.retry_count * 3),  # 逐漸增加重試次數
            'fragment_retries': 5 + (self.retry_count * 3),
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            # 加強SSL設定
            'nocheckcertificate': True,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'skip_unavailable_fragments': True,
            'abort_on_unavailable_fragment': False
        }
        
        # 檢查是否需要使用 cookies 檔案
        # 先從用戶設定中讀取
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup.json")
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                    # 如果啟用了 cookies 檔案
                    if settings.get("use_cookies", False) and settings.get("cookies_file", ""):
                        cookies_file = settings["cookies_file"]
                        if os.path.exists(cookies_file):
                            ydl_opts['cookiefile'] = cookies_file
                            log(f"使用 cookies 檔案: {cookies_file}")
                        else:
                            log(f"找不到 cookies 檔案: {cookies_file}")
        except Exception as e:
            log(f"讀取 cookies 設定失敗: {str(e)}")
        
        # 根據平台特定的設定
        format_str = 'bestvideo+bestaudio/best'  # 預設格式
        
        # 如果平台信息已獲取，使用平台特定的格式設定
        if hasattr(self, 'platform_info') and self.platform_info and isinstance(self.platform_info, dict) and self.platform_info.get("name") != "未知":
            # 使用平台特定的下載選項
            platform_options = self.platform_info.get("download_options", {})
            if "format" in platform_options:
                format_str = platform_options["format"]
        
        # 根據格式選擇設定
        if "最高品質" in self.format_option:
            if "4K" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]'
            elif "1080P" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            elif "720P" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
            elif "480P" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
            elif "360P" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
        elif "僅影片" in self.format_option:
            ydl_opts['format'] = 'bestvideo/best'
        elif "僅音訊 (MP3)" in self.format_option:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif "僅音訊 (WAV)" in self.format_option:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }]
        else:  # 預設品質
            ydl_opts['format'] = 'best'
        
        # 是否自動合併
        if not self.auto_merge:
            ydl_opts['format'] = ydl_opts['format'].replace('+', '/')
            
        # 根據重試次數調整額外選項
        if self.retry_count > 0:
            # 在重試時使用更寬鬆的設定
            ydl_opts['format'] = 'best'  # 使用最簡單的格式選項
            
        if self.retry_count > 1:
            # 在第三次嘗試時使用最低解析度
            ydl_opts['format'] = 'worst'
            
        return ydl_opts
        
    def fallback_download_method(self):
        """備用下載方法，用於處理困難的影片"""
        try:
            self.progress.emit(f"正在使用備用下載方法...", 0, "--", "--")
            
            # 使用完全不同的設定
            ydl_opts = {
                'outtmpl': os.path.join(self.output_path, f'{self.prefix}%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'format': 'best',  # 使用最佳品質，通常更穩定
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 60,
                'retries': 10,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,  # 跳過不可用片段
                'abort_on_unavailable_fragment': False,  # 不因為片段不可用而中止
                'external_downloader': 'native',  # 使用原生下載器
                'hls_prefer_native': True,  # 優先使用原生HLS下載
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Connection': 'keep-alive'
                }
            }
            
            # 根據重試次數調整選項
            if self.retry_count > 0:
                ydl_opts['format'] = 'best[height<=720]'  # 降低解析度
                
            if self.retry_count > 1:
                ydl_opts['format'] = 'best[height<=480]'  # 進一步降低解析度
                
            if self.retry_count > 2:
                ydl_opts['format'] = 'worst'  # 使用最低解析度
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.progress.emit("使用備用方法獲取影片資訊...", 0, "--", "--")
                info = ydl.extract_info(self.url, download=False)
                
                if info is None:
                    # 檢查是否為年齡限制錯誤
                    error_message = "無法獲取影片資訊，可能是無效連結或該影片已被移除"
                    self.progress.emit(f"備用方法失敗: {error_message}", 0, "--", "--")
                    raise Exception(error_message)
                
                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"開始備用下載: {title}", 0, "--", "--")
                
                if not self.is_cancelled:
                    ydl.download([self.url])
                    
                    # 構建下載的檔案路徑
                    file_ext = info.get('ext', 'mp4')
                    if "僅音訊 (MP3)" in self.format_option:
                        file_ext = 'mp3'
                    elif "僅音訊 (WAV)" in self.format_option:
                        file_ext = 'wav'
                        
                    safe_title = self.sanitize_filename(title)
                    file_path = os.path.join(self.output_path, f'{self.prefix}{safe_title}.{file_ext}')
                    
                    self.finished.emit(True, f"備用下載完成: {title}", file_path)
                    return True
                    
            return False
        except Exception as e:
            error_message = str(e)
            
            # 檢查是否為年齡限制錯誤
            if "age" in error_message.lower() and ("restrict" in error_message.lower() or "confirm" in error_message.lower()):
                error_message = "此影片有年齡限制，需要使用 cookies 進行驗證。請在設定中啟用 cookies 選項並選擇有效的 cookies.txt 檔案。"
            
            self.progress.emit(f"備用下載方法失敗: {error_message}", 0, "--", "--")
            raise Exception(error_message)
            
    def try_segment_download(self):
        """嘗試分段下載方法，用於處理卡住的下載"""
        try:
            self.progress.emit(f"正在嘗試分段下載...", 0, "--", "--")
            
            # 使用分段下載設定
            ydl_opts = {
                'outtmpl': os.path.join(self.output_path, f'{self.prefix}%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'format': 'best',
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 30,
                'retries': 5,
                'fragment_retries': 5,
                'skip_unavailable_fragments': True,
                'abort_on_unavailable_fragment': False,
                'external_downloader': 'aria2c',  # 使用aria2c下載器
                'external_downloader_args': [
                    '--min-split-size=1M',  # 最小分片大小
                    '--max-connection-per-server=16',  # 每個服務器最大連接數
                    '--split=16',  # 單檔案分片數
                    '--max-tries=5',  # 最大重試次數
                    '--timeout=120',  # 超時時間
                    '--connect-timeout=60',  # 連接超時
                    '--retry-wait=3'  # 重試等待時間
                ],
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.progress.emit("使用分段下載獲取影片資訊...", 0, "--", "--")
                info = ydl.extract_info(self.url, download=False)
                
                if info is None:
                    raise Exception("無法獲取影片資訊，可能是無效連結或該影片已被移除")
                
                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"開始分段下載: {title}", 0, "--", "--")
                
                if not self.is_cancelled:
                    ydl.download([self.url])
                    
                    # 構建下載的檔案路徑
                    file_ext = info.get('ext', 'mp4')
                    if "僅音訊 (MP3)" in self.format_option:
                        file_ext = 'mp3'
                    elif "僅音訊 (WAV)" in self.format_option:
                        file_ext = 'wav'
                        
                    safe_title = self.sanitize_filename(title)
                    file_path = os.path.join(self.output_path, f'{self.prefix}{safe_title}.{file_ext}')
                    
                    self.finished.emit(True, f"分段下載完成: {title}", file_path)
                    return True
                    
            return False
        except Exception as e:
            self.progress.emit(f"分段下載失敗: {str(e)}", 0, "--", "--")
            return False
    
    def progress_hook(self, d):
        """下載進度回調"""
        # 檢查是否暫停，如果是則等待
        self.check_pause()
        
        # 更新最後進度時間
        self.last_progress_time = time.time()
        
        if self.is_cancelled:
            raise Exception("下載已取消")
            
        if d['status'] == 'downloading':
            # 下載中
            try:
                # 計算下載進度
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                
                if total_bytes > 0:
                    percent = int(downloaded_bytes / total_bytes * 100)
                else:
                    percent = 0
                    
                # 下載速度
                speed = d.get('speed', 0)
                try:
                    if speed:
                        speed_str = self.format_size(speed) + "/s"
                        # 記錄下載速度歷史
                        self.download_speed_history.append(speed)
                        # 只保留最近10個速度記錄
                        if len(self.download_speed_history) > 10:
                            self.download_speed_history.pop(0)
                    else:
                        speed_str = "-- KB/s"
                except Exception as e:
                    log(f"格式化下載速度時發生錯誤: {str(e)}")
                    speed_str = "-- KB/s"
                    
                # 剩餘時間
                eta = d.get('eta', 0)
                if eta:
                    eta_str = self.format_time(eta)
                else:
                    eta_str = "--:--"
                    
                # 發送進度信號
                self.progress.emit(f"下載中: {percent}%", percent, speed_str, eta_str)
            except Exception as e:
                error_msg = f"處理進度時錯誤: {str(e)}"
                log(error_msg)  # 記錄到日誌
                self.progress.emit(error_msg, 0, "--", "--")
                
        elif d['status'] == 'finished':
            # 下載完成，可能需要後處理
            self.progress.emit("下載完成，正在處理...", 100, "--", "--")
            
        elif d['status'] == 'error':
            # 下載錯誤
            self.progress.emit(f"下載錯誤: {d.get('error', '未知錯誤')}", 0, "--", "--")
            
        elif d['status'] == 'fragment':
            # 片段下載中
            try:
                fragment_index = d.get('fragment_index', 0)
                fragment_count = d.get('fragment_count', 0)
                
                if fragment_count > 0:
                    percent = int(fragment_index / fragment_count * 100)
                    self.progress.emit(f"下載片段: {fragment_index}/{fragment_count} ({percent}%)", percent, "--", "--")
            except Exception as e:
                self.progress.emit(f"處理片段進度時出錯: {str(e)}", 0, "--", "--")
                
        elif d['status'] == 'merging formats':
            # 合併格式中
            try:
                filename = d.get('filename', '').split('/')[-1]
                self.progress.emit(f"正在合併檔案: {filename}", 90, "--", "--")
            except Exception as e:
                self.progress.emit(f"處理合併進度時出錯: {str(e)}", 90, "--", "--")
        
    def format_size(self, bytes):
        """格式化檔案大小"""
        try:
            if bytes is None or bytes < 0:
                return "0 B"
            if bytes < 1024:
                return f"{int(bytes)} B"
            elif bytes < 1024 * 1024:
                return f"{bytes/1024:.1f} KB"
            elif bytes < 1024 * 1024 * 1024:
                return f"{bytes/(1024*1024):.1f} MB"
            else:
                return f"{bytes/(1024*1024*1024):.1f} GB"
        except Exception as e:
            log(f"格式化檔案大小時發生錯誤: {str(e)}")
            return "-- B"
            
    def format_time(self, seconds):
        """格式化時間"""
        try:
            if seconds is None or seconds < 0:
                return "--:--"
            
            seconds = int(seconds)
            if seconds < 60:
                return f"0:{seconds:02d}"
            elif seconds < 3600:
                return f"{seconds//60}:{seconds%60:02d}"
            else:
                return f"{seconds//3600}:{(seconds%3600)//60:02d}:{seconds%60:02d}"
        except Exception as e:
            log(f"格式化時間時發生錯誤: {str(e)}")
            return "--:--"
    
    def sanitize_filename(self, filename):
        """清理檔案名稱，移除不合法字符"""
        # 移除 Windows 不允許的檔案名稱字符
        illegal_chars = r'[<>:"/\\|?*]'
        safe_name = re.sub(illegal_chars, '_', filename)
        
        # 截斷過長的檔案名稱
        if len(safe_name) > 200:
            safe_name = safe_name[:197] + "..."
            
        return safe_name
    
    def cancel(self):
        """取消下載"""
        self.is_cancelled = True
        # 如果線程處於暫停狀態，喚醒它以便結束
        if self.is_paused:
            self.resume()
            
    def pause(self):
        """暫停下載"""
        self.is_paused = True
        
    def resume(self):
        """繼續下載"""
        self.is_paused = False
        self.pause_condition.wakeAll()
        
    def check_pause(self):
        """檢查是否需要暫停，如果是則等待恢復信號"""
        if self.is_paused and not self.is_cancelled:
            self.progress.emit("下載已暫停", -1, "--", "--")
            self.pause_mutex.lock()
            self.pause_condition.wait(self.pause_mutex)
            self.pause_mutex.unlock()
            if not self.is_paused:  # 如果已恢復
                self.progress.emit("下載已恢復", -1, "--", "--")

    def check_download_stall(self):
        """檢查下載是否卡住"""
        if self.is_paused or self.is_cancelled:
            return
            
        current_time = time.time()
        # 如果超過設定的超時時間沒有進度更新
        if current_time - self.last_progress_time > self.progress_timeout:
            # 檢查下載速度是否長時間為0
            if len(self.download_speed_history) > 3:
                recent_speeds = self.download_speed_history[-3:]
                if all(speed == 0 or speed is None for speed in recent_speeds):
                    self.progress.emit("下載似乎卡住了，嘗試恢復...", -1, "--", "--")
                    self.handle_stalled_download()
    
    def handle_stalled_download(self):
        """處理卡住的下載"""
        # 停止當前下載
        self.is_cancelled = True
        
        # 等待一小段時間
        time.sleep(2)
        
        # 重置取消狀態
        self.is_cancelled = False
        
        # 增加重試次數
        self.retry_count += 1
        
        # 如果重試次數未超過最大值，重新開始下載
        if self.retry_count <= self.max_retries:
            self.progress.emit(f"自動重試下載 (第 {self.retry_count} 次)...", 0, "--", "--")
            # 重置進度時間
            self.last_progress_time = time.time()
            # 清空速度歷史
            self.download_speed_history = []
            
            # 根據重試次數選擇不同的下載方法
            try:
                success = False
                
                # 第一次重試：使用備用下載方法
                if self.retry_count == 1:
                    self.progress.emit("嘗試備用下載方法...", 0, "--", "--")
                    success = self.fallback_download_method()
                
                # 第二次重試：嘗試分段下載
                elif self.retry_count == 2:
                    self.progress.emit("嘗試分段下載方法...", 0, "--", "--")
                    success = self.try_segment_download()
                
                # 第三次重試：使用最低品質設定
                elif self.retry_count == 3:
                    self.progress.emit("嘗試使用最低品質下載...", 0, "--", "--")
                    # 修改下載選項為最低品質
                    self.format_option = "預設品質"
                    self.resolution = "360P"
                    success = self.fallback_download_method()
                
                # 如果所有方法都失敗
                if not success:
                    self.progress.emit("所有自動重試方法都失敗了", 0, "--", "--")
                    self.finished.emit(False, "下載卡住，所有自動重試方法都失敗了", "")
                    
            except Exception as e:
                self.last_error = str(e)
                self.last_error_traceback = traceback.format_exc()
                self.progress.emit(f"自動重試失敗: {str(e)}", 0, "--", "--")
                self.finished.emit(False, f"自動重試失敗: {str(e)}", "")
        else:
            # 重試次數已用完
            self.progress.emit("下載多次卡住，請手動重試", 0, "--", "--")
            self.finished.emit(False, "下載卡住，請手動重試", "")

class DownloadTab(QWidget):
    """下載頁籤"""
    
    def __init__(self, parent=None, download_path=None):
        """初始化"""
        super().__init__(parent)
        # 設定初始化標誌，避免在初始化時觸發不必要的事件
        self._is_initializing = True
        self.download_path = download_path or os.path.expanduser("~/Downloads")
        self.download_items = {}
        self.download_threads = {}  # 添加下載線程字典
        self.download_formats = {}  # 保存每個下載項目的格式選擇
        self.download_resolutions = {}  # 保存每個下載項目的解析度選擇
        self.max_concurrent_downloads = 2  # 預設最大同時下載數
        self.prefix_history = ["Per Nice-", "Per Best3-", "Per Best2-", "Per Best-", "Per-"]  # 預設前綴選項
        self.error_dialogs = {}  # 添加錯誤對話框字典，用於跟踪當前顯示的錯誤對話框
        self.format_dialogs = {}  # 添加格式選項對話框字典，用於跟踪當前顯示的格式選項對話框
        self.supported_platforms = get_supported_platforms()  # 獲取支援的平台列表
        self.init_ui()  # 先初始化UI
        self.load_settings()  # 再載入設定
        # 初始化完成
        self._is_initializing = False
    
    def set_download_path(self, new_path):
        """設置新的下載路徑"""
        if self.download_path != new_path:
            self.download_path = new_path
            self.path_edit.setText(new_path)
            log(f"下載路徑已更新為: {new_path}")
    
    def update_download_prefix(self, prefix):
        """更新下載檔名前綴"""
        if prefix:
            self.prefix_combo.setCurrentText(prefix)
            log(f"下載檔名前綴已更新為: {prefix}")
    
    def load_settings(self):
        """載入設定"""
        try:
            # 使用程式根目錄而非src目錄
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            settings_path = os.path.join(parent_dir, "setup.json")
            
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                    # 載入最大同時下載數
                    self.max_concurrent_downloads = settings.get("max_concurrent_downloads", 2)
                    
                    # 載入前綴歷史
                    saved_prefixes = settings.get("prefix_history", [])
                    if saved_prefixes:
                        # 合併預設前綴和已保存的前綴，去重
                        all_prefixes = self.prefix_history + saved_prefixes
                        self.prefix_history = list(dict.fromkeys(all_prefixes))  # 去重保持順序
                        
                    # 載入下載路徑
                    if "download_path" in settings and os.path.exists(settings["download_path"]):
                        self.download_path = settings["download_path"]
                        
                    # 載入當前選擇的格式
                    if "current_format" in settings:
                        format_index = self.format_combo.findText(settings["current_format"])
                        if format_index >= 0:
                            self.format_combo.setCurrentIndex(format_index)
                    
                    # 載入當前選擇的解析度
                    if "current_resolution" in settings:
                        resolution_index = self.resolution_combo.findText(settings["current_resolution"])
                        if resolution_index >= 0:
                            self.resolution_combo.setCurrentIndex(resolution_index)
                    
                    # 載入當前前綴
                    if "current_prefix" in settings and settings["current_prefix"]:
                        self.prefix_combo.setCurrentText(settings["current_prefix"])
                    
                    # 載入自動合併設定
                    if "auto_merge" in settings:
                        self.auto_merge_cb.setChecked(settings["auto_merge"])
                        
                    # 載入下載頁籤特定設定
                    if "download_tab" in settings:
                        download_tab_settings = settings["download_tab"]
                        
                        # 這裡可以添加更多下載頁籤特定的設定
                        
                    log(f"已從 {settings_path} 載入用戶設定")
            else:
                # 如果設定檔不存在，創建一個預設設定檔
                self.save_settings()
                log(f"創建預設用戶設定檔: {settings_path}")
        except Exception as e:
            log(f"載入設定失敗: {str(e)}")
    
    def save_settings(self):
        """保存設定"""
        try:
            # 使用 get_settings_path() 確保路徑一致
            settings_path = get_settings_path()
            
            # 讀取現有設定（如果存在）
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    try:
                        settings = json.load(f)
                    except:
                        settings = {}
            
            # 更新基本設定
            settings["max_concurrent_downloads"] = self.max_concurrent_downloads
            settings["prefix_history"] = self.prefix_history
            settings["download_path"] = self.download_path
            
            # 保存當前選擇的格式
            if hasattr(self, 'format_combo'):
                settings["current_format"] = self.format_combo.currentText()
                settings["default_format"] = self.format_combo.currentText()
            
            # 保存當前選擇的解析度
            if hasattr(self, 'resolution_combo'):
                settings["current_resolution"] = self.resolution_combo.currentText()
                settings["default_resolution"] = self.resolution_combo.currentText()
            
            # 保存當前前綴
            if hasattr(self, 'prefix_combo'):
                settings["current_prefix"] = self.prefix_combo.currentText()
                settings["default_prefix"] = self.prefix_combo.currentText()
            
            # 保存自動合併設定
            if hasattr(self, 'auto_merge_cb'):
                settings["auto_merge"] = self.auto_merge_cb.isChecked()
            
            # 保存下載頁籤特定設定
            if "download_tab" not in settings:
                settings["download_tab"] = {}
            
            # 保存設定
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            log(f"已保存用戶設定到: {settings_path}")
        except Exception as e:
            log(f"保存設定失敗: {str(e)}")
    
    def apply_settings(self, settings):
        """應用從設定頁面傳來的設定"""
        log("正在應用設定到下載頁面...")
        
        # 應用下載路徑設定
        if "download_path" in settings and settings["download_path"]:
            self.download_path = settings["download_path"]
            self.path_edit.setText(self.download_path)
            log(f"已更新下載路徑: {self.download_path}")
        
        # 應用最大同時下載數
        if "max_concurrent_downloads" in settings:
            self.max_concurrent_downloads = settings["max_concurrent_downloads"]
            self.max_downloads_spin.setValue(self.max_concurrent_downloads)
            # 更新URL輸入框高度
            line_height = 20  # 預估每行高度
            padding = 30     # 額外空間
            self.url_edit.setMinimumHeight(self.max_concurrent_downloads * line_height + padding)
            self.url_edit.setMaximumHeight(self.max_concurrent_downloads * line_height + padding)
            log(f"已更新最大同時下載數: {self.max_concurrent_downloads}")
        
        # 應用格式設定
        if "default_format" in settings:
            format_index = -1
            if settings["default_format"] == "最高品質":
                format_index = 0
            elif settings["default_format"] == "僅視頻 (無音頻)":
                format_index = 1
            elif settings["default_format"] == "僅音訊 (MP3)":
                format_index = 2
            
            if format_index >= 0:
                self.format_combo.setCurrentIndex(format_index)
                log(f"已更新下載格式: {settings['default_format']}")
        
        # 應用解析度設定
        if "default_resolution" in settings:
            resolution_index = self.resolution_combo.findText(settings["default_resolution"])
            if resolution_index >= 0:
                self.resolution_combo.setCurrentIndex(resolution_index)
                log(f"已更新解析度: {settings['default_resolution']}")
        
        # 應用自動合併設定
        if "auto_merge" in settings:
            self.auto_merge_cb.setChecked(settings["auto_merge"])
            log(f"已更新自動合併設定: {settings['auto_merge']}")
        
        # 應用檔名前綴設定
        if "default_prefix" in settings and settings["default_prefix"]:
            # 更新前綴下拉框
            current_prefix = settings["default_prefix"]
            
            # 檢查是否已存在於前綴歷史中
            if current_prefix not in self.prefix_history:
                self.prefix_history.insert(0, current_prefix)  # 添加到歷史記錄的開頭
                # 更新下拉框
                self.prefix_combo.clear()
                self.prefix_combo.addItems(self.prefix_history)
            
            self.prefix_combo.setCurrentText(current_prefix)
            log(f"已更新檔名前綴: {current_prefix}")
        
        # 保存更新後的設定
        self.save_settings()
        
        log("設定已成功應用到下載頁面")

    def init_ui(self):
        """初始化下載頁面UI"""
        main_layout = QVBoxLayout(self)
        
        # 創建頂部輸入區域
        input_group = QGroupBox("輸入影片連結")
        input_layout = QVBoxLayout(input_group)
        
        # URL輸入框 - 根據最大同時下載數動態調整高度
        url_layout = QVBoxLayout()
        url_label = QLabel(f"影片連結 (每行一個，最多同時下載 {self.max_concurrent_downloads} 個):")
        self.url_edit = QTextEdit()
        self.url_edit.setPlaceholderText("在這裡貼上一個或多個影片連結，每行一個\n支援的平台: YouTube, TikTok/抖音, Facebook, Instagram, Bilibili, X(Twitter)")
        
        # 動態調整高度 - 根據最大同時下載數
        line_height = 20  # 預估每行高度
        padding = 30     # 額外空間
        self.url_edit.setMinimumHeight(self.max_concurrent_downloads * line_height + padding)
        self.url_edit.setMaximumHeight(self.max_concurrent_downloads * line_height + padding)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_edit)
        
        # 新增：視頻標題顯示區
        self.title_label = QLabel("")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-weight: bold; color: #0066cc; margin: 5px 0;")
        
        # 新增：支援平台提示
        platform_layout = QHBoxLayout()
        platform_label = QLabel("支援平台:")
        platform_label.setStyleSheet("font-weight: bold;")
        platform_layout.addWidget(platform_label)
        
        # 添加支援的平台列表（可點擊）
        platform_urls = self.load_external_url_settings()
        
        for platform in self.supported_platforms:
            platform_key = platform.lower()
            if platform_key == "x":
                platform_key = "twitter"  # 確保X和Twitter使用同一個設定
                
            platform_link = QLabel(f"<a href='#'>{platform}</a>")
            platform_link.setStyleSheet("color: #0066cc; margin-right: 10px; text-decoration: underline;")
            platform_link.setToolTip(f"點擊開啟{platform}外部下載網站")
            
            # 連接點擊事件到外部下載網站
            platform_link.linkActivated.connect(lambda _, p=platform: self.open_external_download_site(None, f"https://{p.lower()}.com"))
            platform_layout.addWidget(platform_link)
        
        platform_layout.addStretch(1)
        
        input_layout.addLayout(url_layout)
        input_layout.addWidget(self.title_label)
        input_layout.addLayout(platform_layout)
        
        # 設定區域
        settings_layout = QHBoxLayout()
        
        # 左側設定
        left_settings = QVBoxLayout()
        
        # 格式選擇 - 移除不需要的音訊格式
        format_layout = QHBoxLayout()
        format_label = QLabel("下載格式:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["最高品質", "僅視頻 (無音頻)", "僅音訊 (MP3)"])
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo, 1)
        left_settings.addLayout(format_layout)
        
        # 解析度選擇
        resolution_layout = QHBoxLayout()
        resolution_label = QLabel("解析度:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["自動選擇最佳", "4K", "1080p", "720p", "480p", "360p", "240p"])
        resolution_layout.addWidget(resolution_label)
        resolution_layout.addWidget(self.resolution_combo, 1)
        left_settings.addLayout(resolution_layout)
        
        # 檔名前綴 - 改為下拉選單，調整寬度
        prefix_layout = QHBoxLayout()
        prefix_label = QLabel("檔名前綴:")
        self.prefix_combo = QComboBox()
        self.prefix_combo.setEditable(True)
        self.prefix_combo.addItems(self.prefix_history)
        self.prefix_combo.setCurrentText(self.prefix_history[0] if self.prefix_history else "")
        self.prefix_combo.currentTextChanged.connect(self.on_prefix_changed)
        # 設定最大寬度，避免過長
        self.prefix_combo.setMaximumWidth(150)
        
        # 添加清空前綴按鈕
        self.clear_prefix_btn = QPushButton("清空前綴")
        self.clear_prefix_btn.clicked.connect(self.clear_prefix)
        
        # 添加刪除選中前綴按鈕
        self.remove_prefix_btn = QPushButton("刪除前綴")
        self.remove_prefix_btn.clicked.connect(self.remove_selected_prefix)
        self.remove_prefix_btn.setToolTip("從歷史記錄中刪除當前選中的前綴")
        
        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_combo)
        prefix_layout.addWidget(self.clear_prefix_btn)
        prefix_layout.addWidget(self.remove_prefix_btn)
        prefix_layout.addStretch(1)  # 添加彈性空間，使前綴框不佔滿整行
        left_settings.addLayout(prefix_layout)
        
        settings_layout.addLayout(left_settings)
        
        # 右側設定
        right_settings = QVBoxLayout()
        
        # 下載路徑 - 確保完整顯示
        path_layout = QHBoxLayout()
        path_label = QLabel("下載路徑:")
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.download_path)
        self.path_edit.setMinimumWidth(300)  # 設定最小寬度
        self.browse_btn = QPushButton("瀏覽...")
        self.browse_btn.clicked.connect(self.browse_path)
        # 開啟資料夾按鈕
        self.open_folder_btn = QPushButton("📂 開啟資料夾")
        self.open_folder_btn.clicked.connect(lambda: self.open_download_folder())
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit, 1)
        path_layout.addWidget(self.browse_btn)
        path_layout.addWidget(self.open_folder_btn)
        right_settings.addLayout(path_layout)
        
        # 合併音視頻選項
        merge_layout = QHBoxLayout()
        self.auto_merge_cb = QCheckBox("自動合併音頻和視頻 (高畫質影片將始終合併)")
        self.auto_merge_cb.setChecked(True)
        
        # 新增：最大同時下載數設定
        max_downloads_label = QLabel("最大同時下載數:")
        self.max_downloads_spin = QSpinBox()
        self.max_downloads_spin.setMinimum(1)
        self.max_downloads_spin.setMaximum(10)
        self.max_downloads_spin.setValue(self.max_concurrent_downloads)
        self.max_downloads_spin.valueChanged.connect(self.on_max_downloads_changed)
        
        merge_layout.addWidget(self.auto_merge_cb)
        merge_layout.addStretch(1)
        merge_layout.addWidget(max_downloads_label)
        merge_layout.addWidget(self.max_downloads_spin)
        right_settings.addLayout(merge_layout)
        
        # 加入空白區域對齊佈局
        right_settings.addStretch(1)
        
        settings_layout.addLayout(right_settings)
        
        input_layout.addLayout(settings_layout)
        
        main_layout.addWidget(input_group)
        
        # 創建控制按鈕區 - 添加視覺分隔線和間距
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: #cccccc;")
        main_layout.addWidget(divider)
        main_layout.addSpacing(10)
        
        control_layout = QHBoxLayout()
        
        # 美化按鈕樣式
        button_style = """
        QPushButton {
            background-color: #0078d7;
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #00adef;
        }
        QPushButton:pressed {
            background-color: #005fa3;
        }
        """
        
        self.download_btn = QPushButton("開始下載")
        self.download_btn.setStyleSheet(button_style)
        self.download_btn.clicked.connect(self.start_download)
        
        self.clear_completed_btn = QPushButton("清空已下載成功的檔案")
        self.clear_completed_btn.setStyleSheet(button_style.replace("background-color: #0078d7", "background-color: #5cb85c"))
        self.clear_completed_btn.clicked.connect(self.clear_completed_downloads)
        
        # 移除刪除選取和跳過錯誤任務按鈕
        
        # 創建總進度條
        total_label = QLabel("總進度:")
        self.total_progress = QProgressBar()
        self.total_progress.setMinimum(0)
        self.total_progress.setMaximum(100)
        self.total_progress.setValue(0)
        self.total_progress.setTextVisible(True)
        self.total_progress.setFormat("總進度: 0% (0/0)")
        self.total_progress.setMinimumWidth(300)  # 設置最小寬度，使進度條更明顯
        self.total_progress.setStyleSheet("""
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
        
        # 添加按鈕和總進度條到控制佈局
        control_layout.addWidget(self.download_btn)
        control_layout.addWidget(self.clear_completed_btn)
        control_layout.addStretch(1)
        control_layout.addWidget(total_label)
        control_layout.addWidget(self.total_progress)
        
        main_layout.addLayout(control_layout)
        
        # 創建下載進度區域
        progress_group = QGroupBox("下載進度")
        progress_layout = QVBoxLayout(progress_group)
        
        # 建立捲動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.download_layout = QVBoxLayout(scroll_content)
        self.download_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(scroll_content)
        
        progress_layout.addWidget(scroll_area)
        
        main_layout.addWidget(progress_group)
        
        # 儲存項目字典
        self.download_items = {}
        
        # 添加示範下載項目 (調試用)
        # self.demo_downloads()
    
    def on_max_downloads_changed(self, value):
        """最大同時下載數變更"""
        self.max_concurrent_downloads = value
        
        # 動態調整輸入框高度
        line_height = 20
        padding = 30
        self.url_edit.setMinimumHeight(value * line_height + padding)
        self.url_edit.setMaximumHeight(value * line_height + padding)
        
        # 更新標籤文字
        for widget in self.findChildren(QLabel):
            if "影片連結" in widget.text():
                widget.setText(f"影片連結 (每行一個，最多同時下載 {value} 個):")
                break
        
        # 保存設定
        self.save_settings()

    def on_prefix_changed(self, text):
        """前綴變更時處理"""
        # 避免在程式初始化或清空前綴時觸發大量日誌
        if hasattr(self, '_is_initializing') and self._is_initializing:
            return
            
        if not text:
            # 如果前綴為空，不添加到歷史記錄
            log("清空前綴")
            return
            
        if text in self.prefix_history:
            # 如果前綴已存在於歷史記錄中，將其移到最前面
            self.prefix_history.remove(text)
            self.prefix_history.insert(0, text)
        else:
            # 將新前綴添加到歷史記錄
            self.prefix_history.insert(0, text)
        
        # 限制歷史記錄長度
        if len(self.prefix_history) > 10:
            self.prefix_history = self.prefix_history[:10]
            
        # 更新下拉選單，但避免觸發事件循環
        self.prefix_combo.blockSignals(True)
        current_text = text
        self.prefix_combo.clear()
        self.prefix_combo.addItems(self.prefix_history)
        self.prefix_combo.setCurrentText(current_text)
        self.prefix_combo.blockSignals(False)
        
        # 更新所有現有下載項目的檔名前綴
        updated_count = 0
        for filename, item_data in self.download_items.items():
            if 'thread' in item_data and item_data['thread'] is not None:
                item_data['thread'].prefix = text
                item_data['prefix'] = text
                updated_count += 1
                
        if updated_count > 0:
            log(f"已更新 {updated_count} 個下載項目的檔名前綴為: {text}")
        
        # 立即保存前綴設定到setup.json
        try:
            settings_path = get_settings_path()
            
            # 讀取現有設定（如果存在）
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    try:
                        settings = json.load(f)
                    except:
                        settings = {}
            
            # 更新前綴設定
            settings["current_prefix"] = text
            settings["prefix_history"] = self.prefix_history
        
            # 保存設定
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            log(f"已保存檔案前綴設定: {text}")
        except Exception as e:
            log(f"保存檔案前綴設定失敗: {str(e)}")
        
        # 保存其他設定
        self.save_settings()

    def skip_error_tasks(self):
        """跳過錯誤任務"""
        error_items = []
        
        # 找出所有錯誤任務
        for filename, item in list(self.download_items.items()):
            if "錯誤" in item['status_label'].text() or "失敗" in item['status_label'].text():
                error_items.append(filename)
        
        if not error_items:
            QMessageBox.information(self, "資訊", "沒有發現錯誤任務")
            return
            
        # 刪除錯誤任務
        for filename in error_items:
            self.delete_item(filename)
            
        QMessageBox.information(self, "完成", f"已跳過 {len(error_items)} 個錯誤任務")

    def open_download_folder(self):
        """打開下載資料夾"""
        path = self.path_edit.text()
        if os.path.exists(path):
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', path])
            else:  # linux
                subprocess.run(['xdg-open', path])
        else:
            QMessageBox.warning(self, "資料夾不存在", f"路徑 {path} 不存在，請選擇有效的下載路徑。")
    
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
        """創建下載項目 UI 元件"""
        # 項目容器
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(10, 10, 10, 10)
        
        # 如果parent_layout是None，創建一個新的佈局
        if parent_layout is None:
            parent_layout = QVBoxLayout()
            parent_layout.setContentsMargins(0, 0, 0, 0)
        
        # 背景和陰影效果
        item_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # 影片標題和基本信息
        info_layout = QHBoxLayout()
        
        # 平台圖示（預設為通用圖示）
        icon_label = QLabel("▶")
        icon_label.setObjectName(f"icon_{filename}")
        icon_label.setStyleSheet("color: #0066cc; font-size: 14pt; font-weight: bold;")
        info_layout.addWidget(icon_label)
        
        # 將顯示名稱從預設檔名改為原影片標題
        title_label = QLabel(filename)
        title_label.setObjectName(f"title_{filename}")
        title_label.setStyleSheet("font-weight: bold; color: #0066cc; font-size: 10pt;")
        info_layout.addWidget(title_label)
        
        info_layout.addStretch(1)
        
        # 狀態信息
        status_label = QLabel(status)
        status_label.setObjectName(f"status_{filename}")
        status_label.setStyleSheet("color: #666666;")
        info_layout.addWidget(status_label)
        
        item_layout.addLayout(info_layout)
        
        # 進度條和控制區域
        progress_layout = QHBoxLayout()
        
        # 進度條 - 修改文字顯示方式，確保不被遮擋
        progress_bar = QProgressBar()
        progress_bar.setObjectName(f"progress_{filename}")
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(progress)
        progress_bar.setFormat("%p% 完成")  # 設定進度條文字格式
        progress_bar.setAlignment(Qt.AlignCenter)  # 文字置中
        progress_bar.setTextVisible(True)  # 確保文字可見
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                background-color: #f5f5f5;
                color: black;  /* 文字顏色設為黑色，增加對比度 */
                font-weight: bold;  /* 文字加粗 */
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(progress_bar, 3)  # 進度條佔據更多空間
        
        # 預估剩餘時間和下載速度
        info_widget = QWidget()
        info_box = QHBoxLayout(info_widget)
        info_box.setContentsMargins(0, 0, 0, 0)
        
        eta_label = QLabel(f"ETA: {eta}")
        eta_label.setObjectName(f"eta_{filename}")
        eta_label.setStyleSheet("color: #666666; padding-left: 10px;")
        speed_label = QLabel(f"{speed}")
        speed_label.setObjectName(f"speed_{filename}")
        speed_label.setStyleSheet("color: #666666;")
        
        info_box.addWidget(speed_label)
        info_box.addWidget(eta_label)
        
        progress_layout.addWidget(info_widget, 1)  # 信息佔據較少空間
        
        # 控制按鈕
        control_widget = QWidget()
        control_box = QHBoxLayout(control_widget)
        control_box.setContentsMargins(0, 0, 0, 0)
        
        pause_btn = QPushButton("暫停")
        pause_btn.setObjectName(f"pause_btn_{filename}")
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
        
        # 新增：重試按鈕
        retry_btn = QPushButton("重試")
        retry_btn.setObjectName(f"retry_btn_{filename}")
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
        retry_btn.setVisible(False)  # 預設隱藏，只在錯誤時顯示
        
        # 新增：外部下載按鈕
        external_btn = QPushButton("外部下載")
        external_btn.setObjectName(f"external_btn_{filename}")
        external_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 3px;
                padding: 3px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        external_btn.clicked.connect(lambda: self.open_external_download_site(filename))
        external_btn.setVisible(False)  # 預設隱藏，只在錯誤時顯示
        
        delete_btn = QPushButton("❌")
        delete_btn.setObjectName(f"delete_btn_{filename}")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        
        control_box.addWidget(pause_btn)
        control_box.addWidget(retry_btn)
        control_box.addWidget(external_btn)
        control_box.addWidget(delete_btn)
        
        pause_btn.clicked.connect(lambda: self.toggle_pause_item(filename))
        retry_btn.clicked.connect(lambda: self.retry_download(filename))
        delete_btn.clicked.connect(lambda: self.delete_item(filename))
        
        progress_layout.addWidget(control_widget)
        
        item_layout.addLayout(progress_layout)
        
        # 儲存項目元件引用
        self.download_items[filename] = {
            'widget': item_widget,
            'progress_bar': progress_bar,
            'status_label': status_label,
            'pause_btn': pause_btn,
            'retry_btn': retry_btn,
            'external_btn': external_btn,
            'delete_btn': delete_btn,
            'eta_label': eta_label,
            'speed_label': speed_label,
            'title_label': title_label,
            'icon_label': icon_label,
            'is_paused': False
        }
        
        parent_layout.addWidget(item_widget)
        return item_widget

    def toggle_pause_item(self, filename):
        """暫停/繼續特定下載項目"""
        if filename not in self.download_items:
            return
            
        item_data = self.download_items[filename]
        pause_btn = item_data['pause_btn']
        status_label = item_data['status_label']
        icon_label = item_data['icon_label']
        
        # 獲取下載線程
        if filename in self.download_threads:
            thread = self.download_threads[filename]
            
            if pause_btn.text() == "暫停":
                # 暫停下載
                pause_btn.setText("繼續")
                status_label.setText("已暫停")
                icon_label.setText("⏸")
                icon_label.setStyleSheet("color: #f0ad4e; font-size: 14pt;")
                
                # 實際暫停線程
                if hasattr(thread, 'pause'):
                    thread.pause()
                    
                # 更新進度條樣式
                item_data['progress_bar'].setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #cccccc;
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
            else:
                # 繼續下載
                pause_btn.setText("暫停")
                status_label.setText("進行中")
                icon_label.setText("▶")
                icon_label.setStyleSheet("color: #ff0000; font-size: 14pt; font-weight: bold;")
                
                # 實際恢復線程
                if hasattr(thread, 'resume'):
                    thread.resume()
                    
                # 更新進度條樣式
                item_data['progress_bar'].setStyleSheet("""
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

    def delete_item(self, filename):
        """刪除下載項目"""
        if filename in self.download_items:
            try:
                # 取消下載線程
                if 'thread' in self.download_items[filename]:
                    thread = self.download_items[filename]['thread']
                    if hasattr(thread, 'cancel'):
                        thread.cancel()
                
                # 從UI中移除小部件
                item_widget = self.download_items[filename]['widget']
                self.download_layout.removeWidget(item_widget)
                item_widget.setParent(None)
                item_widget.deleteLater()
                
                # 從字典中移除項目
                del self.download_items[filename]
                
                # 更新總進度
                self.update_total_progress()
                
                log(f"已刪除下載項目: {filename}")
            except Exception as e:
                log(f"刪除項目時出錯: {str(e)}")
                QMessageBox.warning(self, "錯誤", f"刪除項目時出錯: {str(e)}")

    def start_download(self):
        """開始下載"""
        # 獲取URL列表
        urls = self.url_edit.toPlainText().strip().split("\n")
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            QMessageBox.warning(self, "錯誤", "請輸入至少一個影片連結")
            return
            
        # 檢查下載路徑是否存在
        if not os.path.exists(self.download_path):
            try:
                os.makedirs(self.download_path)
                log(f"已創建下載路徑: {self.download_path}")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"無法創建下載路徑: {str(e)}")
                return
        
        # 檢查當前下載數量是否已達上限
        current_downloads = len(self.download_threads)
        if current_downloads >= self.max_concurrent_downloads:
            QMessageBox.warning(
                self, 
                "下載數量已達上限", 
                f"當前已有 {current_downloads} 個下載任務在進行中，已達到最大同時下載數 {self.max_concurrent_downloads}。\n\n請等待部分下載完成後再添加新的下載任務。"
            )
            return
            
        # 計算可添加的下載數量
        available_slots = self.max_concurrent_downloads - current_downloads
        urls_to_download = urls[:available_slots]
        
        if len(urls) > available_slots:
            QMessageBox.information(
                self,
                "部分下載已添加",
                f"已添加 {len(urls_to_download)} 個下載任務。\n\n剩餘的 {len(urls) - available_slots} 個任務將在當前下載完成後自動開始。"
            )
        
        log(f"開始下載 {len(urls_to_download)} 個影片...")
        
        # 為每個URL創建下載項目
        for i, url in enumerate(urls_to_download):
            # 識別平台
            platform_name = identify_platform(url)
            
            # 創建唯一的檔案名，包含平台信息
            if platform_name == "未知":
                filename = f"未知來源影片_{len(self.download_threads) + i + 1}.mp4"
            else:
                filename = f"{platform_name}影片_{len(self.download_threads) + i + 1}.mp4"
            
            # 創建下載項目容器
            item_container = QFrame()
            item_container.setObjectName(f"download_item_{filename}")
            item_container.setFrameStyle(QFrame.StyledPanel)
            item_container.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    margin: 2px;
                }
            """)
            
            # 為容器創建佈局
            container_layout = QVBoxLayout(item_container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            # 創建下載項目
            self.create_download_item(container_layout, filename, 0, "--", "--", "準備中...")
            
            # 將容器添加到下載佈局
            self.download_layout.addWidget(item_container)
            
            # 創建URL輸入框（隱藏）
            url_input = QLineEdit()
            url_input.setObjectName(f"url_input_{filename}")
            url_input.setText(url)
            url_input.hide()
            self.download_layout.addWidget(url_input)
            
            # 開始下載
            self.start_download_for_item(filename, url)
        
        # 注意：不立即清除URL輸入框，等待下載成功後才清除
        # 更新總進度
        self.update_total_progress()

    def start_download_for_item(self, filename, url):
        """為特定項目啟動下載線程"""
        try:
            # 獲取當前選擇的格式和解析度
            format_option = self.format_combo.currentText()
            resolution = self.resolution_combo.currentText()
            
            # 獲取前綴
            prefix = self.prefix_combo.currentText() if self.prefix_combo.currentText() else ""
            
            # 獲取自動合併設定
            auto_merge = self.auto_merge_cb.isChecked()
            
            # 保存該項目的格式和解析度設定
            self.download_formats[filename] = format_option
            self.download_resolutions[filename] = resolution
            
            # 保存URL和平台信息
            self.download_items[filename]['url'] = url
            self.download_items[filename]['platform_info'] = identify_platform(url)
            
            # 創建下載線程
            thread = DownloadThread(
                url,
                self.download_path,
                format_option,
                resolution,
                prefix,
                auto_merge
            )
            
            # 連接信號
            thread.progress.connect(lambda message, percent, speed, eta: 
                                   self.update_download_progress(filename, message, percent, speed, eta))
            thread.finished.connect(lambda success, message, file_path: 
                                   self.download_finished(filename, success, message, file_path))
            thread.platform_detected.connect(lambda platform, url, f=filename: 
                                           self.on_platform_detected(f, platform, url))
            
            # 保存線程
            self.download_threads[filename] = thread
            
            # 同步到進度頁籤
            if hasattr(self.parent(), 'progress_tab'):
                # 添加到進度標籤頁
                progress_item = self.parent().progress_tab.add_download_item(filename, url, thread)
                
                # 連接進度信號到進度標籤頁
                thread.progress.connect(lambda message, percent, speed, eta: 
                                      self.parent().progress_tab.update_download_progress(filename, message, percent, speed, eta))
                
                # 連接完成信號到進度標籤頁
                thread.finished.connect(lambda success, message, file_path: 
                                      self.parent().progress_tab.download_finished(filename, success, message, file_path))
                
                # 日誌記錄
                log(f"已將下載項目添加到進度標籤頁: {filename}")
            
            # 啟動線程
            thread.start()
            
            log(f"已啟動下載線程: {filename}, URL: {url}")
        except Exception as e:
            log(f"啟動下載線程失敗: {str(e)}")
            self.show_error_dialog(filename, f"啟動下載失敗: {str(e)}")

    def on_platform_detected(self, filename, platform, url):
        """處理平台檢測結果"""
        try:
            if filename in self.download_items:
                # 更新平台信息
                self.download_items[filename]['platform_info'] = platform
                
                # 設置平台特定的圖標和顏色
                icon_label = self.download_items[filename]['icon_label']
                title_label = self.download_items[filename]['title_label']
                
                if platform == "YouTube":
                    icon_label.setText("▶")
                    icon_label.setStyleSheet("color: #ff0000; font-size: 14pt; font-weight: bold;")
                elif platform == "TikTok" or platform == "抖音":
                    icon_label.setText("🎵")
                    icon_label.setStyleSheet("color: #000000; font-size: 14pt; font-weight: bold;")
                elif platform == "Facebook":
                    icon_label.setText("📘")
                    icon_label.setStyleSheet("color: #1877f2; font-size: 14pt; font-weight: bold;")
                elif platform == "Instagram":
                    icon_label.setText("📷")
                    icon_label.setStyleSheet("color: #e4405f; font-size: 14pt; font-weight: bold;")
                elif platform == "Bilibili":
                    icon_label.setText("📺")
                    icon_label.setStyleSheet("color: #00a1d6; font-size: 14pt; font-weight: bold;")
                elif platform == "X":
                    icon_label.setText("🐦")
                    icon_label.setStyleSheet("color: #1da1f2; font-size: 14pt; font-weight: bold;")
                elif platform == "未知":
                    icon_label.setText("❓")
                    icon_label.setStyleSheet("color: #999999; font-size: 14pt; font-weight: bold;")
                    title_label.setStyleSheet("font-weight: bold; color: #999999; font-size: 10pt;")
                else:
                    icon_label.setText("▶")
                    icon_label.setStyleSheet("color: #0066cc; font-size: 14pt; font-weight: bold;")
                
                # 更新初始狀態顯示
                if platform == "未知":
                    self.download_items[filename]['status_label'].setText("未知來源影片下載中...")
                    self.download_items[filename]['title_label'].setText(f"未知來源影片_{filename}")
                else:
                    self.download_items[filename]['status_label'].setText(f"{platform}影片下載中...")
                    self.download_items[filename]['title_label'].setText(f"{platform}影片_{filename}")
                
                log(f"檢測到平台: {platform}, 檔案: {filename}")
        except Exception as e:
            log(f"處理平台檢測時出錯: {str(e)}")

    def update_video_info(self, message, url):
        """更新視頻信息"""
        try:
            # 如果訊息中包含影片標題信息
            if "開始下載:" in message and ":" in message:
                title = message.split(":", 1)[1].strip()
                
                # 更新對應下載項目的標題
                for filename, item in self.download_items.items():
                    if item.get('url') == url:
                        # 獲取平台信息
                        platform_name = item.get('platform_info', "未知")
                        
                        # 格式化標題：平台名稱 + 影片標題
                        if platform_name == "未知":
                            formatted_title = f"未知來源: {title}"
                        else:
                            formatted_title = f"{platform_name}: {title}"
                        
                        item['title_label'].setText(formatted_title)
                        break
            elif "Error" in message or "錯誤" in message or "失敗" in message:
                # 處理錯誤情況
                for filename, item in self.download_items.items():
                    if item.get('url') == url:
                        # 獲取平台信息
                        platform_name = item.get('platform_info', "未知")
                        
                        error_status = f"{platform_name}影片下載失敗 ❌"
                        item['status_label'].setText(error_status)
                        item['progress_bar'].setStyleSheet("""
                            QProgressBar::chunk { background-color: #d9534f; }
                        """)
                        item['retry_btn'].setVisible(True)
                        item['icon_label'].setText("❌")
                        item['icon_label'].setStyleSheet("color: #d9534f; font-size: 14pt;")
                        break
        except Exception as e:
            log(f"更新視頻信息時出錯: {str(e)}")

    def update_download_progress(self, filename, message, percent, speed, eta):
        """更新下載進度"""
        if filename in self.download_items:
            # 更新進度條
            try:
                if percent >= 0 and percent <= 100:
                    self.download_items[filename]['progress_bar'].setValue(percent)
                else:
                    # 如果進度值超出範圍，設為0
                    self.download_items[filename]['progress_bar'].setValue(0)
            except Exception as e:
                log(f"更新進度條時發生錯誤: {str(e)}")
            
            # 更新狀態文字
            try:
                if message is not None:
                    # 獲取平台信息
                    platform_name = self.download_items[filename].get('platform_info', "未知")
                    
                    # 格式化狀態消息
                    if "下載中" in message or "downloading" in message.lower():
                        status_text = f"{platform_name}影片下載中: {percent}%"
                    elif "處理中" in message or "合併" in message or "merging" in message.lower() or "processing" in message.lower():
                        status_text = f"{platform_name}影片處理中: {percent}%"
                    elif "已完成" in message or "完成" in message or "finished" in message.lower():
                        status_text = f"{platform_name}影片已完成 ✅"
                    elif "失敗" in message or "錯誤" in message or "error" in message.lower() or "failed" in message.lower():
                        status_text = f"{platform_name}影片下載失敗 ❌"
                    elif "獲取" in message or "extracting" in message.lower():
                        status_text = f"{platform_name}影片獲取資訊中..."
                    else:
                        status_text = message
                    
                    self.download_items[filename]['status_label'].setText(status_text)
                else:
                    # 獲取平台信息
                    platform_name = self.download_items[filename].get('platform_info', "未知")
                    self.download_items[filename]['status_label'].setText(f"{platform_name}影片下載中...")
            except Exception as e:
                log(f"更新狀態文字時發生錯誤: {str(e)}")
            
            # 更新下載速度和剩餘時間
            try:
                self.download_items[filename]['speed_label'].setText(f"速度: {speed}")
                self.download_items[filename]['eta_label'].setText(f"ETA: {eta}")
            except Exception as e:
                log(f"更新速度和ETA時發生錯誤: {str(e)}")
                self.download_items[filename]['speed_label'].setText("速度: --")
                self.download_items[filename]['eta_label'].setText("ETA: --")
            
            # 設定進度條顏色和文字（根據狀態調整）
            if "失敗" in message or "錯誤" in message:
                self.download_items[filename]['progress_bar'].setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #cccccc;
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
                # 顯示重試按鈕
                self.download_items[filename]['retry_btn'].setVisible(True)
                # 更新圖示
                self.download_items[filename]['icon_label'].setText("❌")
                self.download_items[filename]['icon_label'].setStyleSheet("color: #d9534f; font-size: 14pt;")
            elif "暫停" in message:
                self.download_items[filename]['progress_bar'].setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #cccccc;
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
                # 更新圖示
                self.download_items[filename]['icon_label'].setText("⏸")
                self.download_items[filename]['icon_label'].setStyleSheet("color: #f0ad4e; font-size: 14pt;")
            elif "完成" in message:
                self.download_items[filename]['progress_bar'].setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #cccccc;
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
                # 更新圖示
                self.download_items[filename]['icon_label'].setText("✓")
                self.download_items[filename]['icon_label'].setStyleSheet("color: #5cb85c; font-size: 14pt;")
            elif "合併" in message or "處理" in message:
                # 特別處理合併和後處理進度
                self.download_items[filename]['progress_bar'].setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #cccccc;
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
                # 更新圖示
                self.download_items[filename]['icon_label'].setText("🔄")
                self.download_items[filename]['icon_label'].setStyleSheet("color: #5bc0de; font-size: 14pt;")
                
                # 設定進度條顯示模式
                if percent > 0:
                    # 有明確進度時顯示進度
                    self.download_items[filename]['progress_bar'].setRange(0, 100)
                    self.download_items[filename]['progress_bar'].setValue(percent)
                else:
                    # 沒有明確進度時顯示不確定模式
                    self.download_items[filename]['progress_bar'].setRange(0, 0)  # 不確定模式
            else:
                self.download_items[filename]['progress_bar'].setStyleSheet("""
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
                # 更新圖示
                self.download_items[filename]['icon_label'].setText("▶")
                self.download_items[filename]['icon_label'].setStyleSheet("color: #ff0000; font-size: 14pt; font-weight: bold;")
                
            # 更新總進度
            self.update_total_progress()
            
            # 每隔10%記錄一次日誌
            if percent % 10 == 0 and percent > 0:
                try:
                    log(f"下載進度 [{filename}]: {percent}%, 速度: {speed}, ETA: {eta}")
                except Exception as e:
                    log(f"記錄下載進度時發生錯誤: {str(e)}")
                    log(f"下載進度 [{filename}]: {percent}%")

    def download_finished(self, filename, success, message, file_path):
        """下載完成處理"""
        log(f"下載完成: {filename}, 成功: {success}, 訊息: {message}")
        
        # 獲取對應的下載項
        download_item = self.findChild(QFrame, f"download_item_{filename}")
        if not download_item:
            log(f"找不到下載項: {filename}，可能已被刪除")
            
            # 清理下載線程
            if filename in self.download_threads:
                try:
                    thread = self.download_threads.pop(filename)
                    thread.deleteLater()
                except Exception as e:
                    log(f"清理下載線程時發生錯誤: {str(e)}")
            
            # 如果下載成功，仍然通知已下載檔案頁面更新
            if success and file_path:
                self.notify_download_completed(file_path)
                
            return
        
        # 檢查是否為 YT_DLP_FAILURE 錯誤
        if not success and message.startswith("YT_DLP_FAILURE:"):
            log(f"檢測到 YT_DLP_FAILURE 錯誤，顯示特殊對話框: {message}")
            # 延遲顯示特殊錯誤對話框，確保UI更新完成
            QTimer.singleShot(500, lambda: self.show_yt_dlp_failure_dialog(filename, message))
            # 延遲顯示外部下載按鈕
            QTimer.singleShot(1000, lambda: self.show_external_download_button(filename))
            
            # 清理下載線程
            try:
                # 確保線程已經結束
                if filename in self.download_threads:
                    if self.download_threads[filename].isRunning():
                        log(f"等待下載線程結束: {filename}")
                        self.download_threads[filename].cancel()
                        self.download_threads[filename].wait(1000)  # 等待最多1秒
                        
                    # 從字典中移除線程
                    thread = self.download_threads.pop(filename)
                    thread.deleteLater()  # 確保線程對象被正確刪除
                    log(f"已清理下載線程: {filename}")
            except Exception as e:
                log(f"清理下載線程時發生錯誤: {str(e)}")
                
            # 更新UI
            progress_bar = download_item.findChild(QProgressBar, f"progress_{filename}")
            status_label = download_item.findChild(QLabel, f"status_{filename}")
            eta_label = download_item.findChild(QLabel, f"eta_{filename}")
            speed_label = download_item.findChild(QLabel, f"speed_{filename}")
            
            # 獲取平台信息
            platform_name = self.download_items[filename].get('platform_info', "未知")
                
            # 更新為錯誤狀態
            progress_bar.setValue(0)
            status_label.setText(f"{platform_name}影片下載失敗 ❌")
            status_label.setStyleSheet("color: red; font-weight: bold;")
            eta_label.setText("--")
            speed_label.setText("--")
            
            # 更新圖標為錯誤狀態
            icon_label = download_item.findChild(QLabel, f"icon_{filename}")
            if icon_label:
                icon_label.setText("❌")
                icon_label.setStyleSheet("color: #d9534f; font-size: 14pt; font-weight: bold;")
            
            # 更新進度條為紅色
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
                    background-color: #d9534f;
                    border-radius: 5px;
                }
            """)
            
            # 更新按鈕狀態
            pause_btn = download_item.findChild(QPushButton, f"pause_btn_{filename}")
            if pause_btn:
                pause_btn.setEnabled(False)
                pause_btn.setText("失敗")
            
            delete_btn = download_item.findChild(QPushButton, f"delete_btn_{filename}")
            if delete_btn:
                delete_btn.setText("刪除")
            
            return
        
        # 處理其他情況
        if success:
            # 下載成功
            # 檢查檔案路徑是否存在，如果不存在則嘗試在下載目錄中查找
            actual_file_path = file_path
            if not file_path or not os.path.exists(file_path):
                # 嘗試在下載目錄中查找可能的檔案
                try:
                    files = os.listdir(self.download_path)
                    for file in files:
                        if file.startswith(filename.replace('.mp4', '')) or filename.replace('.mp4', '') in file:
                            actual_file_path = os.path.join(self.download_path, file)
                            break
                except Exception as e:
                    log(f"查找下載檔案時發生錯誤: {str(e)}")
                    actual_file_path = None
            
            if actual_file_path and os.path.exists(actual_file_path):
                # 檢查是否有多個中間檔案（片段）
                self.check_merged_files(actual_file_path)
                
                # 顯示完成對話框
                self.show_download_complete_dialog(filename, actual_file_path)
                
                # 更新UI
                progress_bar = download_item.findChild(QProgressBar, f"progress_{filename}")
                status_label = download_item.findChild(QLabel, f"status_{filename}")
                eta_label = download_item.findChild(QLabel, f"eta_{filename}")
                speed_label = download_item.findChild(QLabel, f"speed_{filename}")
                
                if progress_bar and status_label:
                    progress_bar.setValue(100)
                    status_label.setText("下載完成 ✓")
                    status_label.setStyleSheet("color: green; font-weight: bold;")
                    
                if eta_label:
                    eta_label.setText("完成")
                
                if speed_label:
                    speed_label.setText("--")
                
                # 更新圖標為完成狀態
                icon_label = download_item.findChild(QLabel, f"icon_{filename}")
                if icon_label:
                    icon_label.setText("✓")
                    icon_label.setStyleSheet("color: #5cb85c; font-size: 14pt; font-weight: bold;")
                
                # 更新進度條為綠色
                if progress_bar:
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
                            background-color: #5cb85c;
                            border-radius: 5px;
                        }
                    """)
                
                # 更新按鈕狀態
                pause_btn = download_item.findChild(QPushButton, f"pause_btn_{filename}")
                if pause_btn:
                    pause_btn.setEnabled(False)
                    pause_btn.setText("完成")
                
                delete_btn = download_item.findChild(QPushButton, f"delete_btn_{filename}")
                if delete_btn:
                    delete_btn.setText("刪除")
                
                # 通知已下載檔案頁面更新
                self.notify_download_completed(actual_file_path)
                
                # 清除URL輸入框（僅在下載成功時才清除）
                QTimer.singleShot(1000, lambda: self.url_edit.clear())
                
                # 顯示成功訊息
                self.title_label.setText(f"下載成功: {os.path.basename(actual_file_path)}")
                self.title_label.setStyleSheet("font-weight: bold; color: green; margin: 5px 0;")
                
                # 自動移除已完成項目（如果設置了）
                if hasattr(self, 'auto_remove_completed') and self.auto_remove_completed:
                    # 延遲移除，讓用戶有時間看到完成狀態
                    QTimer.singleShot(3000, lambda: self.auto_remove_completed_item(filename))
            else:
                # 文件不存在，顯示錯誤
                self.show_error_dialog(filename, "下載失敗：找不到下載的檔案")
                # 顯示外部下載按鈕
                QTimer.singleShot(1000, lambda: self.show_external_download_button(filename))
                # 更新標題標籤，提示可以使用外部下載工具
                self.title_label.setText("下載失敗：找不到下載的檔案。請嘗試使用外部下載工具。")
                self.title_label.setStyleSheet("font-weight: bold; color: red; margin: 5px 0;")
        else:
            # 下載失敗
            self.show_error_dialog(filename, message)
            # 顯示外部下載按鈕
            QTimer.singleShot(1000, lambda: self.show_external_download_button(filename))
            # 更新標題標籤，提示可以使用外部下載工具
            self.title_label.setText(f"下載失敗：{message}。請嘗試使用外部下載工具。")
            self.title_label.setStyleSheet("font-weight: bold; color: red; margin: 5px 0;")
        
        # 清理下載線程
        if filename in self.download_threads:
            try:
                thread = self.download_threads.pop(filename)
                thread.deleteLater()
                log(f"已清理下載線程: {filename}")
            except Exception as e:
                log(f"清理下載線程時發生錯誤: {str(e)}")
        
        # 更新總進度
        self.update_total_progress()

    def auto_remove_completed_item(self, filename):
        """自動移除已完成的下載項目"""
        try:
            if filename in self.download_items:
                log(f"自動移除已完成的下載項目: {filename}")
                
                # 獲取項目數據
                item_data = self.download_items[filename]
                
                # 檢查是否真的完成了（進度為100%且狀態為已完成）
                if (item_data['progress_bar'].value() == 100 and 
                    "已完成" in item_data['status_label'].text()):
                    
                    # 創建淡出動畫效果
                    item_widget = item_data['widget']
                    
                    # 使用QPropertyAnimation創建淡出效果
                    from PySide6.QtCore import QPropertyAnimation, QEasingCurve
                    from PySide6.QtWidgets import QGraphicsOpacityEffect
                    
                    # 創建透明度效果
                    opacity_effect = QGraphicsOpacityEffect(item_widget)
                    item_widget.setGraphicsEffect(opacity_effect)
                    
                    # 創建淡出動畫
                    fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
                    fade_animation.setDuration(500)  # 0.5秒
                    fade_animation.setStartValue(1.0)
                    fade_animation.setEndValue(0.0)
                    fade_animation.setEasingCurve(QEasingCurve.OutCubic)
                    
                    # 動畫完成後移除項目
                    fade_animation.finished.connect(lambda: self.remove_item_from_ui(filename))
                    
                    # 開始動畫
                    fade_animation.start()
                else:
                    log(f"項目 {filename} 未完成，不自動移除")
                    
        except Exception as e:
            log(f"自動移除項目時發生錯誤: {str(e)}")
            # 如果動畫失敗，直接移除
            self.remove_item_from_ui(filename)
    
    def check_merged_files(self, main_file_path):
        """檢查是否有多個媒體片段檔案，詢問是否只保留合併後的 MP4 檔案"""
        try:
            # 獲取檔案目錄和檔案名（不含副檔名）
            file_dir = os.path.dirname(main_file_path)
            file_base_name = os.path.splitext(os.path.basename(main_file_path))[0]
            
            # 檢查是否有相關的檔案（例如 .f*.mp4 格式的分段檔案）
            related_files = []
            if file_dir and os.path.exists(file_dir):
                for f in os.listdir(file_dir):
                    # 查找相似名稱但不是主檔案的檔案
                    if file_base_name in f and f != os.path.basename(main_file_path):
                        # 特別查找 ffmpeg 合併產生的分段檔案，通常格式為 "原檔名.f*.mp4" 或 "原檔名-*.mp4"
                        if ".f" in f or "-" in f:
                            related_files.append(os.path.join(file_dir, f))
            
            # 如果有相關檔案，詢問用戶是否只保留合併後的檔案
            if related_files and os.path.exists(main_file_path):
                total_size_temp = sum(os.path.getsize(f) for f in related_files if os.path.exists(f))
                main_file_size = os.path.getsize(main_file_path) if os.path.exists(main_file_path) else 0
                
                # 檢查設定是否有自動清理選項
                auto_clean = False
                try:
                    settings_path = get_settings_path()
                    if os.path.exists(settings_path):
                        with open(settings_path, "r", encoding="utf-8") as f:
                            settings = json.load(f)
                            auto_clean = settings.get("auto_clean_merged_files", False)
                except Exception:
                    pass
                
                # 如果設定了自動清理，就不詢問直接刪除
                if auto_clean:
                    deleted_count = 0
                    for f in related_files:
                        try:
                            if os.path.exists(f):
                                os.remove(f)
                                deleted_count += 1
                                log(f"已自動刪除中間檔案: {f}")
                        except Exception as e:
                            log(f"自動刪除檔案失敗: {f}, 原因: {str(e)}")
                    
                    log(f"已自動清理 {deleted_count} 個中間檔案，節省了 {self.format_file_size(total_size_temp)} 空間")
                    
                    # 顯示清理成功通知
                    notification = QMessageBox(QMessageBox.Information, "清理完成", 
                                            f"已自動清理 {deleted_count} 個中間檔案，節省了 {self.format_file_size(total_size_temp)} 空間",
                                            QMessageBox.Ok, self)
                    notification.setWindowModality(Qt.NonModal)  # 非模態對話框，不阻塞主線程
                    notification.show()
                    QTimer.singleShot(3000, notification.close)  # 3秒後自動關閉
                    
                    return
                
                # 如果沒有自動清理設定，顯示詢問對話框
                msg = QMessageBox()
                msg.setWindowTitle("合併檔案清理")
                msg.setText(f"檢測到 {len(related_files)} 個下載片段檔案")
                msg.setInformativeText(f"是否只保留合併後的 MP4 檔案，刪除中間檔案以節省空間？\n\n"
                                       f"合併檔案大小: {self.format_file_size(main_file_size)}\n"
                                       f"中間檔案大小: {self.format_file_size(total_size_temp)}\n"
                                       f"可節省空間: {self.format_file_size(total_size_temp)}")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setDefaultButton(QMessageBox.Yes)
                
                # 設置"總是這樣做"核取方塊
                always_cb = QCheckBox("記住我的選擇，不再詢問")
                msg.setCheckBox(always_cb)
                
                # 顯示對話框
                result = msg.exec_()
                
                # 處理結果
                if result == QMessageBox.Yes:
                    # 刪除中間檔案
                    deleted_count = 0
                    for f in related_files:
                        try:
                            if os.path.exists(f):
                                os.remove(f)
                                deleted_count += 1
                                log(f"已刪除中間檔案: {f}")
                        except Exception as e:
                            log(f"刪除檔案失敗: {f}, 原因: {str(e)}")
                    
                    # 顯示成功通知
                    notification = QMessageBox(QMessageBox.Information, "清理完成", 
                                            f"已清理 {deleted_count} 個中間檔案，節省了 {self.format_file_size(total_size_temp)} 空間",
                                            QMessageBox.Ok, self)
                    notification.setWindowModality(Qt.NonModal)  # 非模態對話框，不阻塞主線程
                    notification.show()
                    QTimer.singleShot(3000, notification.close)  # 3秒後自動關閉
                    
                    # 如果用戶勾選了"記住選擇"，保存設置
                    if always_cb.isChecked():
                        try:
                            # 讀取當前設置
                            settings_path = get_settings_path()
                            settings = {}
                            if os.path.exists(settings_path):
                                with open(settings_path, "r", encoding="utf-8") as f:
                                    settings = json.load(f)
                            
                            # 更新設置
                            settings["auto_clean_merged_files"] = True
                            
                            # 保存回檔案
                            with open(settings_path, "w", encoding="utf-8") as f:
                                json.dump(settings, f, ensure_ascii=False, indent=4)
                            
                            log("已保存自動清理合併檔案設置")
                        except Exception as e:
                            log(f"保存設置失敗: {str(e)}")
                    
                    # 顯示成功訊息
                    QMessageBox.information(self, "清理完成", f"已成功刪除 {deleted_count} 個中間檔案，節省了 {self.format_file_size(total_size_temp)} 空間。")
                else:
                    # 用戶選擇保留所有檔案
                    log("用戶選擇保留所有檔案")
                    
                    # 如果用戶勾選了"記住選擇"，保存設置
                    if always_cb.isChecked():
                        try:
                            # 讀取當前設置
                            settings_path = get_settings_path()
                            settings = {}
                            if os.path.exists(settings_path):
                                with open(settings_path, "r", encoding="utf-8") as f:
                                    settings = json.load(f)
                            
                            # 更新設置
                            settings["auto_clean_merged_files"] = False
                            
                            # 保存回檔案
                            with open(settings_path, "w", encoding="utf-8") as f:
                                json.dump(settings, f, ensure_ascii=False, indent=4)
                            
                            log("已保存不自動清理合併檔案設置")
                        except Exception as e:
                            log(f"保存設置失敗: {str(e)}")
        except Exception as e:
            log(f"檢查合併檔案時出錯: {str(e)}")
    
    def remove_item_from_ui(self, filename):
        """從UI中移除下載項目"""
        try:
            if filename in self.download_items:
                # 獲取項目數據
                item_data = self.download_items[filename]
                item_widget = item_data['widget']
                
                # 找到容器（QFrame）
                container = item_widget.parent()
                while container and not isinstance(container, QFrame):
                    container = container.parent()
                
                if container:
                    # 從下載佈局中移除容器
                    self.download_layout.removeWidget(container)
                    container.setParent(None)
                    container.deleteLater()
                
                # 清理小部件
                item_widget.setParent(None)
                item_widget.deleteLater()
                
                # 從字典中移除項目
                del self.download_items[filename]
                
                # 更新總進度
                self.update_total_progress()
                
                log(f"已從UI中移除下載項目: {filename}")
                
        except Exception as e:
            log(f"從UI中移除項目時發生錯誤: {str(e)}")

    def show_age_restriction_dialog(self):
        """顯示年齡限制對話框"""
        # 檢查是否已經有年齡限制對話框在顯示
        if hasattr(self, 'age_restriction_dialog') and self.age_restriction_dialog.isVisible():
            # 如果已有對話框，則將其帶到前台
            self.age_restriction_dialog.activateWindow()
            self.age_restriction_dialog.raise_()
            return
            
        # 創建對話框
        dialog = QMessageBox(self)
        dialog.setWindowTitle("年齡限制影片")
        dialog.setIcon(QMessageBox.Warning)
        dialog.setText("此影片有年齡限制，需要使用 cookies 進行驗證。")
        dialog.setInformativeText(
            "請按照以下步驟操作：\n\n"
            "1. 前往「設定」標籤頁的「網路設定」區塊\n"
            "2. 啟用「使用 cookies」選項\n"
            "3. 點擊「瀏覽」按鈕選擇 cookies.txt 檔案\n\n"
            "如何獲取 cookies.txt 檔案：\n"
            "1. 在瀏覽器中安裝「Get cookies.txt」擴充功能\n"
            "2. 登入 YouTube 帳號\n"
            "3. 使用擴充功能匯出 cookies.txt 檔案\n"
            "4. 選擇該檔案並套用設定\n"
        )
        
        # 添加「前往設定」按鈕
        go_to_settings_button = dialog.addButton("前往設定", QMessageBox.ActionRole)
        dialog.addButton("關閉", QMessageBox.RejectRole)
        
        # 儲存對話框引用
        self.age_restriction_dialog = dialog
        
        # 顯示對話框
        result = dialog.exec()
        
        # 處理按鈕點擊
        if dialog.clickedButton() == go_to_settings_button:
            # 切換到設定標籤頁
            main_window = self.window()
            if main_window and hasattr(main_window, 'tab_widget'):
                # 找到設定標籤頁的索引
                for i in range(main_window.tab_widget.count()):
                    if "設定" in main_window.tab_widget.tabText(i):
                        main_window.tab_widget.setCurrentIndex(i)
                        
                        # 嘗試聚焦到網路設定區域
                        settings_tab = main_window.tab_widget.widget(i)
                        if hasattr(settings_tab, 'network_group'):
                            settings_tab.network_group.setFocus()
                        break

    def notify_download_completed(self, file_path):
        """通知下載完成（已移除已下載檔案頁籤的更新）"""
        try:
            log(f"下載完成: {file_path}")
        except Exception as e:
            log(f"通知下載完成失敗: {str(e)}")

    def update_total_progress(self):
        """更新總進度信息"""
        # 計算總下載項目數和已完成的下載數量
        total_items = len(self.download_items)
        if total_items == 0:
            # 如果沒有下載項目，重置進度條
            self.total_progress.setValue(0)
            return
        
        completed_items = 0
        in_progress_items = 0
        total_percent = 0
        
        # 統計所有下載項目的進度
        for filename, item_data in self.download_items.items():
            progress_bar = item_data.get('progress_bar')
            if progress_bar:
                progress_value = progress_bar.value()
                if progress_value == 100:
                    completed_items += 1
                else:
                    in_progress_items += 1
                    total_percent += progress_value
        
        # 計算總體進度百分比
        if total_items > 0:
            if in_progress_items > 0:
                # 計算進行中項目的平均進度
                avg_progress = total_percent / in_progress_items
                # 總進度 = (已完成項目數 / 總項目數) * 100 + (進行中項目數 / 總項目數) * 平均進度
                total_progress_percent = int((completed_items / total_items) * 100 + (in_progress_items / total_items) * avg_progress)
            else:
                # 如果沒有進行中的項目，總進度就是已完成項目的比例
                total_progress_percent = int((completed_items / total_items) * 100)
            
            # 更新總進度條
            self.total_progress.setValue(total_progress_percent)
            # 更新總進度標籤
            if completed_items == total_items:
                self.total_progress.setFormat(f"總進度: 100% ({completed_items}/{total_items})")
            else:
                remaining_time = (total_items - completed_items) * 2  # 假設每個項目平均需要2分鐘
                self.total_progress.setFormat(f"總進度: {total_progress_percent}% ({completed_items}/{total_items})")

    def browse_path(self):
        """瀏覽下載路徑"""
        path = QFileDialog.getExistingDirectory(self, "選擇下載資料夾", self.download_path)
        if path:
            self.download_path = path
            self.path_edit.setText(path)
            log(f"已選擇下載路徑: {path}")
            # 保存設定
            self.save_settings()

    def on_format_changed(self, index):
        """當格式選擇改變時更新解析度下拉選單"""
        format_text = self.format_combo.currentText()
        
        # 如果選擇的是音訊格式，禁用解析度選擇
        if "僅音訊" in format_text:
            self.resolution_combo.setEnabled(False)
            self.resolution_combo.setCurrentText("自動選擇最佳")
        else:
            self.resolution_combo.setEnabled(True)
        
        # 立即保存格式設定
        self.save_settings()

    def update_resolution_availability(self):
        """更新解析度可用性（模擬根據影片實際可用解析度）"""
        current_resolution = self.resolution_combo.currentText()
        log(f"已選擇解析度: {current_resolution}")
        
        # 立即保存解析度設定
        self.save_settings()

    def clear_completed_downloads(self):
        """清空已下載成功的檔案"""
        log("清空已下載成功的檔案")
        
        # 找出所有已完成的下載項目
        completed_items = []
        for filename, item_data in list(self.download_items.items()):
            progress_bar = item_data.get('progress_bar')
            status_label = item_data.get('status_label')
            
            # 檢查是否已完成下載
            if (progress_bar and progress_bar.value() == 100) or (status_label and ("已完成" in status_label.text() or "✅" in status_label.text())):
                completed_items.append(filename)
        
        # 如果沒有已完成的項目，顯示提示訊息
        if not completed_items:
            QMessageBox.information(self, "清空完成", "沒有已下載完成的檔案可清空")
            return
        
        # 刪除已完成的項目
        for filename in completed_items:
            self.remove_item_from_ui(filename)
                
            # 如果有相關的下載線程，也一併清理
            if filename in self.download_threads:
                thread = self.download_threads[filename]
                if thread.isRunning():
                    thread.cancel()
                    thread.wait()
                del self.download_threads[filename]
        
        # 更新總進度
        self.update_total_progress()
        
        # 顯示清空完成提示
        QMessageBox.information(self, "清空完成", f"已清空 {len(completed_items)} 個已下載完成的檔案")



    def delete_selected(self):
        """刪除選中的下載項目"""
        # 在實際應用中，這裡應該獲取用戶選中的項目
        # 目前簡單實現為刪除所有已完成或錯誤的項目
        to_delete = []
        
        for filename, item in self.download_items.items():
            status_text = item['status_label'].text()
            if "完成" in status_text or "錯誤" in status_text or "失敗" in status_text:
                to_delete.append(filename)
        
        if not to_delete:
            QMessageBox.information(self, "提示", "沒有找到可刪除的項目")
            return
            
        reply = QMessageBox.question(self, "確認刪除", 
                                   f"確定要刪除 {len(to_delete)} 個項目嗎？",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for filename in to_delete:
                self.delete_item(filename)
            
            QMessageBox.information(self, "完成", f"已刪除 {len(to_delete)} 個項目")

    def show_download_complete_dialog(self, filename, file_path):
        """顯示下載完成對話框"""
        # 檢查檔案路徑是否有效
        if not file_path or not os.path.exists(file_path):
            log(f"下載完成對話框：檔案路徑無效 {file_path}")
            return
            
        # 檢查用戶設定是否要顯示完成對話框
        show_dialog = True  # 這裡可以從設定中讀取
        
        if not show_dialog:
            return
        
        # 創建自定義對話框
        dialog = QDialog(self)
        dialog.setWindowTitle("下載完成")
        dialog.setMinimumWidth(450)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
            }
            QLabel#title {
                font-size: 16px;
                font-weight: bold;
                color: #4CAF50;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#open {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#open:hover {
                background-color: #45a049;
            }
            QPushButton#folder {
                background-color: #2196F3;
                color: white;
            }
            QPushButton#folder:hover {
                background-color: #0b7dda;
            }
            QPushButton#close {
                background-color: #f1f1f1;
                color: #555;
            }
            QPushButton#close:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # 主佈局
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # 標題和圖標
        title_layout = QHBoxLayout()
        success_icon = QLabel()
        success_icon.setText("✅")
        success_icon.setStyleSheet("font-size: 36px;")
        success_icon.setMaximumWidth(50)
        title_layout.addWidget(success_icon)
        
        title_label = QLabel(f"<span id='title'>'{filename}'下載完成！</span>")
        title_label.setObjectName("title")
        title_label.setWordWrap(True)
        title_layout.addWidget(title_label, 1)
        layout.addLayout(title_layout)
        
        # 檔案資訊
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setStyleSheet("background-color: white; border-radius: 4px; padding: 10px;")
        info_layout = QVBoxLayout(info_frame)
        
        # 檔案路徑
        path_label = QLabel(f"<b>檔案位置:</b> {os.path.dirname(file_path)}")
        path_label.setWordWrap(True)
        path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(path_label)
        
        # 檔案名稱
        name_label = QLabel(f"<b>檔案名稱:</b> {os.path.basename(file_path)}")
        name_label.setWordWrap(True)
        name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(name_label)
        
        # 檔案大小
        try:
            file_size = os.path.getsize(file_path)
            size_str = self.format_file_size(file_size)
            size_label = QLabel(f"<b>檔案大小:</b> {size_str}")
            info_layout.addWidget(size_label)
        except:
            pass
            
        layout.addWidget(info_frame)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 打開檔案按鈕
        open_button = QPushButton("打開檔案")
        open_button.setObjectName("open")
        open_button.setIcon(QIcon("icons/file.png"))
        open_button.clicked.connect(lambda: self.open_file(file_path))
        open_button.clicked.connect(dialog.accept)
        
        # 打開資料夾按鈕
        folder_button = QPushButton("打開資料夾")
        folder_button.setObjectName("folder")
        folder_button.setIcon(QIcon("icons/folder.png"))
        folder_button.clicked.connect(lambda: self.open_folder(os.path.dirname(file_path)))
        folder_button.clicked.connect(dialog.accept)
        
        # 關閉按鈕
        close_button = QPushButton("關閉")
        close_button.setObjectName("close")
        close_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(open_button)
        button_layout.addWidget(folder_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # 顯示對話框
        dialog.exec()
        
    def format_file_size(self, size_bytes):
        """格式化檔案大小"""
        try:
            if size_bytes is None or size_bytes < 0:
                return "0 B"
            if size_bytes < 1024:
                return f"{int(size_bytes)} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes/(1024*1024):.1f} MB"
            else:
                return f"{size_bytes/(1024*1024*1024):.2f} GB"
        except Exception as e:
            log(f"格式化檔案大小時發生錯誤: {str(e)}")
            return "-- B"
            
    def open_file(self, file_path):
        """打開檔案"""
        if os.path.exists(file_path):
            try:
                os.startfile(file_path)
            except Exception as e:
                QMessageBox.warning(self, "錯誤", f"無法打開檔案: {str(e)}")
                
    def open_folder(self, folder_path):
        """打開資料夾"""
        if os.path.exists(folder_path):
            try:
                os.startfile(folder_path)
            except Exception as e:
                QMessageBox.warning(self, "錯誤", f"無法打開資料夾: {str(e)}")

    def show_error_dialog(self, filename, error_message):
        """顯示錯誤對話框"""
        # 檢查是否為yt-dlp失敗錯誤
        if error_message.startswith("YT_DLP_FAILURE:"):
            self.show_yt_dlp_failure_dialog(filename, error_message)
            return
        
        # 如果已經有相同檔名的錯誤對話框，先關閉它
        if filename in self.error_dialogs and self.error_dialogs[filename] is not None:
            try:
                self.error_dialogs[filename].close()
            except:
                pass
        
        # 獲取對應的URL
        url_input = self.findChild(QLineEdit, f"url_input_{filename}")
        url = url_input.text() if url_input else "未知URL"
        
        # 獲取格式和解析度
        format_option = self.download_formats.get(filename, "未知")
        resolution = self.download_resolutions.get(filename, "未知")
        
        # 獲取平台信息
        platform_name = self.download_items[filename].get('platform_info', "未知")
        
        # 創建錯誤對話框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"下載錯誤: {filename}")
        dialog.setMinimumWidth(600)
        dialog.setStyleSheet("QLabel { margin: 5px; }")
        
        # 設置對話框佈局
        layout = QVBoxLayout(dialog)
        
        # 錯誤圖標和標題
        header_layout = QHBoxLayout()
        error_icon = QLabel()
        error_icon.setPixmap(QIcon.fromTheme("dialog-error").pixmap(32, 32))
        header_layout.addWidget(error_icon)
        
        error_title = QLabel(f"<h3>下載 '{filename}' 時發生錯誤</h3>")
        header_layout.addWidget(error_title)
        header_layout.addStretch(1)
        layout.addLayout(header_layout)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 錯誤詳情
        details_group = QGroupBox("錯誤詳情")
        details_layout = QVBoxLayout(details_group)
        
        # 錯誤訊息
        error_label = QTextEdit()
        error_label.setPlainText(error_message)
        error_label.setReadOnly(True)
        error_label.setMaximumHeight(150)
        error_label.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }
        """)
        details_layout.addWidget(error_label)
        
        # URL
        url_label = QLabel(f"<b>URL:</b> {url}")
        url_label.setWordWrap(True)
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        details_layout.addWidget(url_label)
        
        # 下載設定
        settings_label = QLabel(f"<b>格式:</b> {format_option}, <b>解析度:</b> {resolution}")
        settings_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        details_layout.addWidget(settings_label)
        
        layout.addWidget(details_group)
        
        # 可能的解決方案
        solutions_group = QGroupBox("可能的解決方案")
        solutions_layout = QVBoxLayout(solutions_group)
        
        # 根據錯誤類型提供不同的解決方案
        error_lower = error_message.lower()
        
        # 平台不支援錯誤
        if "無法辨識" in error_message or "不支援此平台" in error_message:
            solutions_layout.addWidget(QLabel("• 請確認您輸入的URL是否來自支援的平台。"))
            solutions_layout.addWidget(QLabel("• 支援的平台: YouTube, TikTok/抖音, Facebook, Instagram, Bilibili, X(Twitter)"))
            solutions_layout.addWidget(QLabel("• 請嘗試使用分享功能獲取正確的影片連結。"))
        # 需要登入錯誤
        elif "需要登入" in error_message or "cookies" in error_lower:
            solutions_layout.addWidget(QLabel("• 此內容需要登入才能訪問，請在設定中提供cookies.txt檔案。"))
            solutions_layout.addWidget(QLabel("• 在「設定」→「網路設定」→「Cookies設定」中啟用cookies並選擇檔案。"))
            solutions_layout.addWidget(QLabel("• 您可以使用瀏覽器擴充功能匯出cookies.txt檔案。"))
        # 年齡限制錯誤
        elif ("age" in error_lower and "restrict" in error_lower) or ("年齡" in error_message and "限制" in error_message) or (
            "cookies" in error_lower and "age" in error_lower):
            solutions_layout.addWidget(QLabel("• ⚠️ 此影片可能受到年齡限制，請提供 cookies.txt 檔案以繞過限制。"))
            solutions_layout.addWidget(QLabel("• 您可以使用瀏覽器擴充功能匯出 cookies.txt，然後在下載選項中選擇該檔案。"))
            solutions_layout.addWidget(QLabel("• 或者嘗試使用其他影片 URL，如內嵌連結或分享連結。"))
            solutions_layout.addWidget(QLabel("• 詳見: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp"))
        # 網路錯誤
        elif "network" in error_lower or "timeout" in error_lower or "連線" in error_message or "網路" in error_message:
            solutions_layout.addWidget(QLabel("• 請檢查您的網路連線是否正常。"))
            solutions_layout.addWidget(QLabel("• 如果您使用代理或VPN，請確認其是否正常運作。"))
            solutions_layout.addWidget(QLabel("• 嘗試稍後再試，伺服器可能暫時不可用。"))
        # 影片不存在或已被刪除
        elif "not exist" in error_lower or "removed" in error_lower or "不存在" in error_message or "已移除" in error_message:
            solutions_layout.addWidget(QLabel("• 此影片可能已被刪除或設為私人。"))
            solutions_layout.addWidget(QLabel("• 請確認URL是否正確。"))
        # 其他錯誤
        else:
            solutions_layout.addWidget(QLabel("• 嘗試使用不同的格式或解析度選項。"))
            solutions_layout.addWidget(QLabel("• 檢查影片URL是否正確。"))
            solutions_layout.addWidget(QLabel("• 嘗試重新啟動應用程式。"))
            solutions_layout.addWidget(QLabel("• 如果問題持續存在，請保存錯誤日誌以供進一步分析。"))
        
        layout.addWidget(solutions_group)
        
        # 添加外部下載工具區塊
        external_tool_group = QGroupBox("外部下載工具")
        external_tool_layout = QVBoxLayout(external_tool_group)
        
        # 載入外部下載替代網址設定
        external_urls = self.load_external_url_settings()
        
        # 設定按鈕文字和URL
        button_text = "外部下載工具"
        external_url = f"https://savefrom.net/?url={url}"
        
        # 根據平台設置不同的按鈕文字和URL
        if platform_name == "Instagram" or "instagram.com" in url.lower():
            button_text = "IG下載器"
            external_url = external_urls.get("instagram", "https://igram.io/?url={url}").format(url=url)
            external_tool_layout.addWidget(QLabel("Instagram 影片有時需要特殊處理，您可以嘗試使用專門的外部下載工具："))
        elif platform_name in ["X", "Twitter"] or "twitter.com" in url.lower() or "x.com" in url.lower():
            button_text = "X下載器"
            external_url = external_urls.get("twitter", "https://twittervideodownloader.com/?url={url}").format(url=url)
            external_tool_layout.addWidget(QLabel("Twitter/X 影片有時需要特殊處理，您可以嘗試使用專門的外部下載工具："))
        elif platform_name in ["TikTok", "抖音"] or "tiktok.com" in url.lower() or "douyin.com" in url.lower():
            button_text = "TikTok下載器"
            external_url = external_urls.get("tiktok", "https://tiktokio.com/zh_tw/?url={url}").format(url=url)
            external_tool_layout.addWidget(QLabel("TikTok/抖音 影片有時需要特殊處理，您可以嘗試使用專門的外部下載工具："))
        elif platform_name == "Facebook" or "facebook.com" in url.lower() or "fb.com" in url.lower() or "fb.watch" in url.lower():
            button_text = "FB下載器"
            external_url = external_urls.get("facebook", "https://fdown.net/?url={url}").format(url=url)
            external_tool_layout.addWidget(QLabel("Facebook 影片有時需要特殊處理，您可以嘗試使用專門的外部下載工具："))
        elif platform_name == "Threads" or "threads.net" in url.lower():
            button_text = "Threads下載器"
            external_url = external_urls.get("threads", "https://threadsdownloader.com/?url={url}").format(url=url)
            external_tool_layout.addWidget(QLabel("Threads 影片有時需要特殊處理，您可以嘗試使用專門的外部下載工具："))
        elif platform_name == "Bilibili" or "bilibili.com" in url.lower() or "b23.tv" in url.lower():
            button_text = "B站下載器"
            external_url = external_urls.get("bilibili", "https://bilibili.iiilab.com/?url={url}").format(url=url)
            external_tool_layout.addWidget(QLabel("Bilibili 影片有時需要特殊處理，您可以嘗試使用專門的外部下載工具："))
        else:
            external_tool_layout.addWidget(QLabel("您可以嘗試使用外部下載工具來下載此影片："))
        
        # 創建外部工具按鈕
        external_tool_btn = QPushButton(f"🌐 {button_text}")
        external_tool_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        
        # 設置點擊事件
        external_tool_btn.clicked.connect(lambda: self.open_external_downloader(external_url))
        external_tool_layout.addWidget(external_tool_btn)
        
        layout.addWidget(external_tool_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        
        # 重試按鈕
        retry_button = QPushButton("重試下載")
        retry_button.clicked.connect(lambda: self.retry_download(filename, dialog))
        buttons_layout.addWidget(retry_button)
        
        # 更改格式按鈕
        change_format_button = QPushButton("更改格式選項")
        change_format_button.clicked.connect(lambda: self.show_format_options_dialog(filename, dialog))
        buttons_layout.addWidget(change_format_button)
        
        # 保存錯誤日誌按鈕
        save_log_button = QPushButton("保存錯誤日誌")
        output_path = self.download_path
        save_log_button.clicked.connect(lambda: self.save_error_log(filename, error_message, url, format_option, resolution, output_path))
        buttons_layout.addWidget(save_log_button)
        
        # 關閉按鈕
        close_button = QPushButton("關閉")
        close_button.clicked.connect(dialog.close)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        # 保存對話框引用
        self.error_dialogs[filename] = dialog
        
        # 顯示對話框
        dialog.exec()

    def show_yt_dlp_failure_dialog(self, filename, error_message):
        """顯示yt-dlp失敗的特殊對話框"""
        # 解析錯誤訊息
        parts = error_message.split(":", 2)
        if len(parts) >= 3:
            platform_name = parts[1]
            original_error = parts[2]
        else:
            platform_name = "未知平台"
            original_error = error_message
        
        # 獲取對應的URL
        url = "未知URL"
        if filename in self.download_items and 'url' in self.download_items[filename]:
            url = self.download_items[filename]['url']
        else:
            # 嘗試從URL輸入框獲取
            url_input = self.findChild(QLineEdit, f"url_input_{filename}")
            if url_input:
                url = url_input.text()
        
        # 創建特殊錯誤對話框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"⚠️ yt-dlp 下載失敗: {filename}")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #fff3cd;
            }
            QLabel { 
                margin: 5px; 
                color: #856404;
            }
            QGroupBox {
                font-weight: bold;
                color: #856404;
                border: 2px solid #ffeaa7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton#external_tool_btn {
                background-color: #d9534f;
                font-size: 12pt;
                padding: 12px 24px;
            }
            QPushButton#external_tool_btn:hover {
                background-color: #c9302c;
            }
        """)
        
        # 設置對話框佈局
        layout = QVBoxLayout(dialog)
        
        # 警告圖標和標題
        header_layout = QHBoxLayout()
        warning_icon = QLabel("⚠️")
        warning_icon.setStyleSheet("font-size: 48pt; color: #ffc107;")
        header_layout.addWidget(warning_icon)
        
        title_layout = QVBoxLayout()
        error_title = QLabel(f"<h2>⚠️ 無法使用 yt-dlp 成功下載此影片</h2>")
        error_title.setStyleSheet("color: #856404; font-weight: bold;")
        title_layout.addWidget(error_title)
        
        subtitle = QLabel(f"<h4>平台: {platform_name} | 檔案: {filename}</h4>")
        subtitle.setStyleSheet("color: #856404;")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)
        layout.addLayout(header_layout)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #ffeaa7;")
        layout.addWidget(separator)
        
        # 主要訊息
        main_message = QLabel(
            "<h3>你可以試試使用外部下載工具</h3>"
            "<p>由於網站反爬蟲機制或技術限制，yt-dlp 無法下載此影片。</p>"
            "<p>我們推薦使用以下外部工具作為替代方案：</p>"
        )
        main_message.setWordWrap(True)
        main_message.setStyleSheet("color: #856404; font-size: 11pt;")
        layout.addWidget(main_message)
        
        # 外部工具選項
        tools_group = QGroupBox("🌐 推薦的外部下載工具")
        tools_layout = QVBoxLayout(tools_group)
        
        # 根據平台選擇適合的圖標和說明
        platform_icon = "🌐"
        platform_title = "通用下載工具"
        platform_desc = "適用於多種平台的影片下載工具"
        tool_url = "https://savefrom.net/"
        tool_name = "通用下載工具"
        
        # 載入外部下載替代網址設定
        external_urls = self.load_external_url_settings()
        
        # URL 編碼處理
        import urllib.parse
        encoded_url = urllib.parse.quote(url, safe='')
        
        # 根據平台選擇適合的圖標和說明
        platform_icon = "🌐"
        platform_title = "通用下載工具"
        platform_desc = "適用於多種平台的影片下載工具"
        tool_url = "https://savefrom.net/"
        tool_name = "通用下載工具"
        
        if platform_name == "X" or platform_name == "Twitter":
            platform_icon = "🐦"
            platform_title = "Twitter Video Downloader"
            platform_desc = "專門用於下載 Twitter/X.com 影片的線上工具"
            tool_url = external_urls.get("twitter", "https://twittervideodownloader.com/?url={url}").format(url=encoded_url)
            tool_name = "X下載器"
        elif platform_name == "Instagram":
            platform_icon = "📷"
            platform_title = "Instagram Downloader"
            platform_desc = "專門用於下載 Instagram 影片和照片的線上工具"
            tool_url = external_urls.get("instagram", "https://igram.io/?url={url}").format(url=encoded_url)
            tool_name = "IG下載器"
        elif platform_name == "TikTok":
            platform_icon = "🎵"
            platform_title = "TikTok Downloader"
            platform_desc = "專門用於下載 TikTok 影片的線上工具"
            tool_url = external_urls.get("tiktok", "https://tiktokio.com/zh_tw/?url={url}").format(url=encoded_url)
            tool_name = "TikTok下載器"
        elif platform_name == "Facebook":
            platform_icon = "👍"
            platform_title = "Facebook Video Downloader"
            platform_desc = "專門用於下載 Facebook 影片的線上工具"
            tool_url = external_urls.get("facebook", "https://fdown.net/?url={url}").format(url=encoded_url)
            tool_name = "FB下載器"
        elif platform_name == "Bilibili":
            platform_icon = "📺"
            platform_title = "Bilibili Downloader"
            platform_desc = "專門用於下載 Bilibili 影片的線上工具"
            tool_url = external_urls.get("bilibili", "https://bilibili.iiilab.com/?url={url}").format(url=encoded_url)
            tool_name = "B站下載器"
        elif platform_name == "Threads":
            platform_icon = "🧵"
            platform_title = "Threads Downloader"
            platform_desc = "專門用於下載 Threads 影片和照片的線上工具"
            tool_url = external_urls.get("threads", "https://threadsdownloader.com/?url={url}").format(url=encoded_url)
            tool_name = "Threads下載器"
        
        # 平台專屬下載工具區塊
        platform_section = QHBoxLayout()
        platform_icon_label = QLabel(platform_icon)
        platform_icon_label.setStyleSheet("font-size: 24pt;")
        platform_section.addWidget(platform_icon_label)
        
        platform_info = QVBoxLayout()
        platform_title_label = QLabel(f"<b>{platform_title}</b>")
        platform_title_label.setStyleSheet("color: #856404; font-size: 12pt;")
        platform_info.addWidget(platform_title_label)
        
        platform_desc_label = QLabel(platform_desc)
        platform_desc_label.setStyleSheet("color: #856404; font-size: 10pt;")
        platform_info.addWidget(platform_desc_label)
        
        platform_section.addLayout(platform_info)
        platform_section.addStretch(1)
        
        # 打開外部工具按鈕
        external_tool_btn = QPushButton(f"🌐 打開 {tool_name}")
        external_tool_btn.setObjectName("external_tool_btn")
        external_tool_btn.clicked.connect(lambda: self.open_external_downloader(tool_url))
        platform_section.addWidget(external_tool_btn)
        
        tools_layout.addLayout(platform_section)
        
        # 其他工具選項
        other_tools_label = QLabel(
            "<p><b>其他推薦工具：</b></p>"
            "<p>• <a href='https://instadownloader.co/zh-tw/'>Instagram Downloader</a> - Instagram 影片下載</p>"
            "<p>• <a href='https://tiktokio.com/zh_tw/'>TikTok Downloader</a> - TikTok 影片下載</p>"
            "<p>• <a href='https://fdown.net/'>Facebook Downloader</a> - Facebook 影片下載</p>"
            "<p>• <a href='https://twittervideodownloader.com/'>Twitter Video Downloader</a> - X/Twitter 影片下載</p>"
            "<p>• <a href='https://bilibili.iiilab.com/'>Bilibili Downloader</a> - B站影片下載</p>"
            "<p>• <a href='https://threadsdownloader.com/'>Threads Downloader</a> - Threads 影片下載</p>"
            "<p>• <a href='https://savefrom.net/'>SaveFrom.net</a> - 通用影片下載</p>"
        )
        other_tools_label.setOpenExternalLinks(True)
        other_tools_label.setStyleSheet("color: #856404; font-size: 10pt;")
        tools_layout.addWidget(other_tools_label)
        
        layout.addWidget(tools_group)
        
        # 技術詳情
        tech_group = QGroupBox("🔧 技術詳情")
        tech_layout = QVBoxLayout(tech_group)
        
        # 原始錯誤訊息
        error_label = QTextEdit()
        error_label.setPlainText(f"原始錯誤: {original_error}")
        error_label.setReadOnly(True)
        error_label.setMaximumHeight(100)
        error_label.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                color: #856404;
            }
        """)
        tech_layout.addWidget(error_label)
        
        # 建議解決方案
        solutions_label = QLabel()
        solutions_text = "<p><b>建議解決方案：</b></p>"
        
        # 根據平台提供不同的解決方案
        if platform_name in ["X", "Twitter"]:
            solutions_text += (
                "<p>1. 檢查該推文是否為保護推文 (需要登入才能查看)</p>"
                "<p>2. 在設定中提供有效的 cookies.txt 檔案</p>"
                "<p>3. 使用上方推薦的外部下載工具</p>"
            )
        elif platform_name == "Instagram":
            solutions_text += (
                "<p>1. 檢查該帳號是否為私人帳號</p>"
                "<p>2. 在設定中提供有效的 cookies.txt 檔案</p>"
                "<p>3. 使用上方推薦的外部下載工具</p>"
            )
        else:
            solutions_text += (
                "<p>1. 更新 yt-dlp 到最新版本</p>"
                "<p>2. 在設定中提供有效的 cookies.txt 檔案</p>"
                "<p>3. 使用上方推薦的外部下載工具</p>"
            )
        
        solutions_label.setText(solutions_text)
        solutions_label.setStyleSheet("color: #856404; font-size: 10pt;")
        solutions_label.setWordWrap(True)
        tech_layout.addWidget(solutions_label)
        
        layout.addWidget(tech_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        
        # 打開外部下載工具按鈕
        open_external_btn = QPushButton(f"🌐 使用{tool_name}")
        open_external_btn.setStyleSheet("""
            background-color: #d9534f;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 4px;
        """)
        open_external_btn.clicked.connect(lambda: self.open_external_download_site(filename, url))
        buttons_layout.addWidget(open_external_btn)
        
        # 重試按鈕
        retry_button = QPushButton("🔄 重試下載")
        retry_button.clicked.connect(lambda: self.retry_download(filename, dialog))
        buttons_layout.addWidget(retry_button)
        
        # 關閉按鈕
        close_button = QPushButton("✖️ 關閉")
        close_button.clicked.connect(dialog.close)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        # 保存對話框引用
        self.error_dialogs[filename] = dialog
        
        # 顯示對話框
        dialog.exec()

    def open_external_downloader(self, url):
        """打開外部下載工具"""
        try:
            import webbrowser
            webbrowser.open(url)
            log(f"已打開外部下載工具: {url}")
        except Exception as e:
            log(f"打開外部下載工具失敗: {str(e)}")
            QMessageBox.warning(self, "錯誤", f"無法打開瀏覽器: {str(e)}")

    def retry_download(self, filename, dialog=None):
        """重試下載"""
        # 查找對應的 URL 輸入框
        url_input = self.findChild(QLineEdit, f"url_input_{filename}")
        
        if url_input:
            url = url_input.text()
            if url:
                # 關閉錯誤對話框
                if dialog:
                    dialog.accept()
                elif filename in self.error_dialogs:
                    self.error_dialogs[filename].accept()
                
                # 從已有項目重新開始下載
                self.start_download_for_item(filename, url)
        else:
            QMessageBox.warning(self, "錯誤", "找不到對應的下載項目")

    def show_format_options_dialog(self, filename, parent_dialog=None):
        """顯示格式選項對話框"""
        # 檢查是否已經有該檔案的格式選項對話框
        if filename in self.format_dialogs and self.format_dialogs[filename].isVisible():
            # 如果已有對話框，則將其帶到前台
            self.format_dialogs[filename].activateWindow()
            self.format_dialogs[filename].raise_()
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("變更下載格式")
        dialog.setMinimumWidth(400)
        
        # 將對話框保存到字典中
        self.format_dialogs[filename] = dialog
        
        # 設置對話框關閉事件
        dialog.finished.connect(lambda: self.format_dialogs.pop(filename, None))
        
        layout = QVBoxLayout(dialog)
        
        # 格式選擇
        format_group = QGroupBox("下載格式")
        format_layout = QVBoxLayout(format_group)
        
        format_options = [
            "最高品質 (影片+音訊)",
            "僅影片",
            "僅音訊 (MP3)",
            "僅音訊 (WAV)",
            "預設品質"
        ]
        
        format_combo = QComboBox()
        format_combo.addItems(format_options)
        format_layout.addWidget(format_combo)
        
        layout.addWidget(format_group)
        
        # 解析度選擇
        resolution_group = QGroupBox("解析度")
        resolution_layout = QVBoxLayout(resolution_group)
        
        resolution_options = ["最高可用", "4K", "1080P", "720P", "480P", "360P"]
        
        resolution_combo = QComboBox()
        resolution_combo.addItems(resolution_options)
        resolution_layout.addWidget(resolution_combo)
        
        layout.addWidget(resolution_group)
        
        # 其他選項
        options_group = QGroupBox("其他選項")
        options_layout = QVBoxLayout(options_group)
        
        auto_merge_check = QCheckBox("自動合併影片和音訊 (高畫質影片將始終合併)")
        auto_merge_check.setChecked(True)
        options_layout.addWidget(auto_merge_check)
        
        layout.addWidget(options_group)
        
        # 按鈕
        button_layout = QHBoxLayout()
        apply_button = QPushButton("套用並重試下載")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 連接信號
        cancel_button.clicked.connect(dialog.reject)
        apply_button.clicked.connect(lambda: self.apply_new_format_and_retry(
            filename, 
            format_combo.currentText(), 
            resolution_combo.currentText(), 
            auto_merge_check.isChecked(),
            dialog,
            parent_dialog
        ))
        
        dialog.exec()

    def apply_new_format_and_retry(self, filename, format_option, resolution, auto_merge, dialog, parent_dialog=None):
        """套用新格式並重試下載"""
        # 儲存新設定
        self.download_formats[filename] = format_option
        self.download_resolutions[filename] = resolution
        self.auto_merge_options[filename] = auto_merge
        
        # 關閉對話框
        dialog.accept()
        if parent_dialog:
            parent_dialog.accept()
        
        # 重試下載
        self.retry_download(filename)

    def save_error_log(self, filename, error_message, url, format_option, resolution, output_path):
        """保存錯誤日誌"""
        try:
            # 創建錯誤日誌
            error_log_path = create_error_log(error_message, url, format_option, resolution, output_path)
            
            if error_log_path and os.path.exists(error_log_path):
                # 顯示成功訊息
                msg = QMessageBox(self)
                msg.setWindowTitle("錯誤報告已保存")
                msg.setText(f"錯誤報告已保存至:\n{error_log_path}")
                msg.setIcon(QMessageBox.Information)
                
                open_folder_btn = msg.addButton("開啟資料夾", QMessageBox.ActionRole)
                msg.addButton("關閉", QMessageBox.RejectRole)
                
                msg.exec()
                
                if msg.clickedButton() == open_folder_btn:
                    # 打開包含錯誤報告的資料夾
                    os.startfile(os.path.dirname(error_log_path))
            else:
                QMessageBox.warning(self, "錯誤", "無法保存錯誤報告")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"保存錯誤報告時發生錯誤: {str(e)}")

    def clear_prefix(self):
        """清空前綴"""
        try:
            # 暫時阻止信號，避免觸發事件循環
            self.prefix_combo.blockSignals(True)
            self.prefix_combo.setCurrentText("")
            self.prefix_combo.blockSignals(False)
            
            # 更新所有現有下載項目的檔名前綴
            updated_count = 0
            for filename, item_data in self.download_items.items():
                if 'thread' in item_data and item_data['thread'] is not None:
                    item_data['thread'].prefix = ""
                    item_data['prefix'] = ""
                    updated_count += 1
            
            if updated_count > 0:
                log(f"已清空 {updated_count} 個下載項目的檔名前綴")
            
            log("已清空檔名前綴")
            
            # 保存設定
            self.save_settings()
            
            # 顯示成功訊息
            QMessageBox.information(self, "成功", "已成功清空檔名前綴")
        except Exception as e:
            log(f"清空前綴時發生錯誤: {str(e)}")
            QMessageBox.critical(self, "錯誤", f"清空前綴時發生錯誤: {str(e)}")
        
    def remove_selected_prefix(self):
        """從歷史記錄中刪除選中的前綴"""
        try:
            current_text = self.prefix_combo.currentText()
            current_index = self.prefix_combo.currentIndex()
            
            if current_text and current_text in self.prefix_history:
                # 從歷史記錄中刪除
                self.prefix_history.remove(current_text)
                log(f"已從歷史記錄中刪除前綴: {current_text}")
                
                # 從下拉選單中刪除
                self.prefix_combo.blockSignals(True)  # 暫時阻止信號，避免觸發不必要的事件
                self.prefix_combo.removeItem(current_index)
                
                # 如果還有其他前綴，選擇第一個
                if self.prefix_combo.count() > 0:
                    self.prefix_combo.setCurrentIndex(0)
                else:
                    self.prefix_combo.setCurrentText("")
                    
                self.prefix_combo.blockSignals(False)  # 恢復信號
                
                # 保存設定
                self.save_settings()
                
                # 顯示成功訊息
                QMessageBox.information(self, "成功", f"已成功刪除前綴: {current_text}")
            else:
                QMessageBox.warning(self, "警告", "沒有選中的前綴或前綴不在歷史記錄中")
        except Exception as e:
            log(f"刪除前綴時發生錯誤: {str(e)}")
            QMessageBox.critical(self, "錯誤", f"刪除前綴時發生錯誤: {str(e)}")
        
    def force_resume_download(self, filename):
        """強制恢復卡住的下載"""
        if filename not in self.download_items or filename not in self.download_threads:
            return
            
        # 獲取當前線程
        current_thread = self.download_threads[filename]
        
        # 取消當前線程
        if current_thread.isRunning():
            current_thread.cancel()
            
        # 更新UI狀態
        self.update_download_progress(filename, "正在強制恢復下載...", 0, "--", "--")
        
        # 獲取原始參數
        url = self.download_items[filename].get('url', '')
        output_path = self.download_items[filename].get('output_path', '')
        format_option = self.download_items[filename].get('format_option', '')
        resolution = self.download_items[filename].get('resolution', '')
        prefix = self.download_items[filename].get('prefix', '')
        auto_merge = self.download_items[filename].get('auto_merge', True)
        
        # 創建新的下載線程，使用不同的下載選項
        new_thread = DownloadThread(url, output_path, "預設品質", "最高可用", prefix, auto_merge)
        
        # 連接信號
        new_thread.progress.connect(
            lambda msg, percent, speed, eta: self.update_download_progress(filename, msg, percent, speed, eta)
        )
        new_thread.finished.connect(
            lambda success, msg, file_path: self.download_finished(filename, success, msg, file_path)
        )
        
        # 更新線程引用
        self.download_items[filename]['thread'] = new_thread
        self.download_threads[filename] = new_thread
        
        # 隱藏強制恢復按鈕
        if 'force_resume_btn' in self.download_items[filename]:
            self.download_items[filename]['force_resume_btn'].setVisible(False)
            
        # 啟動新線程
        new_thread.start()
        
        # 顯示提示
        QMessageBox.information(self, "強制恢復", f"已強制恢復下載：{filename}\n使用預設品質選項重新下載。")
        
    def skip_error_tasks(self):
        """跳過錯誤任務"""
        error_count = 0
        stalled_count = 0
        
        for filename, item in list(self.download_items.items()):
            status_text = item['status_label'].text()
            
            # 檢查是否為錯誤或卡住狀態
            if "錯誤" in status_text or "失敗" in status_text:
                error_count += 1
                self.delete_item(filename)
            elif "卡住" in status_text:
                stalled_count += 1
                self.force_resume_download(filename)
                
        if error_count > 0 or stalled_count > 0:
            QMessageBox.information(self, "任務處理", 
                                  f"已跳過 {error_count} 個錯誤任務\n已嘗試恢復 {stalled_count} 個卡住的任務")
        else:
            QMessageBox.information(self, "任務處理", "沒有發現錯誤或卡住的任務")

    def open_external_download_site(self, filename, url=None):
        """根據平台打開對應的外部下載網站"""
        if url is None:
            # 如果沒有提供URL，從下載項目中獲取
            if filename is not None:
                url_input = self.findChild(QLineEdit, f"url_input_{filename}")
                if url_input:
                    url = url_input.text()
                else:
                    url = self.download_items.get(filename, {}).get('url', '')
            else:
                # 如果沒有提供文件名和URL，無法繼續
                QMessageBox.warning(self, "錯誤", "無法獲取下載連結")
                return
        
        # 載入外部下載替代網址設定
        external_urls = self.load_external_url_settings()
        
        # URL 編碼處理
        import urllib.parse
        encoded_url = urllib.parse.quote(url, safe='')
        
        # 識別平台
        platform_name = identify_platform(url)
        platform_key = platform_name.lower()
        
        if platform_key == "x":
            platform_key = "twitter"  # 確保X和Twitter使用同一個設定
        elif platform_key == "未知平台":
            platform_key = "unknown"
        
        # 從設定中取得外部下載連結，如果沒有則使用預設值
        if platform_key in external_urls:
            external_url = external_urls[platform_key].format(url=encoded_url)
        else:
            # 默認使用通用下載工具
            external_url = f"https://savefrom.net/?url={encoded_url}"
        
        # 打開瀏覽器
        self.open_external_downloader(external_url)
        
        # 記錄日誌
        log(f"已打開外部下載工具: {external_url}, 原始URL: {url}")
        
    def load_external_url_settings(self):
        """載入外部下載替代網址設定"""
        default_urls = {
            "youtube": "https://publer.com/tools/youtube-shorts-downloader?url={url}",
            "instagram": "https://igram.io/?url={url}",
            "twitter": "https://twittervideodownloader.com/?url={url}",
            "tiktok": "https://tiktokio.com/zh_tw/?url={url}",
            "facebook": "https://fdown.net/?url={url}",
            "threads": "https://threadsdownloader.com/?url={url}",
            "bilibili": "https://bilibili.iiilab.com/?url={url}",
            "x": "https://twittervideodownloader.com/?url={url}"
        }
        
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup.json")
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                    # 載入外部下載替代網址設定
                    if "external_urls" in settings:
                        # 合併預設值和用戶設定
                        external_urls = default_urls.copy()
                        external_urls.update(settings["external_urls"])
                        return external_urls
        except Exception as e:
            log(f"載入外部下載替代網址設定失敗: {str(e)}")
            
        return default_urls

    def show_external_download_button(self, filename):
        """顯示外部下載按鈕"""
        # 檢查是否有 external_btn 按鈕
        if filename in self.download_items and 'external_btn' in self.download_items[filename]:
            external_button = self.download_items[filename]['external_btn']
            
            # 獲取URL和平台信息
            url = self.download_items.get(filename, {}).get('url', '')
            platform_name = self.download_items[filename].get('platform_info', "未知")
            
            # 根據平台設置按鈕文字
            button_text = "外部下載"
            if platform_name == "TikTok" or "tiktok.com" in url or "douyin.com" in url:
                button_text = "TikTok下載器"
            elif platform_name == "Facebook" or "facebook.com" in url or "fb.com" in url:
                button_text = "FB下載器"
            elif platform_name == "Instagram" or "instagram.com" in url:
                button_text = "IG下載器"
            elif platform_name == "X" or "twitter.com" in url or "x.com" in url:
                button_text = "X下載器"
            elif platform_name == "Bilibili" or "bilibili.com" in url or "b23.tv" in url:
                button_text = "B站下載器"
            elif platform_name == "Threads" or "threads.net" in url:
                button_text = "Threads下載器"
            
            # 設置按鈕文字和樣式
            external_button.setText(button_text)
            external_button.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;
                    color: white;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c9302c;
                }
            """)
            
            # 顯示按鈕
            external_button.setVisible(True)
                
            # 調整下載項目的高度以確保按鈕顯示完整
            if 'widget' in self.download_items[filename]:
                self.download_items[filename]['widget'].setMinimumHeight(100)
                
        # 向下兼容舊版按鈕
        elif filename in self.download_buttons and 'external' in self.download_buttons[filename]:
            external_button = self.download_buttons[filename]['external']
            
            # 獲取URL和平台信息
            url = self.download_items.get(filename, {}).get('url', '')
            platform_name = self.download_items[filename].get('platform_info', "未知")
            
            # 根據平台設置按鈕文字
            button_text = "外部下載"
            if platform_name == "TikTok" or "tiktok.com" in url or "douyin.com" in url:
                button_text = "TikTok下載器"
            elif platform_name == "Facebook" or "facebook.com" in url or "fb.com" in url:
                button_text = "FB下載器"
            elif platform_name == "Instagram" or "instagram.com" in url:
                button_text = "IG下載器"
            elif platform_name == "X" or "twitter.com" in url or "x.com" in url:
                button_text = "X下載器"
            elif platform_name == "Bilibili" or "bilibili.com" in url or "b23.tv" in url:
                button_text = "B站下載器"
            elif platform_name == "Threads" or "threads.net" in url:
                button_text = "Threads下載器"
            
            # 設置按鈕文字和樣式
            external_button.setText(button_text)
            external_button.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;
                    color: white;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c9302c;
                }
            """)
            
            # 顯示按鈕
            external_button.setVisible(True)
                
            # 調整表格行高以確保按鈕顯示完整
            for row in range(self.download_table.rowCount()):
                item = self.download_table.item(row, 0)
                if item and item.text() == filename:
                    self.download_table.setRowHeight(row, 45)
                    break

class SettingsTab(QWidget):
    """設定標籤頁"""
    
    # 定義信號
    settings_applied = Signal(dict)
    
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
            "平台支援",
            "外部下載替代網址"
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
        self.settings_stack.addWidget(self.create_platform_settings())
        self.settings_stack.addWidget(self.create_external_urls_settings())
        
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
        log("正在套用設定...")
        
        # 收集所有設定
        settings = {
            # 基本設定
            "download_path": self.folder_input.text(),
            "max_concurrent_downloads": int(self.concurrent_combo.currentText()),
            "show_notification": self.notify_cb.isChecked(),
            "play_sound": self.sound_cb.isChecked(),
            "auto_open_folder": self.open_folder_cb.isChecked(),
            "file_exists_action": "ask" if self.ask_radio.isChecked() else 
                                 "rename" if self.rename_radio.isChecked() else 
                                 "overwrite",
            
            # 格式與品質設定
            "default_format": self.default_format_combo.currentText() if hasattr(self, "default_format_combo") else "最高品質",
            "default_resolution": self.default_resolution_combo.currentText() if hasattr(self, "default_resolution_combo") else "自動選擇最佳",
            "audio_quality": self.audio_quality_combo.currentText() if hasattr(self, "audio_quality_combo") else "192 kbps",
            "prefer_av1": self.prefer_av1_cb.isChecked() if hasattr(self, "prefer_av1_cb") else False,
            "fallback_to_webm": self.fallback_to_webm_cb.isChecked() if hasattr(self, "fallback_to_webm_cb") else True,
            "auto_merge": self.auto_merge_cb.isChecked() if hasattr(self, "auto_merge_cb") else True,
            
            # 命名設定
            "default_prefix": self.default_prefix_input.text() if hasattr(self, "default_prefix_input") else "",
            "sanitize_filename": self.sanitize_filename_cb.isChecked() if hasattr(self, "sanitize_filename_cb") else True,
            "add_timestamp": self.add_timestamp_cb.isChecked() if hasattr(self, "add_timestamp_cb") else False,
            "truncate_filename": self.truncate_filename_cb.isChecked() if hasattr(self, "truncate_filename_cb") else True,
            "max_filename_length": self.max_length_spin.value() if hasattr(self, "max_length_spin") else 200,
            "create_subfolders": self.create_subfolders_cb.isChecked() if hasattr(self, "create_subfolders_cb") else False,
            "organize_by_date": self.organize_by_date_cb.isChecked() if hasattr(self, "organize_by_date_cb") else False,
            
            # 網路設定 - 添加 cookies 相關設定
            "use_cookies": self.use_cookies_cb.isChecked() if hasattr(self, "use_cookies_cb") else False,
            "cookies_file": self.cookies_path_input.text() if hasattr(self, "cookies_path_input") else "",
            "use_proxy": self.use_proxy_cb.isChecked() if hasattr(self, "use_proxy_cb") else False,
            "proxy_type": self.proxy_type_combo.currentText() if hasattr(self, "proxy_type_combo") else "HTTP",
            "proxy_address": self.proxy_address_input.text() if hasattr(self, "proxy_address_input") else "",
            "proxy_port": self.proxy_port_input.text() if hasattr(self, "proxy_port_input") else "",
            "use_proxy_auth": self.use_auth_cb.isChecked() if hasattr(self, "use_auth_cb") else False,
            "proxy_username": self.proxy_username_input.text() if hasattr(self, "proxy_username_input") else "",
            "proxy_password": self.proxy_password_input.text() if hasattr(self, "proxy_password_input") else "",
            "retry_count": self.retry_spin.value() if hasattr(self, "retry_spin") else 3,
            "retry_wait": self.wait_spin.value() if hasattr(self, "wait_spin") else 5,
            "timeout": self.timeout_spin.value() if hasattr(self, "timeout_spin") else 60,
            "disable_ssl": self.disable_ssl_cb.isChecked() if hasattr(self, "disable_ssl_cb") else True,
            
            # 外部下載替代網址設定
            "external_urls": {
                "youtube": self.youtube_url_input.text() if hasattr(self, "youtube_url_input") else "https://publer.com/tools/youtube-shorts-downloader?url={url}",
                "instagram": self.ig_url_input.text() if hasattr(self, "ig_url_input") else "https://igram.io/?url={url}",
                "twitter": self.twitter_url_input.text() if hasattr(self, "twitter_url_input") else "https://twittervideodownloader.com/?url={url}",
                "tiktok": self.tiktok_url_input.text() if hasattr(self, "tiktok_url_input") else "https://tiktokio.com/zh_tw/?url={url}",
                "facebook": self.facebook_url_input.text() if hasattr(self, "facebook_url_input") else "https://fdown.net/?url={url}",
                "threads": self.threads_url_input.text() if hasattr(self, "threads_url_input") else "https://threadsdownloader.com/?url={url}"
            }
        }
        
        # 保存到用戶偏好文件
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup.json")
            
            # 讀取現有設定（如果存在）
            existing_settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    try:
                        existing_settings = json.load(f)
                    except:
                        existing_settings = {}
            
            # 更新設定
            existing_settings.update(settings)
            
            # 保存設定
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(existing_settings, f, ensure_ascii=False, indent=4)
                
            log("設定已保存到用戶偏好文件")
        except Exception as e:
            log(f"保存設定失敗: {str(e)}")
        
        # 發送信號通知其他組件
        self.settings_applied.emit(settings)
        
        # 顯示成功訊息
        QMessageBox.information(self, "設定已套用", "設定已成功套用並保存。")
        
        # 如果啟用了 cookies 檔案但檔案不存在，顯示警告
        if settings["use_cookies"] and settings["cookies_file"]:
            if not os.path.exists(settings["cookies_file"]):
                QMessageBox.warning(self, "警告", f"找不到指定的 cookies 檔案:\n{settings['cookies_file']}\n\n請確認檔案路徑是否正確。")
    
    def cancel_changes(self):
        """取消更改"""
        log("取消設定更改")
        # 重新載入設定
        self.load_settings_from_file()
    
    def reset_settings(self):
        """重設為預設值"""
        log("重設設定為預設值")
        # 基本設定
        self.folder_input.setText(str(Path.home() / "Downloads"))
        self.concurrent_combo.setCurrentIndex(1)  # 預設為2
        self.notify_cb.setChecked(True)
        self.sound_cb.setChecked(True)
        self.open_folder_cb.setChecked(False)
        self.rename_radio.setChecked(True)
        
        # 格式與品質設定
        if hasattr(self, "default_format_combo"):
            self.default_format_combo.setCurrentIndex(0)  # 最高品質
        if hasattr(self, "default_resolution_combo"):
            self.default_resolution_combo.setCurrentIndex(0)  # 自動選擇最佳
        if hasattr(self, "audio_quality_combo"):
            self.audio_quality_combo.setCurrentIndex(2)  # 192 kbps
        if hasattr(self, "prefer_av1_cb"):
            self.prefer_av1_cb.setChecked(False)
        if hasattr(self, "fallback_to_webm_cb"):
            self.fallback_to_webm_cb.setChecked(True)
        if hasattr(self, "auto_merge_cb"):
            self.auto_merge_cb.setChecked(True)
        
        # 命名設定
        if hasattr(self, "default_prefix_input"):
            self.default_prefix_input.setText("TEST-")
        if hasattr(self, "sanitize_filename_cb"):
            self.sanitize_filename_cb.setChecked(True)
        if hasattr(self, "add_timestamp_cb"):
            self.add_timestamp_cb.setChecked(False)
        if hasattr(self, "truncate_filename_cb"):
            self.truncate_filename_cb.setChecked(True)
        if hasattr(self, "max_length_spin"):
            self.max_length_spin.setValue(200)
        if hasattr(self, "create_subfolders_cb"):
            self.create_subfolders_cb.setChecked(False)
        if hasattr(self, "organize_by_date_cb"):
            self.organize_by_date_cb.setChecked(False)
            
        # 網路設定 - 重置 cookies 相關設定
        if hasattr(self, "use_cookies_cb"):
            self.use_cookies_cb.setChecked(False)
        if hasattr(self, "cookies_path_input"):
            self.cookies_path_input.setText("")
        if hasattr(self, "use_proxy_cb"):
            self.use_proxy_cb.setChecked(False)
        if hasattr(self, "proxy_type_combo"):
            self.proxy_type_combo.setCurrentIndex(0)  # HTTP
        if hasattr(self, "proxy_address_input"):
            self.proxy_address_input.setText("")
        if hasattr(self, "proxy_port_input"):
            self.proxy_port_input.setText("")
        if hasattr(self, "use_auth_cb"):
            self.use_auth_cb.setChecked(False)
        if hasattr(self, "proxy_username_input"):
            self.proxy_username_input.setText("")
        if hasattr(self, "proxy_password_input"):
            self.proxy_password_input.setText("")
        if hasattr(self, "retry_spin"):
            self.retry_spin.setValue(3)
        if hasattr(self, "wait_spin"):
            self.wait_spin.setValue(5)
        if hasattr(self, "timeout_spin"):
            self.timeout_spin.setValue(60)
        if hasattr(self, "disable_ssl_cb"):
            self.disable_ssl_cb.setChecked(True)
            
        # 外部下載替代網址設定
        if hasattr(self, "ig_url_input"):
            self.ig_url_input.setText("https://igram.io/?url={url}")
        if hasattr(self, "twitter_url_input"):
            self.twitter_url_input.setText("https://twittervideodownloader.com/?url={url}")
        if hasattr(self, "tiktok_url_input"):
            self.tiktok_url_input.setText("https://tiktokio.com/zh_tw/?url={url}")
        if hasattr(self, "facebook_url_input"):
            self.facebook_url_input.setText("https://fdown.net/?url={url}")
        if hasattr(self, "threads_url_input"):
            self.threads_url_input.setText("https://threadsdownloader.com/?url={url}")
    
    def load_settings_from_file(self):
        """從文件載入設定"""
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup.json")
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                    # 載入基本設定
                    if "download_path" in settings:
                        self.folder_input.setText(settings["download_path"])
                    
                    if "max_concurrent_downloads" in settings:
                        index = self.concurrent_combo.findText(str(settings["max_concurrent_downloads"]))
                        if index >= 0:
                            self.concurrent_combo.setCurrentIndex(index)
                    
                    if "show_notification" in settings:
                        self.notify_cb.setChecked(settings["show_notification"])
                    
                    if "play_sound" in settings:
                        self.sound_cb.setChecked(settings["play_sound"])
                    
                    if "auto_open_folder" in settings:
                        self.open_folder_cb.setChecked(settings["auto_open_folder"])
                    
                    if "file_exists_action" in settings:
                        if settings["file_exists_action"] == "ask":
                            self.ask_radio.setChecked(True)
                        elif settings["file_exists_action"] == "rename":
                            self.rename_radio.setChecked(True)
                        elif settings["file_exists_action"] == "overwrite":
                            self.overwrite_radio.setChecked(True)
                    
                    # 載入格式與品質設定
                    if hasattr(self, "default_format_combo") and "default_format" in settings:
                        index = self.default_format_combo.findText(settings["default_format"])
                        if index >= 0:
                            self.default_format_combo.setCurrentIndex(index)
                    
                    if hasattr(self, "default_resolution_combo") and "default_resolution" in settings:
                        index = self.default_resolution_combo.findText(settings["default_resolution"])
                        if index >= 0:
                            self.default_resolution_combo.setCurrentIndex(index)
                    
                    if hasattr(self, "audio_quality_combo") and "audio_quality" in settings:
                        index = self.audio_quality_combo.findText(settings["audio_quality"])
                        if index >= 0:
                            self.audio_quality_combo.setCurrentIndex(index)
                    
                    if hasattr(self, "prefer_av1_cb") and "prefer_av1" in settings:
                        self.prefer_av1_cb.setChecked(settings["prefer_av1"])
                    
                    if hasattr(self, "fallback_to_webm_cb") and "fallback_to_webm" in settings:
                        self.fallback_to_webm_cb.setChecked(settings["fallback_to_webm"])
                    
                    if hasattr(self, "auto_merge_cb") and "auto_merge" in settings:
                        self.auto_merge_cb.setChecked(settings["auto_merge"])
                    
                    # 載入命名設定
                    if hasattr(self, "default_prefix_input") and "default_prefix" in settings:
                        self.default_prefix_input.setText(settings["default_prefix"])
                    
                    if hasattr(self, "sanitize_filename_cb") and "sanitize_filename" in settings:
                        self.sanitize_filename_cb.setChecked(settings["sanitize_filename"])
                    
                    if hasattr(self, "add_timestamp_cb") and "add_timestamp" in settings:
                        self.add_timestamp_cb.setChecked(settings["add_timestamp"])
                    
                    if hasattr(self, "truncate_filename_cb") and "truncate_filename" in settings:
                        self.truncate_filename_cb.setChecked(settings["truncate_filename"])
                    
                    if hasattr(self, "max_length_spin") and "max_filename_length" in settings:
                        self.max_length_spin.setValue(settings["max_filename_length"])
                    
                    if hasattr(self, "create_subfolders_cb") and "create_subfolders" in settings:
                        self.create_subfolders_cb.setChecked(settings["create_subfolders"])
                    
                    if hasattr(self, "organize_by_date_cb") and "organize_by_date" in settings:
                        self.organize_by_date_cb.setChecked(settings["organize_by_date"])
                        
                    # 載入網路設定 - 添加 cookies 相關設定
                    if hasattr(self, "use_cookies_cb") and "use_cookies" in settings:
                        self.use_cookies_cb.setChecked(settings["use_cookies"])
                        
                    if hasattr(self, "cookies_path_input") and "cookies_file" in settings:
                        self.cookies_path_input.setText(settings["cookies_file"])
                        
                    if hasattr(self, "use_proxy_cb") and "use_proxy" in settings:
                        self.use_proxy_cb.setChecked(settings["use_proxy"])
                        
                    if hasattr(self, "proxy_type_combo") and "proxy_type" in settings:
                        index = self.proxy_type_combo.findText(settings["proxy_type"])
                        if index >= 0:
                            self.proxy_type_combo.setCurrentIndex(index)
                            
                    if hasattr(self, "proxy_address_input") and "proxy_address" in settings:
                        self.proxy_address_input.setText(settings["proxy_address"])
                        
                    if hasattr(self, "proxy_port_input") and "proxy_port" in settings:
                        self.proxy_port_input.setText(settings["proxy_port"])
                        
                    if hasattr(self, "use_auth_cb") and "use_proxy_auth" in settings:
                        self.use_auth_cb.setChecked(settings["use_proxy_auth"])
                        
                    if hasattr(self, "proxy_username_input") and "proxy_username" in settings:
                        self.proxy_username_input.setText(settings["proxy_username"])
                        
                    if hasattr(self, "proxy_password_input") and "proxy_password" in settings:
                        self.proxy_password_input.setText(settings["proxy_password"])
                        
                    if hasattr(self, "retry_spin") and "retry_count" in settings:
                        self.retry_spin.setValue(settings["retry_count"])
                        
                    if hasattr(self, "wait_spin") and "retry_wait" in settings:
                        self.wait_spin.setValue(settings["retry_wait"])
                        
                    if hasattr(self, "timeout_spin") and "timeout" in settings:
                        self.timeout_spin.setValue(settings["timeout"])
                        
                    if hasattr(self, "disable_ssl_cb") and "disable_ssl" in settings:
                        self.disable_ssl_cb.setChecked(settings["disable_ssl"])
                    
                    log("從文件載入設定成功")
        except Exception as e:
            log(f"載入設定失敗: {str(e)}")

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
        
        self.auto_merge_cb = QCheckBox("自動合併影片與音訊 (高畫質影片將始終合併)")
        self.auto_merge_cb.setChecked(True)
        merge_layout.addWidget(self.auto_merge_cb)
        
        self.keep_separate_cb = QCheckBox("保留未合併的原始檔案")
        self.keep_separate_cb.setChecked(False)
        merge_layout.addWidget(self.keep_separate_cb)
        
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
        
        # 連接信號
        apply_btn.clicked.connect(self.apply_settings)
        cancel_btn.clicked.connect(self.cancel_changes)
        reset_btn.clicked.connect(self.reset_settings)
        
        return format_widget

    def create_network_settings(self):
        """創建網路設定頁面"""
        network_widget = QWidget()
        network_layout = QVBoxLayout(network_widget)
        
        # 代理設定組
        proxy_group = QGroupBox("代理伺服器設定")
        proxy_layout = QVBoxLayout(proxy_group)
        
        # 使用代理
        self.use_proxy_cb = QCheckBox("使用代理伺服器")
        self.use_proxy_cb.setChecked(False)
        proxy_layout.addWidget(self.use_proxy_cb)
        
        # 代理類型
        proxy_type_layout = QHBoxLayout()
        proxy_type_layout.addWidget(QLabel("代理類型:"))
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "HTTPS", "SOCKS4", "SOCKS5"])
        proxy_type_layout.addWidget(self.proxy_type_combo)
        proxy_type_layout.addStretch(1)
        proxy_layout.addLayout(proxy_type_layout)
        
        # 代理地址和端口
        proxy_address_layout = QHBoxLayout()
        proxy_address_layout.addWidget(QLabel("代理地址:"))
        self.proxy_address_input = QLineEdit()
        proxy_address_layout.addWidget(self.proxy_address_input)
        proxy_address_layout.addWidget(QLabel("端口:"))
        self.proxy_port_input = QLineEdit()
        self.proxy_port_input.setMaximumWidth(80)
        proxy_address_layout.addWidget(self.proxy_port_input)
        proxy_layout.addLayout(proxy_address_layout)
        
        # 代理認證
        self.use_auth_cb = QCheckBox("使用代理認證")
        self.use_auth_cb.setChecked(False)
        proxy_layout.addWidget(self.use_auth_cb)
        
        # 代理用戶名和密碼
        proxy_auth_layout = QHBoxLayout()
        proxy_auth_layout.addWidget(QLabel("用戶名:"))
        self.proxy_username_input = QLineEdit()
        proxy_auth_layout.addWidget(self.proxy_username_input)
        proxy_auth_layout.addWidget(QLabel("密碼:"))
        self.proxy_password_input = QLineEdit()
        self.proxy_password_input.setEchoMode(QLineEdit.Password)
        proxy_auth_layout.addWidget(self.proxy_password_input)
        proxy_layout.addLayout(proxy_auth_layout)
        
        network_layout.addWidget(proxy_group)
        
        # 添加 Cookies 設定組
        cookies_group = QGroupBox("Cookies 設定 (用於登入需要的平台)")
        cookies_layout = QVBoxLayout(cookies_group)
        
        # 使用 cookies 檔案
        self.use_cookies_cb = QCheckBox("使用 cookies.txt 檔案登入 (解決私人內容、年齡限制等問題)")
        self.use_cookies_cb.setChecked(False)
        cookies_layout.addWidget(self.use_cookies_cb)
        
        # cookies 檔案路徑
        cookies_path_layout = QHBoxLayout()
        cookies_path_layout.addWidget(QLabel("Cookies 檔案:"))
        self.cookies_path_input = QLineEdit()
        self.cookies_path_input.setPlaceholderText("選擇 cookies.txt 檔案...")
        cookies_path_layout.addWidget(self.cookies_path_input)
        
        # 瀏覽按鈕
        self.browse_cookies_btn = QPushButton("瀏覽...")
        self.browse_cookies_btn.clicked.connect(self.browse_cookies)
        cookies_path_layout.addWidget(self.browse_cookies_btn)
        
        cookies_layout.addLayout(cookies_path_layout)
        
        # 幫助文字
        cookies_help = QLabel("提示：您可以使用瀏覽器擴充功能 (如 'Get cookies.txt') 匯出 cookies.txt 檔案，\n"
                             "這對於下載需要登入的內容（如Facebook私人影片、Instagram限定內容）非常有用。")
        cookies_help.setWordWrap(True)
        cookies_help.setStyleSheet("color: #666; font-style: italic;")
        cookies_layout.addWidget(cookies_help)
        
        network_layout.addWidget(cookies_group)
        
        # 重試設定
        retry_group = QGroupBox("重試設定")
        retry_layout = QVBoxLayout(retry_group)
        
        # 重試次數
        retry_count_layout = QHBoxLayout()
        retry_count_layout.addWidget(QLabel("重試次數:"))
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 10)
        self.retry_spin.setValue(3)
        retry_count_layout.addWidget(self.retry_spin)
        retry_count_layout.addStretch(1)
        retry_layout.addLayout(retry_count_layout)
        
        # 重試等待時間
        retry_wait_layout = QHBoxLayout()
        retry_wait_layout.addWidget(QLabel("重試等待時間 (秒):"))
        self.wait_spin = QSpinBox()
        self.wait_spin.setRange(1, 60)
        self.wait_spin.setValue(5)
        retry_wait_layout.addWidget(self.wait_spin)
        retry_wait_layout.addStretch(1)
        retry_layout.addLayout(retry_wait_layout)
        
        # 連接超時
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("連接超時 (秒):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(60)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch(1)
        retry_layout.addLayout(timeout_layout)
        
        network_layout.addWidget(retry_group)
        
        # SSL 設定
        ssl_group = QGroupBox("SSL 設定")
        ssl_layout = QVBoxLayout(ssl_group)
        
        self.disable_ssl_cb = QCheckBox("禁用 SSL 驗證 (解決某些 SSL 錯誤)")
        self.disable_ssl_cb.setChecked(True)
        ssl_layout.addWidget(self.disable_ssl_cb)
        
        network_layout.addWidget(ssl_group)
        
        # 添加伸展空間
        network_layout.addStretch(1)
        
        return network_widget

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
        
        # 添加清空前綴按鈕
        self.clear_prefix_btn = QPushButton("清空前綴")
        self.clear_prefix_btn.clicked.connect(lambda: self.default_prefix_input.setText(""))
        prefix_layout.addWidget(self.clear_prefix_btn)
        
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
        
        # 連接信號
        apply_btn.clicked.connect(self.apply_settings)
        cancel_btn.clicked.connect(self.cancel_changes)
        reset_btn.clicked.connect(self.reset_settings)
        self.use_selected_prefix_btn.clicked.connect(self.use_selected_prefix)
        self.remove_prefix_btn.clicked.connect(self.remove_selected_prefix)
        
        return naming_widget
        
    def use_selected_prefix(self):
        """使用選中的前綴"""
        selected_items = self.prefix_history_list.selectedItems()
        if selected_items:
            selected_prefix = selected_items[0].text()
            self.default_prefix_input.setText(selected_prefix)
            log(f"已選擇前綴: {selected_prefix}")
            
    def remove_selected_prefix(self):
        """移除選中的前綴"""
        selected_items = self.prefix_history_list.selectedItems()
        if selected_items:
            row = self.prefix_history_list.row(selected_items[0])
            selected_prefix = selected_items[0].text()
            self.prefix_history_list.takeItem(row)
            log(f"已移除前綴: {selected_prefix}")

    def create_platform_settings(self):
        """創建平台支援設定頁面"""
        platform_widget = QWidget()
        platform_layout = QVBoxLayout(platform_widget)
        
        # 支援平台說明
        platform_group = QGroupBox("支援的平台")
        platform_group_layout = QVBoxLayout(platform_group)
        
        # 添加支援的平台列表
        supported_platforms = get_supported_platforms()
        for platform in supported_platforms:
            platform_item = QLabel(f"• {platform}")
            platform_item.setStyleSheet("font-size: 11pt; margin: 5px;")
            platform_group_layout.addWidget(platform_item)
        
        platform_layout.addWidget(platform_group)
        
        # 平台特定說明
        notes_group = QGroupBox("平台特別說明")
        notes_layout = QVBoxLayout(notes_group)
        
        notes = [
            ("YouTube", "支援大多數公開影片，年齡限制內容需要cookies。"),
            ("TikTok / 抖音", "支援公開影片和部分私人影片。"),
            ("Facebook", "需要cookies才能下載私人或僅限朋友可見的內容。"),
            ("Instagram", "需要cookies才能下載私人帳號或限時動態內容。"),
            ("Bilibili", "支援大多數公開影片和部分會員專屬內容。"),
            ("X (Twitter)", "支援公開推文中的影片和圖片。")
        ]
        
        for platform, note in notes:
            note_label = QLabel(f"<b>{platform}</b>: {note}")
            note_label.setWordWrap(True)
            note_label.setStyleSheet("margin: 5px;")
            notes_layout.addWidget(note_label)
        
        platform_layout.addWidget(notes_group)
        
        # Cookies說明
        cookies_group = QGroupBox("關於Cookies")
        cookies_layout = QVBoxLayout(cookies_group)
        
        cookies_label = QLabel(
            "某些平台的內容需要登入才能訪問，此時您需要提供cookies.txt檔案。\n\n"
            "獲取cookies.txt的方法：\n"
            "1. 在瀏覽器中安裝「Get cookies.txt」或類似的擴充功能\n"
            "2. 登入需要的平台（如Facebook、Instagram等）\n"
            "3. 使用擴充功能匯出cookies.txt檔案\n"
            "4. 在「網路設定」中啟用cookies並選擇該檔案\n\n"
            "注意：cookies檔案包含您的登入資訊，請妥善保管，不要分享給他人"
        )
        cookies_label.setWordWrap(True)
        cookies_layout.addWidget(cookies_label)
        
        platform_layout.addWidget(cookies_group)
        
        # 添加伸展空間
        platform_layout.addStretch(1)
        
        return platform_widget

    def create_external_urls_settings(self):
        """創建外部下載替代網址設定頁面"""
        external_urls_widget = QWidget()
        layout = QVBoxLayout(external_urls_widget)
        
        # 說明文字
        description_label = QLabel(
            "當下載失敗時，系統會顯示紅色的外部下載按鈕，點擊後會開啟瀏覽器前往下方設定的網站。\n"
            "您可以自訂每個平台的外部下載網址，其中 {url} 將被替換為實際的影片網址。\n"
            "如果留空，則使用預設值。"
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("margin-bottom: 15px;")
        layout.addWidget(description_label)
        
        # 創建表單佈局
        form_layout = QGridLayout()
        form_layout.setColumnStretch(1, 1)  # 讓輸入框列可以伸展
        
        # 添加各平台的設定
        # YouTube
        form_layout.addWidget(QLabel("YouTube:"), 0, 0)
        self.youtube_url_input = QLineEdit()
        self.youtube_url_input.setPlaceholderText("https://publer.com/tools/youtube-shorts-downloader?url={url}")
        form_layout.addWidget(self.youtube_url_input, 0, 1)
        
        # Instagram
        form_layout.addWidget(QLabel("Instagram:"), 1, 0)
        self.ig_url_input = QLineEdit()
        self.ig_url_input.setPlaceholderText("https://igram.io/?url={url}")
        form_layout.addWidget(self.ig_url_input, 1, 1)
        
        # Twitter/X
        form_layout.addWidget(QLabel("Twitter/X:"), 2, 0)
        self.twitter_url_input = QLineEdit()
        self.twitter_url_input.setPlaceholderText("https://twittervideodownloader.com/?url={url}")
        form_layout.addWidget(self.twitter_url_input, 2, 1)
        
        # TikTok
        form_layout.addWidget(QLabel("TikTok:"), 3, 0)
        self.tiktok_url_input = QLineEdit()
        self.tiktok_url_input.setPlaceholderText("https://tiktokio.com/zh_tw/?url={url}")
        form_layout.addWidget(self.tiktok_url_input, 3, 1)
        
        # Facebook
        form_layout.addWidget(QLabel("Facebook:"), 4, 0)
        self.facebook_url_input = QLineEdit()
        self.facebook_url_input.setPlaceholderText("https://fdown.net/?url={url}")
        form_layout.addWidget(self.facebook_url_input, 4, 1)
        
        # Threads
        form_layout.addWidget(QLabel("Threads:"), 5, 0)
        self.threads_url_input = QLineEdit()
        self.threads_url_input.setPlaceholderText("https://threadsdownloader.com/?url={url}")
        form_layout.addWidget(self.threads_url_input, 5, 1)
        
        # 添加表單到主佈局
        form_group = QGroupBox("外部下載替代網址")
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        
        # 還原預設按鈕
        reset_urls_btn = QPushButton("還原預設網址")
        reset_urls_btn.clicked.connect(self.reset_external_urls)
        buttons_layout.addWidget(reset_urls_btn)
        
        buttons_layout.addStretch(1)
        
        # 套用按鈕
        apply_urls_btn = QPushButton("立即套用")
        apply_urls_btn.clicked.connect(self.apply_external_urls)
        buttons_layout.addWidget(apply_urls_btn)
        
        layout.addLayout(buttons_layout)
        
        # 添加伸展空間
        layout.addStretch(1)
        
        # 載入現有設定
        self.load_external_urls_settings()
        
        return external_urls_widget
        
    def load_external_urls_settings(self):
        """載入外部下載替代網址設定"""
        try:
            settings_path = get_settings_path()
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                    # 載入外部下載替代網址設定
                    if "external_urls" in settings:
                        external_urls = settings["external_urls"]
                        if "youtube" in external_urls:
                            self.youtube_url_input.setText(external_urls["youtube"])
                        if "instagram" in external_urls:
                            self.ig_url_input.setText(external_urls["instagram"])
                        if "twitter" in external_urls:
                            self.twitter_url_input.setText(external_urls["twitter"])
                        if "tiktok" in external_urls:
                            self.tiktok_url_input.setText(external_urls["tiktok"])
                        if "facebook" in external_urls:
                            self.facebook_url_input.setText(external_urls["facebook"])
                        if "threads" in external_urls:
                            self.threads_url_input.setText(external_urls["threads"])
        except Exception as e:
            log(f"載入外部下載替代網址設定失敗: {str(e)}")
            
    def reset_external_urls(self):
        """還原預設外部下載替代網址"""
        self.youtube_url_input.setText("https://publer.com/tools/youtube-shorts-downloader?url={url}")
        self.ig_url_input.setText("https://igram.io/?url={url}")
        self.twitter_url_input.setText("https://twittervideodownloader.com/?url={url}")
        self.tiktok_url_input.setText("https://tiktokio.com/zh_tw/?url={url}")
        self.facebook_url_input.setText("https://fdown.net/?url={url}")
        self.threads_url_input.setText("https://threadsdownloader.com/?url={url}")
        
        QMessageBox.information(self, "還原完成", "已還原所有外部下載替代網址為預設值")
        
    def apply_external_urls(self):
        """立即套用外部下載替代網址設定"""
        # 收集設定
        external_urls = {
            "youtube": self.youtube_url_input.text() or "https://publer.com/tools/youtube-shorts-downloader?url={url}",
            "instagram": self.ig_url_input.text() or "https://igram.io/?url={url}",
            "twitter": self.twitter_url_input.text() or "https://twittervideodownloader.com/?url={url}",
            "tiktok": self.tiktok_url_input.text() or "https://tiktokio.com/zh_tw/?url={url}",
            "facebook": self.facebook_url_input.text() or "https://fdown.net/?url={url}",
            "threads": self.threads_url_input.text() or "https://threadsdownloader.com/?url={url}"
        }
        
        # 保存到用戶偏好文件
        try:
            settings_path = get_settings_path()
            
            # 讀取現有設定（如果存在）
            existing_settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    try:
                        existing_settings = json.load(f)
                    except:
                        existing_settings = {}
            
            # 更新設定
            existing_settings["external_urls"] = external_urls
            
            # 保存設定
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(existing_settings, f, ensure_ascii=False, indent=4)
                
            log("外部下載替代網址設定已保存")
            QMessageBox.information(self, "設定已套用", "外部下載替代網址設定已成功套用並保存。")
        except Exception as e:
            log(f"保存外部下載替代網址設定失敗: {str(e)}")
            QMessageBox.warning(self, "保存失敗", f"無法保存外部下載替代網址設定: {str(e)}")

    def browse_cookies(self):
        """瀏覽 cookies 檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "選擇 cookies.txt 檔案", 
            "", 
            "Text files (*.txt);;All files (*.*)"
        )
        if file_path:
            self.cookies_path_input.setText(file_path)

    def create_performance_settings(self):
        """創建效能設定頁面"""
        performance_widget = QWidget()
        performance_layout = QVBoxLayout(performance_widget)
        
        # 下載效能設定
        performance_group = QGroupBox("下載效能設定")
        perf_layout = QVBoxLayout(performance_group)
        
        # 緩衝區大小
        buffer_layout = QHBoxLayout()
        buffer_layout.addWidget(QLabel("下載緩衝區大小 (MB):"))
        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(1, 100)
        self.buffer_size_spin.setValue(16)
        buffer_layout.addWidget(self.buffer_size_spin)
        buffer_layout.addStretch(1)
        perf_layout.addLayout(buffer_layout)
        
        # 下載速度限制
        speed_limit_layout = QHBoxLayout()
        speed_limit_layout.addWidget(QLabel("下載速度限制 (KB/s):"))
        self.speed_limit_spin = QSpinBox()
        self.speed_limit_spin.setRange(0, 10000)
        self.speed_limit_spin.setValue(0)  # 0 表示無限制
        speed_limit_layout.addWidget(self.speed_limit_spin)
        speed_limit_layout.addStretch(1)
        perf_layout.addLayout(speed_limit_layout)
        
        # 記憶體使用設定
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("最大記憶體使用量 (MB):"))
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(100, 2000)
        self.memory_limit_spin.setValue(500)
        memory_layout.addWidget(self.memory_limit_spin)
        memory_layout.addStretch(1)
        perf_layout.addLayout(memory_layout)
        
        performance_layout.addWidget(performance_group)
        
        # 系統資源設定
        system_group = QGroupBox("系統資源設定")
        system_layout = QVBoxLayout(system_group)
        
        self.auto_pause_cb = QCheckBox("下載時自動暫停其他應用程式")
        self.auto_pause_cb.setChecked(False)
        system_layout.addWidget(self.auto_pause_cb)
        
        self.low_priority_cb = QCheckBox("使用低優先級下載 (減少系統負載)")
        self.low_priority_cb.setChecked(True)
        system_layout.addWidget(self.low_priority_cb)
        
        performance_layout.addWidget(system_group)
        
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
        
        # 連接信號
        apply_btn.clicked.connect(self.apply_settings)
        cancel_btn.clicked.connect(self.cancel_changes)
        reset_btn.clicked.connect(self.reset_settings)
        
        return performance_widget

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
        
        # 載入設定
        settings_path = get_settings_path()
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                
                # 載入基本設定
                self.download_path = settings.get("download_path", os.path.join(os.path.expanduser("~"), "Downloads"))
                self.font_size = settings.get("font_size", 11)
                self.content_font_size = settings.get("content_font_size", 11)
                window_title = settings.get("window_title", "多平台影片下載器")
                self.setWindowTitle(window_title)
                
                log(f"已從setup.json載入基本設定")
            except Exception as e:
                log(f"載入設定檔失敗: {str(e)}")
        else:
            # 使用預設設定
            self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            self.font_size = 11
            self.content_font_size = 11
            self.setWindowTitle("多平台影片下載器")
        
        # 載入視窗大小和位置設定
        self.load_window_settings()
        
        # 設置應用程式圖示
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 初始化UI
        self.init_ui()
        
        # 應用樣式
        self.apply_styles()
        
        # 顯示狀態欄
        self.statusBar().showMessage("就緒")
    
    def load_window_settings(self):
        """載入視窗大小和位置設定"""
        try:
            settings_path = get_settings_path()
            
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                    # 載入視窗標題
                    if "window_title" in settings:
                        self.setWindowTitle(settings["window_title"])
                        log(f"已載入視窗標題: {settings['window_title']}")
                    
                    # 載入字體大小設定
                    if "font_size" in settings:
                        self.font_size = settings["font_size"]
                        log(f"已載入字體大小設定: {self.font_size}")
                    
                    # 載入內容字體大小設定
                    if "content_font_size" in settings:
                        self.content_font_size = settings["content_font_size"]
                        log(f"已載入內容字體大小設定: {self.content_font_size}")
                    
                    # 載入下載路徑
                    if "download_path" in settings:
                        self.download_path = settings["download_path"]
                        log(f"已載入下載路徑: {self.download_path}")
                    
                    # 載入視窗大小和位置
                    if "window_geometry" in settings:
                        geometry = settings["window_geometry"]
                        if "x" in geometry and "y" in geometry and "width" in geometry and "height" in geometry:
                            # 檢查視窗是否在螢幕範圍內
                            screen_geo = QApplication.primaryScreen().geometry()
                            if (geometry["x"] < screen_geo.width() and 
                                geometry["y"] < screen_geo.height() and
                                geometry["x"] + geometry["width"] > 0 and
                                geometry["y"] + geometry["height"] > 0):
                                self.setGeometry(
                                    geometry["x"], 
                                    geometry["y"], 
                                    geometry["width"], 
                                    geometry["height"]
                                )
                                log(f"已載入視窗大小和位置設定: {geometry}")
                                
                                # 檢查是否需要最大化
                                if settings.get("window_maximized", False):
                                    self.showMaximized()
                                    log("已將視窗設為最大化")
                    
                    log(f"已從 {settings_path} 載入設定")
            else:
                # 如果沒有設定或設定不完整，使用預設值
                self.setGeometry(100, 100, 1200, 800)
                self.setMinimumSize(800, 600)
                log("未找到設定檔，使用預設視窗大小和位置")
        
        except Exception as e:
            log(f"載入視窗設定失敗: {str(e)}")
            self.setGeometry(100, 100, 1200, 800)
            self.setMinimumSize(800, 600)
        
    def init_ui(self):
        # 創建中央部件和佈局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 創建頂部工具列 - 添加字體大小調整按鈕
        toolbar_layout = QHBoxLayout()
        
        # 字體大小調整按鈕
        font_label = QLabel("文字大小:")
        self.font_size_label = QLabel(f"{self.font_size}")
        self.font_size_label.setAlignment(Qt.AlignCenter)
        self.font_size_label.setMinimumWidth(30)
        
        font_decrease_btn = QPushButton("-")
        font_decrease_btn.setFixedSize(30, 30)
        font_decrease_btn.clicked.connect(self.decrease_font_size)
        font_decrease_btn.setToolTip("減小介面字體大小")
        
        font_increase_btn = QPushButton("+")
        font_increase_btn.setFixedSize(30, 30)
        font_increase_btn.clicked.connect(self.increase_font_size)
        font_increase_btn.setToolTip("增加介面字體大小")
        
        toolbar_layout.addWidget(font_label)
        toolbar_layout.addWidget(font_decrease_btn)
        toolbar_layout.addWidget(self.font_size_label)
        toolbar_layout.addWidget(font_increase_btn)
        toolbar_layout.addStretch(1)
        
        main_layout.addLayout(toolbar_layout)
        
        # 創建頁籤部件
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 導入進度頁籤 - 使用適應打包環境的導入方式
        try:
            # 先嘗試直接導入（適用於開發環境）
            try:
                from src.progress_tab import ProgressTab
            except ImportError:
                # 如果無法從src導入，嘗試從當前路徑導入（適用於打包環境）
                from progress_tab import ProgressTab
        except ImportError as e:
            # 導入失敗時記錄錯誤
            log(f"導入進度標籤頁失敗: {str(e)}")
            # 使用備用方案：在打包環境中，可能需要從其他路徑導入
            import importlib.util
            import os
            
            # 嘗試從同級目錄導入
            progress_tab_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'progress_tab.py')
            if not os.path.exists(progress_tab_path):
                # 如果在打包環境中，嘗試查找進度標籤頁模塊
                log(f"嘗試在打包環境中查找progress_tab.py...")
                if hasattr(sys, '_MEIPASS'):
                    progress_tab_path = os.path.join(sys._MEIPASS, 'progress_tab.py')
            
            if os.path.exists(progress_tab_path):
                log(f"找到進度標籤頁模塊: {progress_tab_path}")
                spec = importlib.util.spec_from_file_location("progress_tab", progress_tab_path)
                progress_tab_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(progress_tab_module)
                ProgressTab = progress_tab_module.ProgressTab
            else:
                # 如果仍然找不到，使用一個簡單的替代實現
                log(f"無法找到進度標籤頁模塊，使用簡易替代實現")
                class ProgressTab(QWidget):
                    def __init__(self, parent=None, download_path=None):
                        super().__init__(parent)
                        layout = QVBoxLayout(self)
                        layout.addWidget(QLabel("無法加載進度標籤頁模塊"))
                    def save_settings(self):
                        pass
        
        # 創建下載頁籤
        self.download_tab = DownloadTab(parent=self, download_path=self.download_path)
        self.tab_widget.addTab(self.download_tab, "下載任務")
        self.tab_widget.setTabToolTip(0, "管理影片下載任務")
        
        # 創建下載進度頁籤
        self.progress_tab = ProgressTab(parent=self, download_path=self.download_path)
        self.tab_widget.addTab(self.progress_tab, "下載進度")
        self.tab_widget.setTabToolTip(1, "監控下載進度和管理任務")
        
        # 創建設定頁籤
        self.settings_tab = SettingsTab(self)
        self.tab_widget.addTab(self.settings_tab, "設定")
        self.tab_widget.setTabToolTip(2, "調整下載器設定")
        
        # 連接設定應用信號
        self.settings_tab.settings_applied.connect(self.on_settings_applied)
        
        # 恢復上次選擇的標籤頁
        try:
            settings_path = get_settings_path()
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    if "current_tab_index" in settings:
                        tab_index = settings["current_tab_index"]
                        if 0 <= tab_index < self.tab_widget.count():
                            self.tab_widget.setCurrentIndex(tab_index)
                            log(f"已恢復標籤頁索引: {tab_index}")
        except Exception as e:
            log(f"恢復標籤頁索引失敗: {str(e)}")
        
    def on_settings_applied(self, settings):
        """當設定被應用時更新下載路徑"""
        self.download_path = settings["download_path"]
        self.download_tab.set_download_path(self.download_path)
        
        # 更新現有下載項目的前綴
        if "default_prefix" in settings:
            self.download_tab.update_download_prefix(settings["default_prefix"])
        
        # 切換回下載頁籤
        self.tab_widget.setCurrentIndex(0)
        
    def apply_styles(self):
        # 設置應用程式樣式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #cccccc;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #eeeeee;
            }
            QStatusBar {
                background-color: #f0f0f0;
                color: #555555;
                border-top: 1px solid #cccccc;
            }
        """)
    
    def increase_font_size(self):
        """增加字體大小"""
        if self.font_size < 20:  # 設置上限
            self.font_size += 1
            self.update_font_size()
            
    def decrease_font_size(self):
        """減少字體大小"""
        if self.font_size > 8:  # 設置下限
            self.font_size -= 1
            self.update_font_size()
            
    def update_font_size(self):
        """更新字體大小"""
        self.font_size_label.setText(f"{self.font_size}")
        
        # 更新應用程式字體
        font = QFont()
        font.setPointSize(self.font_size)
        QApplication.setFont(font)
        
        # 更新所有頁籤的字體大小
        if hasattr(self, 'download_tab'):
            self.update_tab_font_size(self.download_tab)
        
        if hasattr(self, 'settings_tab'):
            self.update_tab_font_size(self.settings_tab)
        
        # 保存字體大小設定
        self.save_font_size()
        
    def update_tab_font_size(self, tab):
        """更新指定頁籤的所有控件字體大小"""
        # 遞迴更新所有子控件的字體大小
        for child in tab.findChildren(QWidget):
            font = child.font()
            font.setPointSize(self.font_size)
            child.setFont(font)
        
    def save_font_size(self):
        """保存字體大小設定"""
        try:
            settings_path = get_settings_path()
            
            # 讀取現有設定（如果存在）
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    try:
                        settings = json.load(f)
                    except:
                        settings = {}
            
            # 更新字體大小設定
            settings["font_size"] = self.font_size
            settings["content_font_size"] = getattr(self, 'content_font_size', self.font_size)
            
            # 保存設定
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            log(f"已保存字體大小設定: 介面字體={self.font_size}, 內容字體={getattr(self, 'content_font_size', self.font_size)}")
        except Exception as e:
            log(f"保存字體大小設定失敗: {str(e)}")
    
    def save_window_settings(self):
        """保存視窗大小和位置設定"""
        try:
            settings_path = get_settings_path()
            
            # 讀取現有設定（如果存在）
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    try:
                        settings = json.load(f)
                    except:
                        settings = {}
            
            # 獲取當前視窗位置和大小
            geometry = self.geometry()
            window_geometry = {
                "x": geometry.x(),
                "y": geometry.y(),
                "width": geometry.width(),
                "height": geometry.height()
            }
            
            # 更新設定
            settings["window_title"] = self.windowTitle()
            settings["window_geometry"] = window_geometry
            settings["font_size"] = self.font_size
            settings["content_font_size"] = getattr(self, 'content_font_size', self.font_size)
            settings["download_path"] = self.download_path
            
            # 保存是否最大化
            settings["window_maximized"] = self.isMaximized()
            
            # 保存標籤頁索引
            settings["current_tab_index"] = self.tab_widget.currentIndex()
            
            # 確保UI設定存在
            if "ui_settings" not in settings:
                settings["ui_settings"] = {}
            
            # 保存下載頁籤的前綴設定
            if hasattr(self, 'download_tab') and hasattr(self.download_tab, 'prefix_combo'):
                current_prefix = self.download_tab.prefix_combo.currentText()
                settings["current_prefix"] = current_prefix
                
                # 保存前綴歷史
                if hasattr(self.download_tab, 'prefix_history'):
                    settings["prefix_history"] = self.download_tab.prefix_history
            
            # 保存設定
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            log(f"已保存所有設定到setup.json: {settings_path}")
        except Exception as e:
            log(f"保存設定失敗: {str(e)}")
            
    def closeEvent(self, event):
        """關閉視窗時的處理"""
        log("關閉主視窗...")
        
        # 保存視窗大小和位置
        self.save_window_settings()
        
        # 保存進度標籤頁設定
        if hasattr(self, 'progress_tab') and hasattr(self.progress_tab, 'save_settings'):
            try:
                self.progress_tab.save_settings()
                log("已保存進度標籤頁設定")
            except Exception as e:
                log(f"保存進度標籤頁設定失敗: {str(e)}")
        
        # 更新版本信息
        try:
            settings_path = get_settings_path()
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                settings["version"] = "1.73"  # 更新版本號
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
                log("已更新設定檔版本信息")
        except Exception as e:
            log(f"更新設定檔版本信息失敗: {str(e)}")
        
        # 檢查是否有正在進行的下載
        active_downloads = False
        if hasattr(self, 'download_tab') and hasattr(self.download_tab, 'download_threads'):
            active_downloads = len(self.download_tab.download_threads) > 0
        
        if active_downloads:
            # 詢問用戶是否確定要退出
            reply = QMessageBox.question(
                self, 
                "確認退出", 
                "有下載任務正在進行中，確定要退出嗎？\n退出將取消所有正在進行的下載。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        # 取消所有下載
        if hasattr(self, 'download_tab') and hasattr(self.download_tab, 'download_threads'):
            for filename, thread in list(self.download_tab.download_threads.items()):
                try:
                    log(f"取消下載線程: {filename}")
                    thread.cancel()
                    thread.wait(500)  # 等待最多0.5秒
                except Exception as e:
                    log(f"取消下載線程時發生錯誤: {str(e)}")
        
        # 關閉所有對話框
        if hasattr(self, 'download_tab'):
            # 關閉錯誤對話框
            if hasattr(self.download_tab, 'error_dialogs'):
                for dialog in list(self.download_tab.error_dialogs.values()):
                    try:
                        dialog.close()
                    except Exception as e:
                        log(f"關閉錯誤對話框時發生錯誤: {str(e)}")
            
            # 關閉格式選項對話框
            if hasattr(self.download_tab, 'format_dialogs'):
                for dialog in list(self.download_tab.format_dialogs.values()):
                    try:
                        dialog.close()
                    except Exception as e:
                        log(f"關閉格式選項對話框時發生錯誤: {str(e)}")
        
        log("主視窗關閉，應用程式即將退出")
        event.accept()

def check_create_setup_json():
    """檢查setup.json是否存在，如果不存在則創建一個預設的設定檔"""
    settings_path = get_settings_path()
    
    log(f"檢查設定檔: {settings_path}")
    
    if not os.path.exists(settings_path):
        log("未找到setup.json，創建預設設定檔...")
        default_settings = {
            "window_title": "多平台影片下載器",
            "window_geometry": {
                "x": 100,
                "y": 100,
                "width": 1200,
                "height": 800
            },
            "window_maximized": False,
            "font_size": 11,
            "content_font_size": 11,
            "download_path": str(Path.home() / "Downloads"),
            "max_concurrent_downloads": 2,
            "current_format": "最高品質",
            "current_resolution": "最高畫質",
            "current_prefix": "",
            "auto_merge": True,
            "current_tab_index": 0,
            "com_port": "COM1",
            "com_timeout": 1000,
            "end_string": "\r\n",
            "ip_address": "127.0.0.1",
            "ui_settings": {
                "files_tab_splitter": [700, 300]
            },
            "download_tab": {},
            "external_urls": {
                "youtube": "https://publer.com/tools/youtube-shorts-downloader?url={url}",
                "instagram": "https://igram.io/?url={url}",
                "twitter": "https://twittervideodownloader.com/?url={url}",
                "tiktok": "https://tiktokio.com/zh_tw/?url={url}",
                "facebook": "https://fdown.net/?url={url}",
                "threads": "https://threadsdownloader.com/?url={url}",
                "bilibili": "https://bilibili.iiilab.com/?url={url}",
                "x": "https://twittervideodownloader.com/?url={url}",
                "unknown": "https://savefrom.net/?url={url}"
            },
            "version": "1.73"
        }
        
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=4)
            log(f"已創建預設setup.json設定檔於: {settings_path}")
        except Exception as e:
            log(f"創建setup.json失敗: {str(e)}")
    else:
        log(f"找到現有setup.json: {settings_path}")
    
    return settings_path

def main():
    """主函數"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用Fusion風格，跨平台一致性更好
    
    # 檢查並創建setup.json
    settings_path = check_create_setup_json()
    
    # 載入設定
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    
        # 設定應用程式資訊
        window_title = settings.get("window_title", "多平台影片下載器")
        app.setApplicationName(window_title)
        app.setApplicationVersion("1.73")  # 更新版本號
        app.setOrganizationName("Video Downloader")
    
        # 設置應用字體
        font_size = settings.get("font_size", 11)
        font = QFont()
        font.setPointSize(font_size)
        app.setFont(font)
    
        log(f"啟動{window_title} V1.73 - 支援YouTube、TikTok、Facebook等多個平台")
        log(f"已從 {settings_path} 載入設定")
    except Exception as e:
        log(f"讀取設定檔失敗: {str(e)}")
        # 使用預設設定
        app.setApplicationName("多平台影片下載器")
        app.setApplicationVersion("1.73")
        app.setOrganizationName("Video Downloader")
        
        font = QFont()
        font.setPointSize(11)
        app.setFont(font)
        
        log("啟動多平台影片下載器 V1.73 - 支援YouTube、TikTok、Facebook等多個平台")
    
    window = MainWindow()
    window.show()
    
    log("程式初始化完成")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()