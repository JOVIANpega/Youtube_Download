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
import ssl
import re
import subprocess
import traceback
import urllib.request
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget,
                               QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTextEdit, QLineEdit, QProgressBar, QCheckBox,
                               QComboBox, QFileDialog, QGroupBox, QSplitter,
                               QListWidget, QGridLayout, QRadioButton,
                               QButtonGroup, QToolBar, QStatusBar, QScrollArea, QFrame, QMessageBox, QSpinBox, QDialog, QDialogButtonBox)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QTimer, QThread, QSettings
from PySide6.QtGui import QIcon, QAction, QFont, QPixmap
import yt_dlp
import json
import datetime

# 設置日誌函數
def log(message):
    """輸出日誌"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # 保存到日誌檔案
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"downloader_{datetime.datetime.now().strftime('%Y-%m-%d')}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    except Exception as e:
        print(f"無法寫入日誌檔案: {str(e)}")

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

# SSL修復函數
def apply_ssl_fix():
    """應用SSL修復（V1.55特色功能）"""
    log("自動套用SSL證書修復...")
    try:
        # 模擬SSL設定
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl._create_default_https_context = lambda: ssl_context
        log("SSL證書驗證已停用，這可以解決某些SSL錯誤")
        return True
    except Exception as e:
        log(f"SSL修復遇到問題: {e}")
        return False

# 應用SSL修復
apply_ssl_fix()

class DownloadThread(QThread):
    """下載線程類"""
    progress = Signal(str, int, str, str)  # 訊息, 進度百分比, 速度, ETA
    finished = Signal(bool, str, str)  # 成功/失敗, 訊息, 檔案路徑
    
    def __init__(self, url, output_path, format_option, resolution, prefix, auto_merge):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_option = format_option
        self.resolution = resolution
        self.prefix = prefix
        self.auto_merge = auto_merge
        self.is_cancelled = False
        self.retry_count = 0
        self.max_retries = 3
        self.last_error = None
        self.last_error_traceback = None
    
    def run(self):
        while self.retry_count <= self.max_retries and not self.is_cancelled:
            try:
                self.progress.emit(f"正在獲取影片資訊... (嘗試 {self.retry_count + 1}/{self.max_retries + 1})", 0, "--", "--")
                
                # 設定下載選項
                ydl_opts = self.get_ydl_options()
                
                # 下載嘗試 1：正常下載
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        self.progress.emit("獲取影片資訊...", 0, "--", "--")
                        info = ydl.extract_info(self.url, download=False)
                        
                        if info is None:
                            raise Exception("無法獲取影片資訊，可能是無效連結或該影片已被移除")
                        
                        title = info.get('title', 'Unknown Video')
                        self.progress.emit(f"開始下載: {title}", 0, "--", "--")
                        
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
                            
                            self.finished.emit(True, f"下載完成: {title}", file_path)
                            return  # 成功完成
                except yt_dlp.utils.DownloadError as e:
                    # 保存錯誤信息
                    self.last_error = str(e)
                    self.last_error_traceback = traceback.format_exc()
                    
                    if "age-restricted" in str(e).lower() or "sign in" in str(e).lower():
                        self.progress.emit(f"年齡限制影片，需要登入：{str(e)}", 0, "--", "--")
                        # 不重試年齡限制的影片
                        self.finished.emit(False, f"下載失敗: 年齡限制影片，需要登入", "")
                        return
                    elif "unavailable" in str(e).lower() or "not available" in str(e).lower():
                        self.progress.emit(f"影片不可用：{str(e)}", 0, "--", "--")
                        # 不重試不可用的影片
                        self.finished.emit(False, f"下載失敗: 影片不可用", "")
                        return
                    else:
                        self.progress.emit(f"標準下載失敗 (嘗試 {self.retry_count + 1})：{str(e)}", 0, "--", "--")
                        # 嘗試備用下載方法
                        try:
                            self.progress.emit(f"嘗試備用下載方法...", 0, "--", "--")
                            success = self.fallback_download_method()
                            if success:
                                return  # 成功完成
                        except Exception as fallback_e:
                            self.last_error = str(fallback_e)
                            self.last_error_traceback = traceback.format_exc()
                            self.progress.emit(f"備用下載方法失敗：{str(fallback_e)}", 0, "--", "--")
                            raise fallback_e
                
                # 如果還沒有成功，但尚未達到最大重試次數，則繼續
                self.retry_count += 1
                if self.is_cancelled:
                    self.progress.emit("下載已取消", 0, "--", "--")
                    self.finished.emit(False, "下載已取消", "")
                    return
            
            except Exception as e:
                # 保存錯誤信息
                self.last_error = str(e)
                self.last_error_traceback = traceback.format_exc()
                
                # 紀錄錯誤
                error_msg = str(e)
                self.progress.emit(f"錯誤 (嘗試 {self.retry_count + 1})：{error_msg}", 0, "--", "--")
                
                # 增加重試計數
                self.retry_count += 1
                
                # 檢查是否需要繼續重試
                if self.retry_count > self.max_retries or self.is_cancelled:
                    break
                
                # 短暫暫停後重試
                self.progress.emit(f"將在 3 秒後重試...", 0, "--", "--")
                time.sleep(3)
        
        # 如果所有嘗試都失敗
        if self.retry_count > self.max_retries and not self.is_cancelled:
            error_message = "下載失敗：已達最大重試次數"
            if self.last_error:
                error_message += f"\n最後錯誤: {self.last_error}"
            
            self.progress.emit(f"已達最大重試次數 ({self.max_retries + 1})，下載失敗", 0, "--", "--")
            self.finished.emit(False, error_message, "")
    
    def get_ydl_options(self):
        """獲取下載選項，根據重試次數調整設定"""
        ydl_opts = {
            'outtmpl': os.path.join(self.output_path, f'{self.prefix}%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'socket_timeout': 30 + (self.retry_count * 10),  # 逐漸增加超時時間
            'retries': 5 + (self.retry_count * 3),  # 逐漸增加重試次數
            'fragment_retries': 5 + (self.retry_count * 3),
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }
        
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
                'format': 'worst',  # 使用最差品質，通常更穩定
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 60,
                'retries': 10,
                'fragment_retries': 10,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.progress.emit("使用備用方法獲取影片資訊...", 0, "--", "--")
                info = ydl.extract_info(self.url, download=False)
                
                if info is None:
                    self.progress.emit("備用方法：無法獲取影片資訊", 0, "--", "--")
                    return False
                
                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"備用方法開始下載: {title}", 0, "--", "--")
                
                if not self.is_cancelled:
                    ydl.download([self.url])
                    
                    # 構建下載的檔案路徑
                    file_ext = info.get('ext', 'mp4')
                    safe_title = self.sanitize_filename(title)
                    file_path = os.path.join(self.output_path, f'{self.prefix}{safe_title}.{file_ext}')
                    
                    self.finished.emit(True, f"備用方法下載完成: {title}", file_path)
                    return True
            
        except Exception as e:
            self.progress.emit(f"備用方法下載失敗：{str(e)}", 0, "--", "--")
            return False
            
        return False
    
    def progress_hook(self, d):
        """下載進度回調"""
        if self.is_cancelled:
            raise Exception("下載已取消")
            
        if d['status'] == 'downloading':
            # 計算進度百分比
            if 'total_bytes' in d and d['total_bytes']:
                percent = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                percent = int((d['downloaded_bytes'] / d['total_bytes_estimate']) * 100)
            else:
                percent = 0
                
            # 計算下載速度
            speed = d.get('speed', 0)
            if speed:
                speed_str = f"{speed / 1024 / 1024:.1f} MB/s"
            else:
                speed_str = "--"
                
            # 計算剩餘時間
            eta = d.get('eta', None)
            if eta:
                eta_str = f"{eta // 60:02d}:{eta % 60:02d}"
            else:
                eta_str = "--:--"
                
            self.progress.emit(f"下載中... {percent}%", percent, speed_str, eta_str)
            
        elif d['status'] == 'finished':
            self.progress.emit("下載完成，正在處理...", 100, "--", "--")
    
        elif d['status'] == 'merging':
            # 處理合併進度
            if 'merged_bytes' in d and 'total_bytes' in d and d['total_bytes']:
                percent = int((d['merged_bytes'] / d['total_bytes']) * 100)
                self.progress.emit(f"正在合併檔案... {percent}%", percent, "--", "--")
            else:
                self.progress.emit("正在合併檔案...", 90, "--", "--")  # 預設顯示90%進度
                
        elif d['status'] == 'postprocessing':
            # 處理後處理進度
            if '_percent' in d:
                percent = int(float(d['_percent']))
                self.progress.emit(f"正在處理檔案... {percent}%", percent, "--", "--")
            else:
                self.progress.emit("正在處理檔案...", 95, "--", "--")  # 預設顯示95%進度
    
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

class DownloadTab(QWidget):
    """下載頁籤"""
    
    def __init__(self, parent=None, download_path=None):
        """初始化"""
        super().__init__(parent)
        self.download_path = download_path or os.path.expanduser("~/Downloads")
        self.download_items = {}
        self.download_threads = {}  # 添加下載線程字典
        self.max_concurrent_downloads = 2  # 預設最大同時下載數
        self.prefix_history = ["Per Nice-", "Per Best3-", "Per Best2-", "Per Best-", "Per-"]  # 預設前綴選項
        self.load_settings()  # 載入設定
        self.init_ui()
    
    def load_settings(self):
        """載入設定"""
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_preferences.json")
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
                        
                    log("已載入用戶設定")
        except Exception as e:
            log(f"載入設定失敗: {str(e)}")
    
    def save_settings(self):
        """保存設定"""
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_preferences.json")
            
            # 讀取現有設定（如果存在）
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    try:
                        settings = json.load(f)
                    except:
                        settings = {}
            
            # 更新設定
            settings["max_concurrent_downloads"] = self.max_concurrent_downloads
            settings["prefix_history"] = self.prefix_history
            settings["download_path"] = self.download_path
            
            # 保存設定
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            log("已保存用戶設定")
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
        input_group = QGroupBox("輸入YouTube連結")
        input_layout = QVBoxLayout(input_group)
        
        # URL輸入框 - 根據最大同時下載數動態調整高度
        url_layout = QVBoxLayout()
        url_label = QLabel(f"YouTube連結 (每行一個，最多同時下載 {self.max_concurrent_downloads} 個):")
        self.url_edit = QTextEdit()
        self.url_edit.setPlaceholderText("在這裡貼上一個或多個YouTube視頻連結，每行一個")
        
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
        
        input_layout.addLayout(url_layout)
        input_layout.addWidget(self.title_label)
        
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
        
        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_combo)
        prefix_layout.addWidget(self.clear_prefix_btn)
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
        self.auto_merge_cb = QCheckBox("自動合併音頻和視頻")
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
        
        self.pause_all_btn = QPushButton("暫停所有")
        self.pause_all_btn.setStyleSheet(button_style.replace("background-color: #0078d7", "background-color: #f0ad4e"))
        self.pause_all_btn.clicked.connect(self.pause_all)
        
        self.delete_btn = QPushButton("刪除選取")
        self.delete_btn.setStyleSheet(button_style.replace("background-color: #0078d7", "background-color: #d9534f"))
        self.delete_btn.clicked.connect(self.delete_selected)
        
        # 新增：跳過錯誤任務按鈕
        self.skip_error_btn = QPushButton("跳過錯誤任務")
        self.skip_error_btn.setStyleSheet(button_style.replace("background-color: #0078d7", "background-color: #5cb85c"))
        self.skip_error_btn.clicked.connect(self.skip_error_tasks)
        
        control_layout.addWidget(self.download_btn)
        control_layout.addWidget(self.pause_all_btn)
        control_layout.addWidget(self.delete_btn)
        control_layout.addWidget(self.skip_error_btn)
        control_layout.addStretch(1)
        
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
        
        # 總進度部分移至右下角
        total_progress_layout = QHBoxLayout()
        total_progress_layout.addStretch(1)
        
        total_progress_container = QWidget()
        total_progress_box = QHBoxLayout(total_progress_container)
        total_progress_box.setContentsMargins(0, 0, 0, 0)
        
        total_label = QLabel("總進度:")
        self.total_progress = QProgressBar()
        self.total_progress.setMinimum(0)
        self.total_progress.setMaximum(100)
        self.total_progress.setValue(0)
        self.total_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 5px;
            }
        """)
        
        total_progress_box.addWidget(total_label)
        total_progress_box.addWidget(self.total_progress)
        
        total_progress_layout.addWidget(total_progress_container)
        progress_layout.addLayout(total_progress_layout)
        
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
            if "YouTube連結" in widget.text():
                widget.setText(f"YouTube連結 (每行一個，最多同時下載 {value} 個):")
                break
        
        # 保存設定
        self.save_settings()

    def on_prefix_changed(self, text):
        """前綴變更時處理"""
        if not text or text in self.prefix_history:
            return
            
        # 將新前綴添加到歷史記錄
        self.prefix_history.insert(0, text)
        
        # 限制歷史記錄長度
        if len(self.prefix_history) > 10:
            self.prefix_history = self.prefix_history[:10]
            
        # 更新下拉選單
        current_text = text
        self.prefix_combo.clear()
        self.prefix_combo.addItems(self.prefix_history)
        self.prefix_combo.setCurrentText(current_text)
        
        # 保存設定
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
        
        # YouTube 圖示
        icon_label = QLabel("▶")
        icon_label.setStyleSheet("color: #ff0000; font-size: 14pt; font-weight: bold;")
        info_layout.addWidget(icon_label)
        
        # 將顯示名稱從預設檔名改為原影片標題
        title_label = QLabel(filename)
        title_label.setStyleSheet("font-weight: bold; color: #0066cc; font-size: 10pt;")
        info_layout.addWidget(title_label)
        
        info_layout.addStretch(1)
        
        # 狀態信息
        status_label = QLabel(status)
        status_label.setStyleSheet("color: #666666;")
        info_layout.addWidget(status_label)
        
        item_layout.addLayout(info_layout)
        
        # 進度條和控制區域
        progress_layout = QHBoxLayout()
        
        # 進度條 - 修改文字顯示方式，確保不被遮擋
        progress_bar = QProgressBar()
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
        eta_label.setStyleSheet("color: #666666; padding-left: 10px;")
        speed_label = QLabel(f"{speed}")
        speed_label.setStyleSheet("color: #666666;")
        
        info_box.addWidget(speed_label)
        info_box.addWidget(eta_label)
        
        progress_layout.addWidget(info_widget, 1)  # 信息佔據較少空間
        
        # 控制按鈕
        control_widget = QWidget()
        control_box = QHBoxLayout(control_widget)
        control_box.setContentsMargins(0, 0, 0, 0)
        
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
        
        # 新增：重試按鈕
        retry_btn = QPushButton("重試")
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
        
        delete_btn = QPushButton("❌")
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
        
        control_box.addWidget(pause_btn)
        control_box.addWidget(retry_btn)
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
        # 獲取所有URL
        urls_text = self.url_edit.toPlainText().strip()
        if not urls_text:
            QMessageBox.warning(self, "錯誤", "請輸入至少一個YouTube連結!")
            return
        
        # 分割多行URL
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            QMessageBox.warning(self, "錯誤", "沒有找到有效的YouTube連結!")
            return
        
        # 驗證所有URL
        invalid_urls = []
        for url in urls:
            if not url.startswith(("http://", "https://")) or "youtube.com" not in url and "youtu.be" not in url:
                invalid_urls.append(url)
        
        if invalid_urls:
            QMessageBox.warning(self, "錯誤", f"發現 {len(invalid_urls)} 個無效連結!\n首個無效連結: {invalid_urls[0]}")
            return
        
        # 檢查下載路徑
        output_path = self.path_edit.text()
        if not output_path or not os.path.exists(output_path):
            QMessageBox.warning(self, "錯誤", "請選擇有效的下載路徑!")
            return
        
        # 獲取設定
        format_option = self.format_combo.currentText()
        resolution = self.resolution_combo.currentText()
        prefix = self.prefix_combo.currentText()
        auto_merge = self.auto_merge_cb.isChecked()
        
        log(f"開始下載 {len(urls)} 個影片...")
        log(f"格式選項: {format_option}")
        log(f"解析度: {resolution}")
        log(f"檔案前綴: {prefix}")
        log(f"自動合併: {'是' if auto_merge else '否'}")
        log(f"下載路徑: {output_path}")
        
        # 應用SSL修復
        log("自動套用SSL證書修復...")
        apply_ssl_fix()
        
        # 套用檔名前綴
        log(f"應用檔案名稱前綴: {prefix}")
        
        # 為每個URL創建下載任務
        for i, url in enumerate(urls):
            try:
                # 創建假的進度項目
                filename = f"YouTube影片_{i+1}.mp4"
                self.create_download_item(self.download_layout, filename, 0, "--:--", "--", "準備下載...")
                
                # 儲存下載參數到項目
                self.download_items[filename]['url'] = url
                self.download_items[filename]['output_path'] = output_path
                self.download_items[filename]['format_option'] = format_option
                self.download_items[filename]['resolution'] = resolution
                self.download_items[filename]['prefix'] = prefix
                self.download_items[filename]['auto_merge'] = auto_merge
                
                # 開始下載
                self.start_download_for_item(filename, url)
                
            except Exception as e:
                error_msg = f"處理URL時發生錯誤: {str(e)}"
                log(error_msg)
                QMessageBox.warning(self, "警告", f"處理URL '{url}' 時出錯: {str(e)}")
        
        # 清空輸入框，方便下一次輸入
        self.url_edit.clear()

    def start_download_for_item(self, filename, url):
        """為單個項目開始下載"""
        try:
            # 獲取下載參數
            output_path = self.download_items[filename]['output_path']
            format_option = self.download_items[filename]['format_option']
            resolution = self.download_items[filename]['resolution']
            prefix = self.download_items[filename]['prefix']
            auto_merge = self.download_items[filename]['auto_merge']
            
            # 建立下載線程
            download_thread = DownloadThread(url, output_path, format_option, resolution, prefix, auto_merge)
            
            # 連接信號
            download_thread.progress.connect(
                lambda msg, percent, speed, eta: self.update_download_progress(filename, msg, percent, speed, eta)
            )
            download_thread.finished.connect(
                lambda success, msg, file_path: self.download_finished(filename, success, msg, file_path)
            )
            
            # 儲存線程引用到兩個字典中
            self.download_items[filename]['thread'] = download_thread
            self.download_threads[filename] = download_thread
            download_thread.start()
            
        except Exception as e:
            self.update_download_progress(filename, f"啟動下載失敗: {str(e)}", 0, "--", "--")
            log(f"啟動下載線程失敗: {str(e)}")

    def update_video_info(self, message, url):
        """更新視頻信息"""
        try:
            # 如果訊息中包含影片標題信息
            if "開始下載:" in message and ":" in message:
                title = message.split(":", 1)[1].strip()
                
                # 更新對應下載項目的標題
                for filename, item in self.download_items.items():
                    if item.get('url') == url:
                        item['title_label'].setText(title)
                        break
            elif "Error" in message or "錯誤" in message or "失敗" in message:
                # 處理錯誤情況
                for filename, item in self.download_items.items():
                    if item.get('url') == url:
                        item['status_label'].setText(message)
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
            self.download_items[filename]['progress_bar'].setValue(percent)
            
            # 更新狀態文字
            self.download_items[filename]['status_label'].setText(message)
            
            # 更新下載速度和剩餘時間
            self.download_items[filename]['speed_label'].setText(f"速度: {speed}")
            self.download_items[filename]['eta_label'].setText(f"ETA: {eta}")
            
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
                log(f"下載進度 [{filename}]: {percent}%, 速度: {speed}, ETA: {eta}")

    def download_finished(self, filename, success, message, file_path):
        """下載完成回調"""
        # 檢查項目是否存在
        if filename in self.download_items:
            item_data = self.download_items[filename]
            
            if success:
                # 設置為綠色完成狀態
                item_data["status_label"].setText("下載完成")
                item_data["status_label"].setStyleSheet("color: green; font-weight: bold;")
                item_data["progress_bar"].setValue(100)
                item_data["progress_bar"].setStyleSheet(
                    "QProgressBar::chunk { background-color: #4CAF50; }"
                )
                
                # 更新按鈕狀態
                item_data["pause_btn"].setEnabled(False)
                item_data["delete_btn"].setText("刪除")
                
                # 顯示完成對話框
                self.show_download_complete_dialog(filename, file_path)
            else:
                # 設置為紅色錯誤狀態
                item_data["status_label"].setText("下載失敗")
                item_data["status_label"].setStyleSheet("color: red; font-weight: bold;")
                item_data["progress_bar"].setStyleSheet(
                    "QProgressBar::chunk { background-color: #f44336; }"
                )
                
                # 更新按鈕狀態
                item_data["pause_btn"].setEnabled(False)
                item_data["delete_btn"].setText("刪除")
                
                # 顯示錯誤對話框
                self.show_error_dialog(filename, message)
        
            # 清理下載線程
            if filename in self.download_threads:
                self.download_threads[filename].deleteLater()
                del self.download_threads[filename]
        
        # 更新總進度
        self.update_total_progress()

    def update_total_progress(self):
        """更新總進度信息"""
        # 計算完成的下載數量
        total_items = len(self.download_items) + 1  # +1 因為已完成的不在列表中
        completed_items = 0
        
        # 查找所有進度條
        progress_bars = self.findChildren(QProgressBar)
        for progress_bar in progress_bars:
            if progress_bar.value() == 100:
                completed_items += 1
        
        # 更新總進度標籤
        total_label = self.findChild(QLabel, "total_progress_label")
        if total_label:
            if total_items == completed_items:
                total_label.setText(f"總進度：{completed_items}/{total_items} 完成")
            else:
                total_label.setText(f"總進度：{completed_items}/{total_items} 完成 | 總剩餘時間：約 {(total_items-completed_items) * 2} 分鐘")

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

    def update_resolution_availability(self):
        """更新解析度可用性（模擬根據影片實際可用解析度）"""
        current_resolution = self.resolution_combo.currentText()
        log(f"已選擇解析度: {current_resolution}")

    def pause_all(self):
        """暫停所有下載任務"""
        log("暫停所有下載任務")
        
        # 暫停所有正在運行的下載線程
        for filename, item in list(self.download_items.items()):
            if 'thread' in item and item['thread'].isRunning():
                item['thread'].cancel()
                log(f"已暫停下載: {filename}")
                
                # 更新UI
                status_label = self.findChild(QLabel, f"status_label_{filename}")
                if status_label:
                    status_label.setText("已暫停")
        
        # 獲取所有暫停按鈕
        pause_buttons = self.findChildren(QPushButton)
        for button in pause_buttons:
            if button.objectName().startswith("pause_btn_") and button.text() == "暫停":
                filename = button.objectName().replace("pause_btn_", "")
                log(f"更新按鈕狀態: {filename}")
                self.toggle_pause_item(filename)

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
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("下載完成")
        msg_box.setText(f"'{filename}'下載完成！")
        
        # 添加圖標
        msg_box.setIconPixmap(QPixmap("icons/success.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # 添加按鈕
        open_button = msg_box.addButton("打開檔案", QMessageBox.AcceptRole)
        open_folder_button = msg_box.addButton("打開資料夾", QMessageBox.ActionRole)
        close_button = msg_box.addButton("關閉", QMessageBox.RejectRole)
        
        msg_box.exec()
        
        # 處理按鈕點擊
        clicked_button = msg_box.clickedButton()
        if clicked_button == open_button and os.path.exists(file_path):
            # 打開檔案
            os.startfile(file_path)
        elif clicked_button == open_folder_button and os.path.exists(os.path.dirname(file_path)):
            # 打開檔案所在資料夾
            os.startfile(os.path.dirname(file_path))

    def show_error_dialog(self, filename, error_message):
        """顯示錯誤詳情對話框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("下載錯誤")
        dialog.setMinimumWidth(500)
        
        # 獲取對應的URL
        url_input = self.findChild(QLineEdit, f"url_input_{filename}")
        url = url_input.text() if url_input else "未知URL"
        
        # 獲取當前下載設定
        format_option = self.download_formats.get(filename, "預設品質")
        resolution = self.download_resolutions.get(filename, "最高可用")
        output_path = self.path_input.text()
        
        # 主佈局
        layout = QVBoxLayout(dialog)
        
        # 標題和圖標
        title_layout = QHBoxLayout()
        error_icon = QLabel()
        error_icon.setPixmap(QPixmap("icons/error.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        error_icon.setMaximumWidth(48)
        title_layout.addWidget(error_icon)
        
        title_label = QLabel(f"<b>'{filename}'下載失敗</b>")
        title_label.setWordWrap(True)
        title_layout.addWidget(title_label, 1)
        layout.addLayout(title_layout)
        
        # 分割線
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 錯誤詳情
        error_group = QGroupBox("錯誤詳情")
        error_layout = QVBoxLayout(error_group)
        
        error_text = QTextEdit()
        error_text.setReadOnly(True)
        error_text.setPlainText(error_message)
        error_text.setMaximumHeight(150)
        error_layout.addWidget(error_text)
        
        layout.addWidget(error_group)
        
        # 可能的解決方法
        solutions_group = QGroupBox("可能的解決方法")
        solutions_layout = QVBoxLayout(solutions_group)
        
        # 根據錯誤類型添加不同的解決方案建議
        if "age-restricted" in error_message.lower() or "sign in" in error_message.lower():
            solutions_layout.addWidget(QLabel("• 此影片有年齡限制，需要登入才能觀看。"))
            solutions_layout.addWidget(QLabel("• 請嘗試登入 YouTube 或使用其他方法下載。"))
        elif "unavailable" in error_message.lower() or "not available" in error_message.lower():
            solutions_layout.addWidget(QLabel("• 該影片不可用或已被刪除。"))
            solutions_layout.addWidget(QLabel("• 請確認影片連結是否正確，或該影片是否仍可在 YouTube 上觀看。"))
        elif "error 429" in error_message.lower() or "too many requests" in error_message.lower():
            solutions_layout.addWidget(QLabel("• YouTube 伺服器拒絕請求，可能是因為請求過於頻繁。"))
            solutions_layout.addWidget(QLabel("• 請稍等一段時間再嘗試下載。"))
            solutions_layout.addWidget(QLabel("• 嘗試使用代理或 VPN 連接。"))
        elif "ssl" in error_message.lower() or "certificate" in error_message.lower():
            solutions_layout.addWidget(QLabel("• SSL 憑證驗證失敗。"))
            solutions_layout.addWidget(QLabel("• 嘗試更新程式或使用「忽略SSL驗證」選項（已自動啟用）。"))
        elif "ffmpeg" in error_message.lower():
            solutions_layout.addWidget(QLabel("• FFmpeg 相關錯誤，無法處理媒體檔案。"))
            solutions_layout.addWidget(QLabel("• 請確認 FFmpeg 是否正確安裝，或選擇不需要轉換的下載格式。"))
        elif "network" in error_message.lower() or "timeout" in error_message.lower() or "connection" in error_message.lower():
            solutions_layout.addWidget(QLabel("• 網路連接問題。"))
            solutions_layout.addWidget(QLabel("• 請檢查您的網路連接並重試。"))
            solutions_layout.addWidget(QLabel("• 嘗試選擇較低的解析度，可能更容易下載成功。"))
        else:
            solutions_layout.addWidget(QLabel("• 嘗試使用不同的格式或解析度選項。"))
            solutions_layout.addWidget(QLabel("• 檢查您的網路連接。"))
            solutions_layout.addWidget(QLabel("• 稍後再試。"))
            solutions_layout.addWidget(QLabel("• 確認影片連結是否正確且影片可用。"))
        
        layout.addWidget(solutions_group)
        
        # 操作按鈕
        button_layout = QHBoxLayout()
        retry_button = QPushButton("重試")
        retry_button.clicked.connect(lambda: self.retry_download(filename, dialog))
        
        change_format_button = QPushButton("變更格式選項")
        change_format_button.clicked.connect(lambda: self.show_format_options_dialog(filename, dialog))
        
        save_log_button = QPushButton("保存錯誤報告")
        save_log_button.clicked.connect(lambda: self.save_error_log(filename, error_message, url, format_option, resolution, output_path))
        
        close_button = QPushButton("關閉")
        close_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(retry_button)
        button_layout.addWidget(change_format_button)
        button_layout.addWidget(save_log_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()

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
                
                # 從已有項目重新開始下載
                self.start_download_for_item(filename, url)
        else:
            QMessageBox.warning(self, "錯誤", "找不到對應的下載項目")

    def show_format_options_dialog(self, filename, parent_dialog=None):
        """顯示格式選項對話框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("變更下載格式")
        dialog.setMinimumWidth(400)
        
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
        
        auto_merge_check = QCheckBox("自動合併影片和音訊")
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
        self.prefix_combo.setCurrentText("")
        # 如果需要，可以將空前綴添加到歷史記錄中
        if "" not in self.prefix_history:
            self.prefix_history.insert(0, "")
            self.prefix_combo.clear()
            self.prefix_combo.addItems(self.prefix_history)
            self.prefix_combo.setCurrentText("")
        
        log("已清空檔名前綴")
        
        # 保存設定
        self.save_settings()

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
            "命名與整理"
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
        }
        
        # 保存到用戶偏好文件
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_preferences.json")
            
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
    
    def load_settings_from_file(self):
        """從文件載入設定"""
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_preferences.json")
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
        
        self.auto_merge_cb = QCheckBox("自動合併影片與音訊")
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
        proxy_group = QGroupBox("代理設定")
        proxy_layout = QVBoxLayout(proxy_group)
        
        # 是否使用代理
        self.use_proxy_cb = QCheckBox("使用代理伺服器")
        self.use_proxy_cb.setChecked(False)
        proxy_layout.addWidget(self.use_proxy_cb)
        
        # 代理類型
        proxy_type_layout = QHBoxLayout()
        proxy_type_layout.addWidget(QLabel("代理類型:"))
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "SOCKS4", "SOCKS5"])
        proxy_type_layout.addWidget(self.proxy_type_combo)
        proxy_type_layout.addStretch(1)
        proxy_layout.addLayout(proxy_type_layout)
        
        # 代理位址
        proxy_address_layout = QHBoxLayout()
        proxy_address_layout.addWidget(QLabel("代理位址:"))
        self.proxy_address_input = QLineEdit()
        self.proxy_address_input.setPlaceholderText("例如: 127.0.0.1")
        proxy_address_layout.addWidget(self.proxy_address_input)
        proxy_layout.addLayout(proxy_address_layout)
        
        # 代理連接埠
        proxy_port_layout = QHBoxLayout()
        proxy_port_layout.addWidget(QLabel("連接埠:"))
        self.proxy_port_input = QLineEdit()
        self.proxy_port_input.setPlaceholderText("例如: 1080")
        proxy_port_layout.addWidget(self.proxy_port_input)
        proxy_port_layout.addStretch(1)
        proxy_layout.addLayout(proxy_port_layout)
        
        # 代理驗證
        auth_group = QGroupBox("代理驗證")
        auth_layout = QVBoxLayout(auth_group)
        
        self.use_auth_cb = QCheckBox("需要驗證")
        self.use_auth_cb.setChecked(False)
        auth_layout.addWidget(self.use_auth_cb)
        
        # 使用者名稱
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("使用者名稱:"))
        self.proxy_username_input = QLineEdit()
        username_layout.addWidget(self.proxy_username_input)
        auth_layout.addLayout(username_layout)
        
        # 密碼
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密碼:"))
        self.proxy_password_input = QLineEdit()
        self.proxy_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.proxy_password_input)
        auth_layout.addLayout(password_layout)
        
        proxy_layout.addWidget(auth_group)
        network_layout.addWidget(proxy_group)
        
        # 連接設定組
        connection_group = QGroupBox("連接設定")
        connection_layout = QVBoxLayout(connection_group)
        
        # 重試次數
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel("下載失敗重試次數:"))
        self.retry_spin = QSpinBox()
        self.retry_spin.setMinimum(0)
        self.retry_spin.setMaximum(10)
        self.retry_spin.setValue(3)
        retry_layout.addWidget(self.retry_spin)
        retry_layout.addStretch(1)
        connection_layout.addLayout(retry_layout)
        
        # 等待時間
        wait_layout = QHBoxLayout()
        wait_layout.addWidget(QLabel("重試間隔時間 (秒):"))
        self.wait_spin = QSpinBox()
        self.wait_spin.setMinimum(1)
        self.wait_spin.setMaximum(60)
        self.wait_spin.setValue(5)
        wait_layout.addWidget(self.wait_spin)
        wait_layout.addStretch(1)
        connection_layout.addLayout(wait_layout)
        
        # 超時時間
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("連接超時時間 (秒):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(10)
        self.timeout_spin.setMaximum(300)
        self.timeout_spin.setValue(60)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch(1)
        connection_layout.addLayout(timeout_layout)
        
        # SSL驗證
        self.disable_ssl_cb = QCheckBox("停用SSL證書驗證（解決某些SSL錯誤）")
        self.disable_ssl_cb.setChecked(True)
        connection_layout.addWidget(self.disable_ssl_cb)
        
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
        apply_btn.clicked.connect(self.apply_settings)
        cancel_btn.clicked.connect(self.cancel_changes)
        reset_btn.clicked.connect(self.reset_settings)
        
        return network_widget

    def create_performance_settings(self):
        """創建性能優化設定頁面"""
        performance_widget = QWidget()
        performance_layout = QVBoxLayout(performance_widget)
        
        # 執行緒設定組
        thread_group = QGroupBox("執行緒設定")
        thread_layout = QVBoxLayout(thread_group)
        
        # 執行緒數量
        thread_count_layout = QHBoxLayout()
        thread_count_layout.addWidget(QLabel("下載執行緒數量:"))
        self.thread_spin = QSpinBox()
        self.thread_spin.setMinimum(1)
        self.thread_spin.setMaximum(32)
        self.thread_spin.setValue(4)
        thread_count_layout.addWidget(self.thread_spin)
        thread_count_layout.addStretch(1)
        thread_layout.addLayout(thread_count_layout)
        
        # 分段下載
        self.segment_cb = QCheckBox("啟用分段下載 (更快但可能增加伺服器負載)")
        self.segment_cb.setChecked(True)
        thread_layout.addWidget(self.segment_cb)
        
        # 分段大小
        segment_size_layout = QHBoxLayout()
        segment_size_layout.addWidget(QLabel("分段大小 (MB):"))
        self.segment_spin = QSpinBox()
        self.segment_spin.setMinimum(1)
        self.segment_spin.setMaximum(100)
        self.segment_spin.setValue(10)
        segment_size_layout.addWidget(self.segment_spin)
        segment_size_layout.addStretch(1)
        thread_layout.addLayout(segment_size_layout)
        
        performance_layout.addWidget(thread_group)
        
        # 記憶體設定組
        memory_group = QGroupBox("記憶體設定")
        memory_layout = QVBoxLayout(memory_group)
        
        # 使用記憶體緩衝
        self.memory_buffer_cb = QCheckBox("使用記憶體緩衝區 (更快但消耗更多記憶體)")
        self.memory_buffer_cb.setChecked(True)
        memory_layout.addWidget(self.memory_buffer_cb)
        
        # 緩衝區大小
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
        
        # 連接信號
        apply_btn.clicked.connect(self.apply_settings)
        cancel_btn.clicked.connect(self.cancel_changes)
        reset_btn.clicked.connect(self.reset_settings)
        
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
        # 設定預設下載路徑
        self.download_path = os.path.expanduser("~/Downloads")
        self.init_ui()
    
    def init_ui(self):
        """初始化用戶界面"""
        self.setWindowTitle("YouTube下載器 V1.63")
        self.setGeometry(100, 100, 900, 700)
        
        # 創建主佈局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 創建標籤頁小部件
        self.tabs = QTabWidget()
        
        # 添加標籤頁
        self.download_tab = DownloadTab(download_path=self.download_path)
        self.settings_tab = SettingsTab()
        
        self.tabs.addTab(self.download_tab, "下載任務")
        self.tabs.addTab(self.settings_tab, "設定")
        
        # 連接設定頁面和下載頁面
        self.settings_tab.settings_applied.connect(self.on_settings_applied)
        
        # 載入初始設定
        self.settings_tab.load_settings_from_file()
        
        layout.addWidget(self.tabs)
        
        # 顯示主視窗
        self.show()
    
    def on_settings_applied(self, settings):
        """當設定被套用時"""
        log("設定已套用，正在更新下載頁面...")
        self.download_tab.apply_settings(settings)
        
        # 切換回下載頁面
        self.tabs.setCurrentIndex(0)

def main():
    """主函數"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用Fusion風格，跨平台一致性更好
    
    # 設定應用程式資訊
    app.setApplicationName("YouTube下載器")
    app.setApplicationVersion("1.63")
    app.setOrganizationName("YouTube Downloader")
    
    # 設置應用字體
    font = QFont()
    font.setPointSize(9)
    app.setFont(font)
    
    log("啟動YouTube下載器 V1.63 - 分頁式界面")
    
    window = MainWindow()
    window.show()
    
    log("程式初始化完成")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 