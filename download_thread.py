#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
下載線程模組
實現多線程下載功能
"""

import os
import re
import time
import yt_dlp
from PySide6.QtCore import QThread, Signal, QTimer, QMutex, QWaitCondition

from logger import logger
from utils import apply_ssl_fix, format_size, format_time, sanitize_filename
from platform_detector import identify_platform


class DownloadThread(QThread):
    """下載線程類"""
    
    # 信號定義
    progress = Signal(str, int, str, str)  # 訊息, 進度百分比, 速度, ETA
    finished = Signal(bool, str, str)      # 成功/失敗, 訊息, 檔案路徑
    platform_detected = Signal(str, str)   # 平台名稱, URL
    
    def __init__(self, url, output_path, format_option, resolution, prefix="", auto_merge=True):
        """初始化下載線程"""
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_option = format_option
        self.resolution = resolution
        self.prefix = prefix if prefix else ""
        self.auto_merge = auto_merge
        
        # 控制狀態
        self.is_cancelled = False
        self.is_paused = False
        self.pause_condition = QWaitCondition()
        self.pause_mutex = QMutex()
        
        # 重試機制
        self.retry_count = 0
        self.max_retries = 3
        
        # 進度監控
        self.last_progress_time = time.time()
        self.progress_timeout = 30  # 進度超時時間（秒）
        self.download_speed_history = []
        
        # 平台資訊
        self.platform_info = None
        
        # 監控卡住狀況
        self.stall_check_timer = QTimer()
        self.stall_check_timer.timeout.connect(self.check_download_stall)
        self.stall_check_timer.start(5000)  # 每5秒檢查一次
    
    def run(self):
        """執行下載任務"""
        try:
            # 記錄開始時間
            self.start_time = time.time()
            self.last_progress_time = time.time()
            self.progress.emit("正在獲取影片資訊...", 0, "--", "--")
            
            # 檢查前綴長度限制
            if len(self.prefix) > 15:
                self.prefix = self.prefix[:15]
                logger.warning(f"前綴過長，已截斷為: {self.prefix}")
            
            # 套用SSL修復
            apply_ssl_fix()
            
            # 識別平台
            self.platform_info = identify_platform(self.url)
            platform_name = self.platform_info["name"]
            
            # 發送平台識別信號
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self.platform_detected.emit(platform_name, self.url))

            # 檢查是否需要登入
            if self.platform_info.get('needs_login', False):
                error_msg = f"⚠️ {platform_name}平台需要登入才能下載\n\n目前支援的免登入平台：\n✅ YouTube\n✅ Bilibili\n✅ TikTok\n\n需要登入的平台：\n❌ 抖音、Instagram、Facebook、Threads\n\n建議：請使用支援的平台或其他專用下載工具"
                logger.warning(f"{platform_name}平台需要登入，已提示用戶")
                QTimer.singleShot(0, lambda: self.finished.emit(False, error_msg, ""))
                return
            logger.info(f"識別到平台: {platform_name}, URL: {self.url}")
            
            # 檢查是否為未知平台
            if platform_name == "未知":
                raise Exception("無法辨識或不支援此平台，請確認URL格式是否正確")
            
            # 獲取下載選項
            ydl_opts = self.get_ydl_options()
            
            # 開始下載
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 獲取影片資訊
                self.progress.emit(f"正在獲取{platform_name}影片資訊...", 0, "--", "--")
                info = ydl.extract_info(self.url, download=False)
                
                if info is None:
                    raise Exception(f"無法獲取{platform_name}影片資訊，可能是無效連結或該影片已被移除")
                
                # 獲取影片標題
                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"開始下載: {title}", 0, "--", "--")
                
                # 檢查是否需要暫停
                self.check_pause()
                
                # 檢查是否已取消
                if self.is_cancelled:
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: self.finished.emit(False, "下載已取消", ""))
                    return
                
                # 執行下載
                ydl.download([self.url])
                
                # 等待下載完成並查找檔案
                time.sleep(1)  # 等待檔案系統同步

                # 查找下載的檔案
                found_file = self.find_downloaded_file(title)

                if found_file and os.path.exists(found_file):
                    logger.info(f"下載成功完成: {found_file}")
                    self.finished.emit(True, f"下載完成: {title}", found_file)
                    return
                else:
                    # 如果沒有找到檔案，但下載完成了，嘗試查找任何新檔案
                    logger.info("下載完成但未找到預期檔案，搜索下載目錄...")
                    import glob
                    pattern = os.path.join(self.output_path, f"{prefix}*")
                    files = glob.glob(pattern)
                    if files:
                        # 找到最新的檔案
                        latest_file = max(files, key=os.path.getctime)
                        logger.info(f"找到下載檔案: {latest_file}")
                        self.finished.emit(True, f"下載完成: {os.path.basename(latest_file)}", latest_file)
                        return
                    else:
                        # 如果找不到檔案，嘗試備用方法
                        logger.warning("未找到任何下載檔案")
                        success = self.fallback_download_method()
                        if not success:
                            # 列出目錄內容以便調試
                            try:
                                current_files = os.listdir(self.output_path)
                                logger.error(f"下載後目錄內容: {current_files}")
                            except:
                                pass
                            raise Exception("無法找到下載的檔案，下載可能已失敗")
                
        except Exception as e:
            error_message = str(e)
            logger.error(f"下載失敗: {error_message}")

            # 檢查是否為年齡驗證問題
            if any(keyword in error_message.lower() for keyword in [
                'sign in to confirm', 'age', 'verify', 'login', 'account',
                'restricted', 'unavailable', 'private', 'age-restricted'
            ]):
                # 嘗試使用替代方法
                logger.info("檢測到年齡驗證問題，嘗試替代方法...")
                try:
                    success = self.try_age_restricted_download()
                    if success:
                        return
                except Exception as age_error:
                    logger.error(f"替代方法也失敗: {str(age_error)}")
                    error_message += f"\n\n🔞 此影片需要年齡驗證\n\n💡 建議解決方案：\n1. 使用瀏覽器登入YouTube後下載\n2. 使用線上下載工具（如 y2mate.com）\n3. 尋找相同內容但無年齡限制的影片"
            
            # 檢查是否為取消操作
            if self.is_cancelled:
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self.finished.emit(False, "下載已取消", ""))
                return
            
            # 檢查是否需要重試
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                self.progress.emit(f"第 {self.retry_count} 次重試，使用備用方法...", 0, "--", "--")
                
                try:
                    # 等待一段時間再重試，避免立即重試造成的問題
                    time.sleep(2)
                    
                    # 檢查是否在等待期間被取消
                    if self.is_cancelled:
                        from PySide6.QtCore import QTimer
                        QTimer.singleShot(0, lambda: self.finished.emit(False, "下載已取消", ""))
                        return
                    
                    success = self.fallback_download_method()
                    if success:
                        return
                except Exception as fallback_error:
                    logger.error(f"備用方法也失敗: {str(fallback_error)}")
                    error_message += f"\n\n備用方法也失敗: {str(fallback_error)}"
                    
                    # 如果重試次數達到上限，嘗試分段下載
                    if self.retry_count >= self.max_retries:
                        self.progress.emit("嘗試分段下載方法...", 0, "--", "--")
                        try:
                            # 再次等待並檢查取消狀態
                            time.sleep(1)
                            if self.is_cancelled:
                                from PySide6.QtCore import QTimer
                                QTimer.singleShot(0, lambda: self.finished.emit(False, "下載已取消", ""))
                                return
                                
                            success = self.try_segment_download()
                            if success:
                                return
                        except Exception as segment_error:
                            logger.error(f"分段下載也失敗: {str(segment_error)}")
                            error_message += f"\n\n分段下載也失敗: {str(segment_error)}"
            
            # 所有方法都失敗，發送失敗信號
            logger.error(f"所有下載方法都失敗: {error_message}")
            self.finished.emit(False, error_message, "")
            
        finally:
            # 確保清理資源
            try:
                if self.stall_check_timer.isActive():
                    self.stall_check_timer.stop()
            except Exception:
                pass  # 忽略計時器停止錯誤
    
    def get_ydl_options(self):
        """獲取下載選項，根據重試次數調整設定"""
        # 確保前綴不為None
        prefix = self.prefix if self.prefix else ""
        
        # 基本下載選項
        ydl_opts = {
            'outtmpl': os.path.join(self.output_path, f'{prefix}%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 30 + (self.retry_count * 10),  # 逐漸增加超時時間
            'retries': 5 + (self.retry_count * 3),
            'fragment_retries': 5 + (self.retry_count * 3),
            # 年齡驗證處理
            'age_limit': None,
            'skip_unavailable_fragments': True,
            # 嘗試繞過某些限制
            'extractor_args': {
                'youtube': {
                    'skip': ['dash'] if 'youtube' in self.url.lower() else [],
                    'player_skip': ['configs'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '300',
                'Connection': 'keep-alive',
            }
        }
        
        # 根據平台特定的設定
        format_str = 'bestvideo+bestaudio/best'  # 預設格式
        
        # 使用平台特定的格式設定
        if self.platform_info and isinstance(self.platform_info, dict) and self.platform_info.get("name") != "未知":
            platform_options = self.platform_info.get("download_options", {})
            if "format" in platform_options:
                format_str = platform_options["format"]
        
        # 修復格式選擇，確保高畫質下載
        if "僅音訊" in self.format_option and "MP3" in self.format_option:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif "僅影片" in self.format_option:
            ydl_opts['format'] = 'bestvideo/best'
        else:
            # 根據解析度選擇格式
            if "4K" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]/best'
            elif "1080P" in self.resolution or "1080p" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
            elif "720P" in self.resolution or "720p" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
            elif "480P" in self.resolution or "480p" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
            elif "360P" in self.resolution or "360p" in self.resolution:
                ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]/best'
            elif "最高品質" in self.format_option:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                # 預設使用720P品質
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'

            # 重試時降低品質
            if self.retry_count > 0:
                ydl_opts['format'] = 'best[height<=720]/best'
            if self.retry_count > 1:
                ydl_opts['format'] = 'best[height<=480]/best'
        
        # 是否自動合併（僅對複合格式有效）
        if not self.auto_merge and '+' in ydl_opts['format']:
            ydl_opts['format'] = ydl_opts['format'].replace('+', '/')
            
        return ydl_opts

    def find_downloaded_file(self, title):
        """查找下載的檔案"""
        try:
            if not os.path.exists(self.output_path):
                return None

            safe_title = sanitize_filename(title)
            prefix = self.prefix if self.prefix else ""

            # 獲取目錄中的所有檔案
            all_files = os.listdir(self.output_path)

            # 過濾出媒體檔案
            media_extensions = ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv', '.mp3', '.m4a', '.wav', '.aac']
            media_files = [f for f in all_files if any(f.lower().endswith(ext) for ext in media_extensions)]

            if not media_files:
                return None

            # 方法1: 精確匹配前綴+標題
            expected_filename = f"{prefix}{safe_title}"
            for file in media_files:
                if file.startswith(expected_filename):
                    return os.path.join(self.output_path, file)

            # 方法2: 匹配前綴
            if prefix:
                for file in media_files:
                    if file.startswith(prefix):
                        return os.path.join(self.output_path, file)

            # 方法3: 模糊匹配標題
            title_words = safe_title.lower().split()[:3]  # 取前3個詞
            for file in media_files:
                file_lower = file.lower()
                if all(word in file_lower for word in title_words if len(word) > 2):
                    return os.path.join(self.output_path, file)

            # 方法4: 按時間排序，取最新的檔案
            if media_files:
                media_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.output_path, x)), reverse=True)
                return os.path.join(self.output_path, media_files[0])

            return None

        except Exception as e:
            logger.error(f"查找下載檔案時出錯: {str(e)}")
            return None

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
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.progress.emit("使用備用方法獲取影片資訊...", 0, "--", "--")
                info = ydl.extract_info(self.url, download=False)
                
                if info is None:
                    self.progress.emit(f"備用方法失敗: 無法獲取影片資訊", 0, "--", "--")
                    return False
                
                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"開始備用下載: {title}", 0, "--", "--")
                
                if not self.is_cancelled:
                    ydl.download([self.url])
                    
                    # 構建下載的檔案路徑
                    file_ext = info.get('ext', 'mp4')
                    if "僅音訊" in self.format_option and "MP3" in self.format_option:
                        file_ext = 'mp3'
                        
                    safe_title = sanitize_filename(title)
                    file_path = os.path.join(self.output_path, f'{self.prefix}{safe_title}.{file_ext}')
                    
                    if os.path.exists(file_path):
                        logger.info(f"備用下載成功: {file_path}")
                        self.finished.emit(True, f"備用下載完成: {title}", file_path)
                        return True
                    else:
                        # 查找可能的檔案
                        files = os.listdir(self.output_path)
                        for file in files:
                            if file.startswith(f"{self.prefix}{safe_title}"):
                                file_path = os.path.join(self.output_path, file)
                                logger.info(f"備用下載成功: {file_path}")
                                self.finished.emit(True, f"備用下載完成: {title}", file_path)
                                return True
                        
                        return False
            
            return False
        except Exception as e:
            self.progress.emit(f"備用下載方法失敗: {str(e)}", 0, "--", "--")
            return False
            
    def try_segment_download(self):
        """嘗試分段下載方法，用於處理卡住的下載"""
        try:
            self.progress.emit(f"正在嘗試分段下載...", 0, "--", "--")
            
            # 分段下載選項
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
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.progress.emit("使用分段下載獲取影片資訊...", 0, "--", "--")
                info = ydl.extract_info(self.url, download=False)
                
                if info is None:
                    self.progress.emit(f"分段下載失敗: 無法獲取影片資訊", 0, "--", "--")
                    return False
                
                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"開始分段下載: {title}", 0, "--", "--")
                
                if not self.is_cancelled:
                    ydl.download([self.url])
                    
                    # 構建下載的檔案路徑
                    file_ext = info.get('ext', 'mp4')
                    if "僅音訊" in self.format_option and "MP3" in self.format_option:
                        file_ext = 'mp3'
                        
                    safe_title = sanitize_filename(title)
                    file_path = os.path.join(self.output_path, f'{self.prefix}{safe_title}.{file_ext}')
                    
                    if os.path.exists(file_path):
                        from PySide6.QtCore import QTimer
                        QTimer.singleShot(0, lambda: self.finished.emit(True, f"分段下載完成: {title}", file_path))
                        return True
                    else:
                        # 查找可能的檔案
                        files = os.listdir(self.output_path)
                        for file in files:
                            if file.startswith(f"{self.prefix}{safe_title}"):
                                file_path = os.path.join(self.output_path, file)
                                from PySide6.QtCore import QTimer
                                QTimer.singleShot(0, lambda: self.finished.emit(True, f"分段下載完成: {title}", file_path))
                                return True
                        
                        return False
                        
            return False
        except Exception as e:
            self.progress.emit(f"分段下載失敗: {str(e)}", 0, "--", "--")
            return False
    
    def progress_hook(self, d):
        """下載進度回調"""
        try:
            # 檢查是否暫停，如果是則等待
            self.check_pause()

            # 更新最後進度時間
            self.last_progress_time = time.time()

            if self.is_cancelled:
                raise Exception("下載已取消")

            if d['status'] == 'downloading':
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
                    if speed:
                        speed_str = format_size(speed) + "/s"
                        # 記錄下載速度歷史
                        self.download_speed_history.append(speed)
                        # 只保留最近10個速度記錄
                        if len(self.download_speed_history) > 10:
                            self.download_speed_history.pop(0)
                    else:
                        speed_str = "-- KB/s"

                    # 剩餘時間
                    eta = d.get('eta', 0)
                    if eta:
                        eta_str = format_time(eta)
                    else:
                        eta_str = "--:--"

                    # 直接發送進度信號，不使用QTimer
                    self.progress.emit(f"下載中: {percent}%", percent, speed_str, eta_str)

                except Exception as e:
                    logger.error(f"處理進度時錯誤: {str(e)}")
                    self.progress.emit("處理進度時出錯", 0, "--", "--")

            elif d['status'] == 'finished':
                # 下載完成，可能需要後處理
                self.progress.emit("下載完成，正在處理...", 100, "--", "--")

            elif d['status'] == 'error':
                # 下載錯誤
                error_msg = d.get('error', '未知錯誤')
                self.progress.emit(f"下載錯誤: {error_msg}", 0, "--", "--")

        except Exception as e:
            logger.error(f"進度回調處理錯誤: {str(e)}")
            # 不要在這裡拋出異常，避免中斷下載流程
    
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
        # 如果已經重試次數達到上限，則放棄
        if self.retry_count >= self.max_retries:
            self.progress.emit("下載多次卡住，無法恢復", 0, "--", "--")
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self.finished.emit(False, "下載卡住，請手動重試", ""))
            return
            
        # 增加重試次數
        self.retry_count += 1
        self.progress.emit(f"自動重試下載 (第 {self.retry_count} 次)...", 0, "--", "--")
        
        # 重置進度時間
        self.last_progress_time = time.time()
        
        # 清空速度歷史
        self.download_speed_history = []
        
        # 根據重試次數選擇不同的下載方法
        try:
            # 第一次重試：使用備用下載方法
            if self.retry_count == 1:
                self.progress.emit("嘗試備用下載方法...", 0, "--", "--")
                success = self.fallback_download_method()
                if success:
                    return
            
            # 第二次重試：嘗試分段下載
            elif self.retry_count == 2:
                self.progress.emit("嘗試分段下載方法...", 0, "--", "--")
                success = self.try_segment_download()
                if success:
                    return
            
            # 第三次重試：使用最低品質設定
            elif self.retry_count == 3:
                self.progress.emit("嘗試使用最低品質下載...", 0, "--", "--")
                # 修改下載選項為最低品質
                self.format_option = "預設品質"
                self.resolution = "360P"
                success = self.fallback_download_method()
                if success:
                    return
            
            # 所有方法都失敗
            self.progress.emit("所有自動重試方法都失敗了", 0, "--", "--")
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self.finished.emit(False, "下載卡住，所有自動重試方法都失敗了", ""))

        except Exception as e:
            logger.error(f"自動重試失敗: {str(e)}")
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self.finished.emit(False, f"自動重試失敗: {str(e)}", ""))

    def try_age_restricted_download(self):
        """嘗試下載年齡限制影片的替代方法"""
        try:
            logger.info("嘗試年齡限制影片的替代下載方法...")

            # 方法1：使用不同的extractor參數
            prefix = self.prefix if self.prefix else ""
            alt_opts = {
                'outtmpl': os.path.join(self.output_path, f'{prefix}%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 60,
                'retries': 10,
                'fragment_retries': 10,
                # 特殊設定用於年齡限制影片
                'age_limit': 99,
                'skip_unavailable_fragments': True,
                'extractor_args': {
                    'youtube': {
                        'skip': ['hls', 'dash'],
                        'player_skip': ['js', 'configs'],
                        'include_live_dash': False,
                    }
                },
                'format': 'worst[ext=mp4]/worst',  # 使用較低品質嘗試
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Accept': '*/*',
                }
            }

            import yt_dlp
            with yt_dlp.YoutubeDL(alt_opts) as ydl:
                self.progress.emit("嘗試替代方法下載年齡限制影片...", 0, "--", "--")

                # 嘗試獲取資訊
                info = ydl.extract_info(self.url, download=False)
                if info is None:
                    return False

                title = info.get('title', 'Unknown Video')
                self.progress.emit(f"使用替代方法下載: {title}", 0, "--", "--")

                # 執行下載
                ydl.download([self.url])

                # 查找下載的檔案
                found_file = self.find_downloaded_file(title)
                if found_file and os.path.exists(found_file):
                    logger.info(f"替代方法下載成功: {found_file}")
                    self.finished.emit(True, f"替代方法下載完成: {title}", found_file)
                    return True

            return False

        except Exception as e:
            logger.error(f"替代下載方法失敗: {str(e)}")
            return False