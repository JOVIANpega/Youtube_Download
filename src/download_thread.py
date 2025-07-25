#!/usr/bin/env python3
"""
YouTube 下載器 - 下載線程模組
"""

import os
import time
import re
import yt_dlp
from PySide6.QtCore import QThread, Signal, QTimer, QMutex, QWaitCondition

from src.utils import log, apply_ssl_fix, format_size, format_time, sanitize_filename, identify_platform

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
        # 使用簡單的方式替代 QWaitCondition 和 QMutex
        # self.pause_condition = QWaitCondition()
        # self.pause_mutex = QMutex()
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
            self.platform_info = identify_platform(self.url)
            platform_name = self.platform_info["name"]
            
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
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # 獲取影片信息
                    self.progress.emit(f"正在獲取{platform_name}影片資訊...", 0, "--", "--")
                    info = ydl.extract_info(self.url, download=False)
                    
                    if info is None:
                        raise Exception(f"無法獲取{platform_name}影片資訊，可能是無效連結或該影片已被移除")
                    
                    # 獲取影片標題
                    title = info.get('title', 'Unknown Video')
                    self.progress.emit(f"開始下載 {platform_name} 影片: {title}", 0, "--", "--")
                    
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
                    
                    # 使用前綴+標題作為檔案名
                    safe_title = sanitize_filename(title)
                    if self.prefix:
                        filename = f"{self.prefix}{safe_title}.{file_ext}"
                    else:
                        filename = f"{safe_title}.{file_ext}"
                    
                    file_path = os.path.join(self.output_path, filename)
                    
                    # 檢查檔案是否存在
                    if os.path.exists(file_path):
                        self.finished.emit(True, "下載完成", file_path)
                    else:
                        # 嘗試尋找類似名稱的檔案
                        files = os.listdir(self.output_path)
                        found = False
                        for file in files:
                            if safe_title in file and file.endswith(f".{file_ext}"):
                                file_path = os.path.join(self.output_path, file)
                                self.finished.emit(True, "下載完成", file_path)
                                found = True
                                break
                        
                        if not found:
                            # 如果找不到檔案，嘗試備用下載方法
                            self.fallback_download_method()
            except Exception as e:
                self.last_error = str(e)
                log(f"下載失敗: {self.last_error}")
                
                # 檢查是否為Twitter保護推文錯誤
                error_lower = self.last_error.lower()
                if platform_name in ["X", "Twitter"] and ("protected tweet" in error_lower or "not authorized" in error_lower or "account credentials" in error_lower):
                    # 直接返回特殊錯誤訊息，不嘗試備用方法
                    special_error = f"YT_DLP_FAILURE:{platform_name}:{self.last_error}"
                    log(f"檢測到Twitter保護推文錯誤，返回特殊錯誤訊息: {special_error}")
                    self.finished.emit(False, special_error, "")
                    return
                
                # 處理特定平台的錯誤
                platform_name = self.platform_info["name"] if self.platform_info else "未知"
                error_message = self.get_platform_specific_error_message(platform_name, self.last_error)
                
                # 檢查是否為yt-dlp執行失敗，如果是則直接返回錯誤
                if error_message.startswith("YT_DLP_FAILURE:"):
                    self.finished.emit(False, error_message, "")
                    return
                
                # 檢查是否需要登入
                if self.platform_info["needs_login"] and ("需要登入" in self.last_error or "login" in self.last_error.lower()):
                    self.finished.emit(False, f"下載失敗: 此{platform_name}內容需要登入，請在設定中提供cookies.txt檔案", "")
                    return
                
                # 嘗試備用下載方法
                if self.retry_count < self.max_retries:
                    self.retry_count += 1
                    log(f"嘗試備用下載方法 (嘗試 {self.retry_count}/{self.max_retries})...")
                    self.fallback_download_method()
                else:
                    self.finished.emit(False, error_message, "")
        except Exception as e:
            log(f"下載線程發生異常: {str(e)}")
            self.finished.emit(False, f"下載失敗: {str(e)}", "")
    
    def get_ydl_options(self):
        """獲取yt-dlp下載選項"""
        # 根據選擇的格式設定下載選項
        format_str = "bestvideo+bestaudio/best"  # 預設格式
        
        # 如果平台信息已獲取，使用平台特定的格式設定
        if self.platform_info and self.platform_info["name"] != "未知":
            # 使用平台特定的下載選項
            platform_options = self.platform_info["download_options"]
            if "format" in platform_options:
                format_str = platform_options["format"]
        
        # 根據用戶選擇的格式和解析度覆蓋平台特定設定
        if "僅影片" in self.format_option:
            if self.resolution == "最高畫質":
                format_str = "bestvideo"
            else:
                # 解析度限制
                res_match = re.search(r'(\d+)p', self.resolution)
                if res_match:
                    max_height = res_match.group(1)
                    format_str = f"bestvideo[height<={max_height}]"
        elif "僅音訊 (MP3)" in self.format_option:
            format_str = "bestaudio/best"
        else:  # 影片+音訊
            if self.resolution == "最高畫質":
                format_str = "bestvideo+bestaudio/best"
            else:
                # 解析度限制
                res_match = re.search(r'(\d+)p', self.resolution)
                if res_match:
                    max_height = res_match.group(1)
                    # 對於720p或更高解析度，使用更精確的格式選擇
                    if int(max_height) >= 720:
                        format_str = f"bestvideo[height<={max_height}]+bestaudio/best"
                    else:
                        format_str = f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]"
        
        # 構建輸出模板
        if self.prefix:
            outtmpl = os.path.join(self.output_path, f"{self.prefix}%(title)s.%(ext)s")
        else:
            outtmpl = os.path.join(self.output_path, "%(title)s.%(ext)s")
        
        # 基本下載選項
        ydl_opts = {
            'format': format_str,
            'outtmpl': outtmpl,
            'progress_hooks': [self.progress_hook],
            'ignoreerrors': True,
            'no_warnings': False,
            'quiet': False,
            'verbose': False,
            'nocheckcertificate': True,  # 忽略SSL證書驗證
        }
        
        # 如果是特定平台，使用平台特定的格式設定
        if self.platform_info and self.platform_info["name"] in ["TikTok", "抖音", "X", "Twitter", "Facebook", "Instagram", "Bilibili"]:
            ydl_opts.update({
                'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                'no_playlist': True,
                'restrict_filenames': True,
            })
        
        # 如果是音訊格式，添加轉換為MP3的選項
        if "僅音訊 (MP3)" in self.format_option:
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        
        # 檢查是否需要合併影片和音訊
        need_merge = False
        
        # 對於高畫質影片，始終合併音訊和影片，無論auto_merge設定如何
        if "僅影片" not in self.format_option and "僅音訊" not in self.format_option:
            # 檢查是否為高畫質影片 (720p或以上)
            res_match = re.search(r'(\d+)p', self.resolution)
            if res_match and int(res_match.group(1)) >= 720:
                need_merge = True
            elif self.resolution == "最高畫質":
                need_merge = True
            elif self.auto_merge:
                need_merge = True
        
        # 如果需要合併影片和音訊，添加合併選項
        if need_merge:
            ydl_opts.update({
                'merge_output_format': 'mp4',
            })
        
        # 從設定檔案中讀取cookies設定
        try:
            import json
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_preferences.json")
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                    # 檢查是否需要使用 cookies 檔案
                    try:
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
        except Exception as e:
            log(f"讀取設定檔案失敗: {str(e)}")
        
        return ydl_opts
    
    def fallback_download_method(self):
        """備用下載方法，當標準下載失敗時嘗試"""
        try:
            log("嘗試備用下載方法...")
            self.progress.emit("嘗試備用下載方法...", 0, "--", "--")
            
            # 修改下載選項，使用更簡單的格式選擇
            if "僅音訊" in self.format_option:
                format_str = "bestaudio"
            elif "僅影片" in self.format_option:
                format_str = "bestvideo"
            else:
                format_str = "best"  # 使用單一最佳格式
            
            # 構建輸出模板
            if self.prefix:
                outtmpl = os.path.join(self.output_path, f"{self.prefix}%(title)s.%(ext)s")
            else:
                outtmpl = os.path.join(self.output_path, "%(title)s.%(ext)s")
            
            # 備用下載選項
            ydl_opts = {
                'format': format_str,
                'outtmpl': outtmpl,
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True,
                'no_warnings': True,
                'quiet': False,
                'verbose': False,
                'nocheckcertificate': True,
            }
            
            # 如果是音訊格式，添加轉換為MP3的選項
            if "僅音訊 (MP3)" in self.format_option:
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            
            # 對於高畫質影片，添加合併選項
            need_merge = False
            
            # 檢查是否需要合併影片和音訊
            if "僅影片" not in self.format_option and "僅音訊" not in self.format_option:
                # 檢查是否為高畫質影片 (720p或以上)
                res_match = re.search(r'(\d+)p', self.resolution)
                if res_match and int(res_match.group(1)) >= 720:
                    need_merge = True
                elif self.resolution == "最高畫質":
                    need_merge = True
                elif self.auto_merge:
                    need_merge = True
            
            # 如果需要合併，添加合併選項
            if need_merge:
                ydl_opts.update({
                    'merge_output_format': 'mp4',
                })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 獲取影片信息
                info = ydl.extract_info(self.url, download=False)
                
                if info is None:
                    raise Exception("無法獲取影片資訊，可能是無效連結或該影片已被移除")
                
                # 獲取影片標題
                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"備用方法下載: {title}", 0, "--", "--")
                
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
                
                # 使用前綴+標題作為檔案名
                safe_title = sanitize_filename(title)
                if self.prefix:
                    filename = f"{self.prefix}{safe_title}.{file_ext}"
                else:
                    filename = f"{safe_title}.{file_ext}"
                
                file_path = os.path.join(self.output_path, filename)
                
                # 檢查檔案是否存在
                if os.path.exists(file_path):
                    self.finished.emit(True, "下載完成", file_path)
                else:
                    # 嘗試尋找類似名稱的檔案
                    files = os.listdir(self.output_path)
                    found = False
                    for file in files:
                        if safe_title in file and file.endswith(f".{file_ext}"):
                            file_path = os.path.join(self.output_path, file)
                            self.finished.emit(True, "下載完成", file_path)
                            found = True
                            break
                    
                    if not found:
                        # 如果找不到檔案，嘗試分段下載
                        self.try_segment_download()
        except Exception as e:
            self.last_error = str(e)
            log(f"備用下載方法失敗: {self.last_error}")
            
            # 檢查是否為Twitter保護推文錯誤
            platform_name = self.platform_info["name"] if self.platform_info else "未知"
            error_lower = self.last_error.lower()
            if platform_name in ["X", "Twitter"] and ("protected tweet" in error_lower or "not authorized" in error_lower or "account credentials" in error_lower):
                # 直接返回特殊錯誤訊息，不嘗試其他方法
                special_error = f"YT_DLP_FAILURE:{platform_name}:{self.last_error}"
                log(f"備用方法檢測到Twitter保護推文錯誤，返回特殊錯誤訊息: {special_error}")
                self.finished.emit(False, special_error, "")
                return
            
            # 處理特定平台的錯誤
            error_message = self.get_platform_specific_error_message(platform_name, self.last_error)
            
            # 檢查是否為yt-dlp執行失敗，如果是則直接返回錯誤
            if error_message.startswith("YT_DLP_FAILURE:"):
                self.finished.emit(False, error_message, "")
                return
            
            # 如果備用方法也失敗，嘗試分段下載
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                log(f"嘗試分段下載 (嘗試 {self.retry_count}/{self.max_retries})...")
                self.try_segment_download()
            else:
                self.finished.emit(False, f"備用方法也失敗: {error_message}", "")
    
    def try_segment_download(self):
        """嘗試分段下載，當其他方法都失敗時使用"""
        try:
            log("嘗試分段下載...")
            self.progress.emit("嘗試分段下載...", 0, "--", "--")
            
            # 修改下載選項，使用分段下載
            format_str = "best"  # 使用單一最佳格式
            
            # 構建輸出模板
            if self.prefix:
                outtmpl = os.path.join(self.output_path, f"{self.prefix}%(title)s.%(ext)s")
            else:
                outtmpl = os.path.join(self.output_path, "%(title)s.%(ext)s")
            
            # 分段下載選項
            ydl_opts = {
                'format': format_str,
                'outtmpl': outtmpl,
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True,
                'no_warnings': True,
                'quiet': False,
                'verbose': False,
                'nocheckcertificate': True,
                'fragment_retries': 10,  # 分段重試次數
                'retries': 10,  # 連接重試次數
                'skip_unavailable_fragments': True,  # 跳過不可用的分段
            }
            
            # 如果是音訊格式，添加轉換為MP3的選項
            if "僅音訊 (MP3)" in self.format_option:
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            
            # 對於高畫質影片，添加合併選項
            need_merge = False
            
            # 檢查是否需要合併影片和音訊
            if "僅影片" not in self.format_option and "僅音訊" not in self.format_option:
                # 檢查是否為高畫質影片 (720p或以上)
                res_match = re.search(r'(\d+)p', self.resolution)
                if res_match and int(res_match.group(1)) >= 720:
                    need_merge = True
                elif self.resolution == "最高畫質":
                    need_merge = True
                elif self.auto_merge:
                    need_merge = True
            
            # 如果需要合併，添加合併選項
            if need_merge:
                ydl_opts.update({
                    'merge_output_format': 'mp4',
                })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 獲取影片信息
                info = ydl.extract_info(self.url, download=False)
                
                if info is None:
                    raise Exception("無法獲取影片資訊，可能是無效連結或該影片已被移除")
                
                # 獲取影片標題
                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"分段下載: {title}", 0, "--", "--")
                
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
                
                # 使用前綴+標題作為檔案名
                safe_title = sanitize_filename(title)
                if self.prefix:
                    filename = f"{self.prefix}{safe_title}.{file_ext}"
                else:
                    filename = f"{safe_title}.{file_ext}"
                
                file_path = os.path.join(self.output_path, filename)
                
                # 檢查檔案是否存在
                if os.path.exists(file_path):
                    self.finished.emit(True, "下載完成", file_path)
                    return True
                else:
                    # 嘗試尋找類似名稱的檔案
                    files = os.listdir(self.output_path)
                    found = False
                    for file in files:
                        if safe_title in file and file.endswith(f".{file_ext}"):
                            file_path = os.path.join(self.output_path, file)
                            self.finished.emit(True, "下載完成", file_path)
                            found = True
                            return True
                    
                    if not found:
                        self.finished.emit(False, "下載失敗：無法找到下載的檔案", "")
                        return False
        except Exception as e:
            self.progress.emit(f"分段下載失敗: {str(e)}", 0, "--", "--")
            
            # 檢查是否為Twitter保護推文錯誤
            platform_name = self.platform_info["name"] if self.platform_info else "未知"
            error_str = str(e)
            error_lower = error_str.lower()
            if platform_name in ["X", "Twitter"] and ("protected tweet" in error_lower or "not authorized" in error_lower or "account credentials" in error_lower):
                # 直接返回特殊錯誤訊息
                special_error = f"YT_DLP_FAILURE:{platform_name}:{error_str}"
                log(f"分段下載檢測到Twitter保護推文錯誤，返回特殊錯誤訊息: {special_error}")
                self.finished.emit(False, special_error, "")
                return False
            
            # 處理特定平台的錯誤
            error_message = self.get_platform_specific_error_message(platform_name, error_str)
            
            # 檢查是否為yt-dlp執行失敗，如果是則直接返回錯誤
            if error_message.startswith("YT_DLP_FAILURE:"):
                self.finished.emit(False, error_message, "")
                return False
            
            self.finished.emit(False, f"下載失敗: {error_message}", "")
            return False
    
    def progress_hook(self, d):
        """下載進度回調函數 - 優化版"""
        try:
            # 更新最後進度時間
            self.last_progress_time = time.time()
            
            if d['status'] == 'downloading':
                # 獲取下載進度
                try:
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes', 0)
                    
                    if total is None or total == 0:
                        total = d.get('total_bytes_estimate', 0)
                    
                    if total > 0:
                        percent = int(downloaded / total * 100)
                        # 避免太頻繁更新，只在進度變化時發送信號
                        if abs(percent - self.last_progress) >= 1 or time.time() - self.last_progress_time > 1.0:
                            # 獲取下載速度
                            speed = d.get('speed', 0)
                            if speed:
                                speed_str = format_size(speed) + "/s"
                                
                                # 記錄下載速度歷史
                                self.download_speed_history.append(speed)
                                if len(self.download_speed_history) > 5:  # 減少歷史記錄數量
                                    self.download_speed_history.pop(0)
                            else:
                                speed_str = "--"
                            
                            # 獲取剩餘時間
                            eta = d.get('eta', None)
                            if eta is not None:
                                eta_str = format_time(eta)
                            else:
                                eta_str = "--"
                            
                            # 獲取檔案名稱
                            filename = d.get('filename', '')
                            if filename:
                                filename = os.path.basename(filename)
                            else:
                                filename = "未知檔案"
                            
                            # 發送進度信號
                            self.progress.emit(f"下載中: {filename}", percent, speed_str, eta_str)
                            self.last_progress = percent
                    else:
                        # 沒有總大小信息時，每秒最多更新一次
                        if time.time() - self.last_progress_time > 1.0:
                            self.progress.emit("下載中...", 0, "--", "--")
                except Exception as e:
                    # 只在較長時間間隔記錄錯誤，避免日誌爆炸
                    if time.time() - self.last_progress_time > 5.0:
                        log(f"處理下載進度時發生錯誤: {str(e)}")
                    # 發送進度信號，但不包含可能導致錯誤的值
                    self.progress.emit("下載中...", 0, "--", "--")
            
            elif d['status'] == 'finished':
                # 下載完成
                filename = d.get('filename', '')
                if filename:
                    filename = os.path.basename(filename)
                else:
                    filename = "未知檔案"
                
                # 設置一個下載完成標記，防止重複處理
                if not hasattr(self, '_download_finished') or not self._download_finished:
                    self._download_finished = True
                    self.progress.emit(f"處理中: {filename}", 100, "--", "--")
                
            elif d['status'] == 'error':
                # 下載錯誤
                self.progress.emit("下載錯誤", 0, "--", "--")
        except Exception as e:
            # 只在較長時間間隔記錄錯誤，避免日誌爆炸
            if time.time() - self.last_progress_time > 5.0:
                log(f"進度回調函數發生錯誤: {str(e)}")
    
    def cancel(self):
        """取消下載"""
        self.is_cancelled = True
        self.resume()  # 如果正在暫停，先恢復以便能夠正確取消
    
    def pause(self):
        """暫停下載"""
        self.is_paused = True
    
    def resume(self):
        """繼續下載"""
        self.is_paused = False
    
    def check_pause(self):
        """檢查是否需要暫停"""
        if self.is_paused:
            # 使用簡單的方式替代 QWaitCondition 和 QMutex
            # self.pause_condition.wait(self.pause_mutex)
            pass
    
    def check_download_stall(self):
        """檢查下載是否卡住"""
        current_time = time.time()
        if current_time - self.last_progress_time > self.progress_timeout:
            # 下載卡住了
            log(f"下載似乎卡住了 {self.progress_timeout} 秒沒有進度更新")
            self.handle_stalled_download()
    
    def handle_stalled_download(self):
        """處理卡住的下載"""
        # 檢查下載速度歷史
        if self.download_speed_history:
            avg_speed = sum(self.download_speed_history) / len(self.download_speed_history)
            if avg_speed < 1024:  # 平均速度小於1KB/s
                log("下載速度過慢，可能是網絡問題")
                
                # 如果下載速度過慢且已經重試次數未達上限，則重試
                if self.retry_count < self.max_retries:
                    self.retry_count += 1
                    log(f"嘗試重新下載 (嘗試 {self.retry_count}/{self.max_retries})...")
                    
                    # 重置進度時間，避免重複觸發
                    self.last_progress_time = time.time()
                    
                    # 在主線程中重新啟動下載
                    self.progress.emit("重新啟動下載...", 0, "--", "--")
                    
                    # 由於我們在QThread中，不能直接重啟下載
                    # 發送信號給主線程，讓主線程重新啟動下載
                    self.finished.emit(False, "下載卡住，需要重試", "RETRY")
                    return
        
        # 如果沒有重試或重試次數已達上限，則繼續等待
        log("下載似乎卡住了，但仍在等待...")
        
        # 重置進度時間，給予更多時間
        self.last_progress_time = time.time()
    
    def get_platform_specific_error_message(self, platform_name, error):
        """根據平台和錯誤類型生成特定的錯誤訊息"""
        error_lower = error.lower()
        
        # 檢測是否為yt-dlp執行失敗
        yt_dlp_failure_keywords = [
            "unsupported url", "no video formats found", "video unavailable",
            "private video", "deleted video", "not found", "does not exist",
            "access denied", "forbidden", "403", "404", "not authorized",
            "protected", "restricted", "age restricted", "sign in required",
            "login required", "authentication required", "rate limit",
            "too many requests", "blocked", "geoblocked", "region restricted",
            "protected tweet", "you are not authorized", "account credentials",
            "postprocessing", "codec", "invalid argument", "requested format is not available"
        ]
        
        # 特別針對X/Twitter平台的錯誤關鍵詞
        twitter_specific_keywords = [
            "protected tweet", "you are not authorized", "account credentials",
            "twitter", "provide account credentials"
        ]
        
        # 特別針對Instagram平台的錯誤關鍵詞
        instagram_specific_keywords = [
            "requested format is not available", "postprocessing", "codec", 
            "invalid argument", "could not write header", "instagram",
            "login required", "sign in required", "authentication required",
            "private account", "private profile", "private post"
        ]
        
        # 特別針對TikTok平台的錯誤關鍵詞
        tiktok_specific_keywords = [
            "tiktok", "douyin", "captcha", "verification", "rate limit",
            "too many requests", "region", "blocked", "unavailable in your region"
        ]
        
        # 特別針對Facebook平台的錯誤關鍵詞
        facebook_specific_keywords = [
            "facebook", "fb.com", "login", "authentication", "private content",
            "content not available", "cookies required", "session"
        ]
        
        # 特別針對Bilibili平台的錯誤關鍵詞
        bilibili_specific_keywords = [
            "bilibili", "b23.tv", "需要登入", "大會員", "vip", "premium content",
            "地區限制", "region restricted"
        ]
        
        # 特別針對Threads平台的錯誤關鍵詞
        threads_specific_keywords = [
            "threads", "threads.net", "meta", "private", "login required"
        ]
        
        # 檢查是否為X/Twitter平台的特定錯誤
        if platform_name in ["X", "Twitter"] and any(keyword in error_lower for keyword in twitter_specific_keywords):
            return f"YT_DLP_FAILURE:{platform_name}:{error}"
        
        # 檢查是否為Instagram平台的特定錯誤
        if platform_name == "Instagram" and any(keyword in error_lower for keyword in instagram_specific_keywords):
            return f"YT_DLP_FAILURE:{platform_name}:{error}"
        
        # 檢查是否為TikTok平台的特定錯誤
        if platform_name in ["TikTok", "抖音"] and any(keyword in error_lower for keyword in tiktok_specific_keywords):
            return f"YT_DLP_FAILURE:{platform_name}:{error}"
        
        # 檢查是否為Facebook平台的特定錯誤
        if platform_name == "Facebook" and any(keyword in error_lower for keyword in facebook_specific_keywords):
            return f"YT_DLP_FAILURE:{platform_name}:{error}"
        
        # 檢查是否為Bilibili平台的特定錯誤
        if platform_name == "Bilibili" and any(keyword in error_lower for keyword in bilibili_specific_keywords):
            return f"YT_DLP_FAILURE:{platform_name}:{error}"
        
        # 檢查是否為Threads平台的特定錯誤
        if platform_name == "Threads" and any(keyword in error_lower for keyword in threads_specific_keywords):
            return f"YT_DLP_FAILURE:{platform_name}:{error}"
        
        # 檢查一般yt-dlp失敗關鍵詞
        is_yt_dlp_failure = any(keyword in error_lower for keyword in yt_dlp_failure_keywords)
        
        # 如果是yt-dlp失敗，返回特殊錯誤訊息
        if is_yt_dlp_failure:
            return f"YT_DLP_FAILURE:{platform_name}:{error}"
        
        # 所有錯誤都使用YT_DLP_FAILURE前綴，確保顯示外部下載按鈕
        return f"YT_DLP_FAILURE:{platform_name}:{error}" 