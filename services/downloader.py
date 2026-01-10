#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載器服務
yt-dlp 下載器（progress hook、狀態機、暫停/取消/重試）
"""

import os
import time
import threading
from enum import Enum
from typing import Dict, Any, Optional, Callable
try:
    import yt_dlp
except ImportError:
    print("警告: yt-dlp 未安裝，下載功能將不可用")
    print("請運行: pip install yt-dlp")
    yt_dlp = None
from utils.threading_utils import CancellationToken, ProgressReporter, OperationCancelledException
from utils.path_utils import get_safe_path, sanitize_filename, get_file_size_str
from utils.naming import FilenameManager
from services.ffmpeg_manager import FFmpegManager
from logging_config import get_logger

logger = get_logger(__name__)

class DownloadStatus(Enum):
    """下載狀態"""
    IDLE = "idle"
    EXTRACTING = "extracting"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DownloadTask:
    """下載任務"""
    
    def __init__(self, url: str, output_path: str, options: Dict[str, Any] = None):
        self.url = url
        self.output_path = output_path
        self.options = options or {}
        self.status = DownloadStatus.IDLE
        self.progress = 0.0
        self.speed = 0
        self.eta = 0
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.filename = ""
        self.title = ""
        self.video_id = ""
        self.error_message = ""
        self.start_time = None
        self.end_time = None
        
    def to_dict(self):
        """轉換為字典"""
        return {
            'url': self.url,
            'output_path': self.output_path,
            'status': self.status.value,
            'progress': self.progress,
            'speed': self.speed,
            'eta': self.eta,
            'downloaded_bytes': self.downloaded_bytes,
            'total_bytes': self.total_bytes,
            'filename': self.filename,
            'title': self.title,
            'video_id': self.video_id,
            'error_message': self.error_message,
            'start_time': self.start_time,
            'end_time': self.end_time,
        }

class VideoDownloader:
    """視頻下載器"""
    
    def __init__(self):
        self.ffmpeg_manager = FFmpegManager()
        self.current_task: Optional[DownloadTask] = None
        self.cancellation_token: Optional[CancellationToken] = None
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        self._lock = threading.Lock()
        
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """設置進度回調"""
        self.progress_callback = callback
        
    def set_status_callback(self, callback: Callable[[DownloadStatus, str], None]):
        """設置狀態回調"""
        self.status_callback = callback
        
    def _update_progress(self, progress: float, message: str = ""):
        """更新進度"""
        if self.progress_callback:
            try:
                self.progress_callback(progress, message)
            except Exception as e:
                # The provided snippet seems to be for a UI component, not this service.
                # Applying the logging part that is relevant to this service.
                err_msg = str(e)
                logger.error(f"進度回調錯誤: {err_msg}")
                
    def _update_status(self, status: DownloadStatus, message: str = ""):
        """更新狀態"""
        if self.current_task:
            self.current_task.status = status
            if message:
                self.current_task.error_message = message
                
        if self.status_callback:
            try:
                self.status_callback(status, message)
            except Exception as e:
                logger.error(f"狀態回調錯誤: {e}")
                
    def _progress_hook(self, d):
        """yt-dlp 進度鉤子"""
        if not self.current_task:
            return
            
        try:
            # 優先檢查是否已取消
            if self.cancellation_token and self.cancellation_token.is_cancelled():
                raise OperationCancelledException("操作已取消")

            if d['status'] == 'downloading':
                self.current_task.status = DownloadStatus.DOWNLOADING
                
                # 更新進度資訊
                if 'total_bytes' in d:
                    self.current_task.total_bytes = d['total_bytes']
                elif 'total_bytes_estimate' in d:
                    self.current_task.total_bytes = d['total_bytes_estimate']
                    
                if 'downloaded_bytes' in d:
                    self.current_task.downloaded_bytes = d['downloaded_bytes']
                    
                if self.current_task.total_bytes > 0:
                    self.current_task.progress = (self.current_task.downloaded_bytes / 
                                                self.current_task.total_bytes) * 100
                else:
                    # 如果總大小未知，設為 0 並在訊息中顯示已下載量
                    self.current_task.progress = 0.0
                    
                # 更新速度和 ETA
                if 'speed' in d and d['speed']:
                    self.current_task.speed = d['speed']
                    
                if 'eta' in d and d['eta']:
                    self.current_task.eta = d['eta']
                    
                # 判斷當前下載的部分
                filename = d.get('filename', '')
                ext = os.path.splitext(filename)[1].lower()
                part_msg = "下載音訊" if ext in ['.m4a', '.mp3', '.aac', '.opus'] else "下載影片"
                
                # 回調進度
                downloaded_str = get_file_size_str(self.current_task.downloaded_bytes)
                speed_str = f"{get_file_size_str(self.current_task.speed)}/s" if self.current_task.speed else ""
                eta_str = f"ETA: {self.current_task.eta}s" if self.current_task.eta else ""
                
                if self.current_task.total_bytes > 0:
                    message = f"[{part_msg}] {speed_str} {eta_str}".strip()
                else:
                    # 總大小未知時，在狀態欄顯示已下載多少
                    message = f"[{part_msg}] 已下載 {downloaded_str} | {speed_str}".strip()
                
                self._update_progress(self.current_task.progress, message)
                
            elif d['status'] == 'finished':
                # 如果還沒設過檔名或檔名包含 .part，更新它
                new_filename = os.path.basename(d.get('filename', ''))
                if new_filename and (not self.current_task.filename or '.part' in self.current_task.filename):
                    self.current_task.filename = new_filename
                self.current_task.progress = 100.0
                self._update_progress(100.0, "下載/合併完成")
                
            elif d['status'] == 'error':
                self._update_status(DownloadStatus.FAILED, str(d.get('error', '未知錯誤')))
                
        except Exception as e:
            logger.error(f"進度鉤子錯誤: {e}")
            
    def get_video_info(self, url: str, cancellation_token: CancellationToken = None) -> Dict[str, Any]:
        """獲取視頻資訊"""
        if yt_dlp is None:
            raise Exception("yt-dlp 未安裝，無法獲取視頻資訊")
            
        # 在開始前檢查取消
        if cancellation_token and cancellation_token.is_cancelled():
            raise OperationCancelledException("操作已取消")
            
        try:
            # 獲取資訊用的小選項
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'socket_timeout': 15, # 進一步縮短，避免長久卡轉
                'source_address': '0.0.0.0', # 強制使用 IPv4 增加連線速度
            }
            
            # 獲取資訊時也套用代理 (SettingsManager 取得全域設定)
            from services.settings import SettingsManager
            sm = SettingsManager()
            global_settings = sm.load_settings()
            proxy = global_settings.get('proxy', '').strip()
            if proxy:
                ydl_opts['proxy'] = proxy
            
            # 如果有提供 Token，也順便檢查一下
            if cancellation_token and cancellation_token.is_cancelled():
                raise OperationCancelledException("操作已取消")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 在 extract_info 之前再次檢查
                if cancellation_token and cancellation_token.is_cancelled():
                    raise OperationCancelledException("操作已取消")
                
                info = ydl.extract_info(url, download=False)
                
            return {
                'title': info.get('title', '未知標題'),
                'id': info.get('id', 'no_id'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', '未知上傳者'),
                'upload_date': info.get('upload_date', ''),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', ''),
                'thumbnail': info.get('thumbnail', ''),
                'formats': info.get('formats', []),
                'platform': info.get('extractor', ''),
            }
            
        except Exception as e:
            logger.error(f"獲取視頻資訊失敗: {e}")
            raise Exception(f"無法獲取視頻資訊: {str(e)}")
            
    def download(self, url: str, output_path: str, options: Dict[str, Any] = None,
                cancellation_token: CancellationToken = None,
                progress_reporter: ProgressReporter = None,
                logger: Any = None) -> str:
        """下載視頻"""
        
        if yt_dlp is None:
            raise Exception("yt-dlp 未安裝，無法下載視頻")
        
        with self._lock:
            if self.current_task and self.current_task.status == DownloadStatus.DOWNLOADING:
                raise Exception("已有下載任務正在進行")
                
        # 創建下載任務
        self.current_task = DownloadTask(url, output_path, options)
        self.cancellation_token = cancellation_token
        self.current_task.start_time = time.time()
        
        try:
            # 更新狀態
            self._update_status(DownloadStatus.EXTRACTING, "正在解析視頻資訊...")
            
            # 檢查取消
            if cancellation_token and cancellation_token.is_cancelled():
                raise OperationCancelledException("操作已取消")
                
            # 獲取視頻資訊 (傳入取消令牌)
            video_info = self.get_video_info(url, cancellation_token)
            title = video_info.get('title', 'video')
            
            # 處理檔名
            filename_prefix = options.get('filename_prefix', '')
            if filename_prefix:
                title = FilenameManager.add_prefix(title, filename_prefix)
                
            # 清理檔名
            platform = video_info.get('platform', '')
            clean_title = FilenameManager.clean_filename_for_platform(title, platform)
            
            # 生成唯一檔名 (標題 + ID)
            video_id = video_info.get('id', 'video')
            self.current_task.video_id = video_id
            self.current_task.title = clean_title
            
            # 檢查檔案是否已存在，若存在則加上序號（如 -2）
            base_name = f"{clean_title} [{video_id}]"
            suffix = ""
            counter = 1
            import glob
            while True:
                candidate = f"{base_name}{suffix}.*"
                # 搜尋資料夾中是否有任何檔案匹配該名稱（不限副檔名）
                existing = glob.glob(os.path.join(output_path, candidate))
                # 過濾掉暫存檔
                valid_existing = [e for e in existing if not e.endswith(('.part', '.ytdl', '.temp'))]
                if not valid_existing:
                    break
                counter += 1
                suffix = f"-{counter}"
            
            # 使用 %(ext)s 作為模板
            filename_template = f"{base_name}{suffix}.%(ext)s"
            
            # 設置 yt-dlp 選項
            ydl_opts = self._build_ydl_options(output_path, filename_template, options, logger)
            ydl_opts['progress_hooks'] = [self._progress_hook]
            
            # 檢查 FFmpeg
            if options.get('auto_merge', True):
                ffmpeg_path = self.ffmpeg_manager.get_ffmpeg_path()
                if ffmpeg_path:
                    ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_path)
                else:
                    logger.warning("未找到 FFmpeg，合併功能可能失效")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 取得預計輸出檔名
                try:
                    full_filename = ydl.prepare_filename(video_info)
                    self.current_task.filename = os.path.basename(full_filename)
                except Exception as e:
                    logger.warning(f"無法預先取得檔名: {e}")
                
                # 檢查進度回調
                def check_cancellation():
                    if cancellation_token and cancellation_token.is_cancelled():
                        raise OperationCancelledException("操作已取消")
                
                # 直接處理已獲取的資訊，跳過重複擷取網頁的步驟
                self._update_status(DownloadStatus.DOWNLOADING, "正在連結數據流...")
                ydl.process_video_result(video_info, download=True)
                
            # 檢查最終取消狀態
            if cancellation_token and cancellation_token.is_cancelled():
                raise OperationCancelledException("操作已取消")
                
            # 完成
            self.current_task.end_time = time.time()
            self._update_status(DownloadStatus.COMPLETED, "下載完成")
            
            return self.current_task.filename
            
        except OperationCancelledException:
            self._update_status(DownloadStatus.CANCELLED, "下載已取消")
            raise
            
        except Exception as e:
            error_msg = str(e)
            # logger.error(f"下載失敗: {error_msg}")
            self._update_status(DownloadStatus.FAILED, error_msg)
            raise Exception(f"下載失敗: {error_msg}")
            
        finally:
            if self.current_task and not self.current_task.end_time:
                self.current_task.end_time = time.time()
                
    def _build_ydl_options(self, output_path: str, filename_template: str, 
                          options: Dict[str, Any], logger: Any = None) -> Dict[str, Any]:
        """構建 yt-dlp 選項"""
        
        # 基本選項
        ydl_opts = {
            'outtmpl': os.path.join(output_path, filename_template),
            'format': self._get_format_selector(options),
            'writesubtitles': options.get('download_subtitles', False),
            'writeautomaticsub': options.get('download_auto_subtitles', False),
            'logger': logger,
            'noplaylist': True,
            'cachedir': False,
            'no_mtime': True,
            'noprogress': False,
            
            # 性能與穩定性平衡設定
            'concurrent_fragment_downloads': 5, 
            'nocheckcertificate': True,
            'socket_timeout': 30,
            'source_address': '0.0.0.0', # 強制 IPv4 避免連線逾時
            'retries': 3,
            'ignoreerrors': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'], # 優先使用行動版客戶端，較少遇到網頁版 429
                }
            },
            'buffersize': 1024 * 256,
        }
        
        # 網路避障設定 (代理/延遲)
        proxy = options.get('proxy', '').strip()
        if proxy:
            ydl_opts['proxy'] = proxy
            
        if options.get('use_random_delay', False):
            # 隨機延遲 5~15 秒，降低連線頻率
            ydl_opts.update({
                'sleep_interval': 5,
                'max_sleep_interval': 15,
                'sleep_interval_requests': 2,
            })
            
        # 移除手動旋轉 UA 邏輯，讓 yt-dlp 依照 player_client 自動配對正確的 UA，避免特徵不符被抓
        pass
        
        # 帳號授權 (Cookies from browser)
        browser = options.get('browser', 'none')
        if browser and browser != 'none':
            ydl_opts['cookiesfrombrowser'] = (browser,)
        
        # 品質與格式
        quality = options.get('quality', 'best')
        if quality == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': options.get('audio_format', 'mp3'),
                    'preferredquality': '192',
                }]
            })
        else:
            # 視頻格式
            video_format = options.get('video_format', 'mp4')
            if video_format != 'best':
                ydl_opts['merge_output_format'] = video_format
        
        return ydl_opts
        
    def _get_format_selector(self, options: Dict[str, Any]) -> str:
        """獲取格式選擇器"""
        quality = options.get('quality', 'best')
        
        if quality == 'best':
            return 'best[height<=1080]/best'
        elif quality == 'audio':
            return 'bestaudio/best'
        elif quality.endswith('p'):
            height = quality[:-1]
            return f'best[height<={height}]/best'
        else:
            return 'best'
            
    def cancel_download(self):
        """取消下載"""
        if self.cancellation_token:
            self.cancellation_token.cancel()
            
    def get_current_task(self) -> Optional[DownloadTask]:
        """獲取當前任務"""
        return self.current_task
        
    def is_downloading(self) -> bool:
        """檢查是否正在下載"""
        return (self.current_task and 
                self.current_task.status in [DownloadStatus.EXTRACTING, 
                                           DownloadStatus.DOWNLOADING, 
                                           DownloadStatus.MERGING])