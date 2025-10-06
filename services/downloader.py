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
                logger.error(f"進度回調錯誤: {e}")
                
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
                    
                # 更新速度和 ETA
                if 'speed' in d and d['speed']:
                    self.current_task.speed = d['speed']
                    
                if 'eta' in d and d['eta']:
                    self.current_task.eta = d['eta']
                    
                # 更新檔名
                if 'filename' in d:
                    self.current_task.filename = os.path.basename(d['filename'])
                    
                # 回調進度
                speed_str = f"{get_file_size_str(self.current_task.speed)}/s" if self.current_task.speed else ""
                eta_str = f"ETA: {self.current_task.eta}s" if self.current_task.eta else ""
                message = f"{speed_str} {eta_str}".strip()
                
                self._update_progress(self.current_task.progress, message)
                
            elif d['status'] == 'finished':
                self.current_task.filename = os.path.basename(d['filename'])
                self.current_task.progress = 100.0
                self._update_progress(100.0, "下載完成")
                
            elif d['status'] == 'error':
                self._update_status(DownloadStatus.FAILED, str(d.get('error', '未知錯誤')))
                
        except Exception as e:
            logger.error(f"進度鉤子錯誤: {e}")
            
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """獲取視頻資訊"""
        if yt_dlp is None:
            raise Exception("yt-dlp 未安裝，無法獲取視頻資訊")
            
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            return {
                'title': info.get('title', '未知標題'),
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
                progress_reporter: ProgressReporter = None) -> str:
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
                
            # 獲取視頻資訊
            video_info = self.get_video_info(url)
            title = video_info.get('title', 'video')
            
            # 處理檔名
            filename_prefix = options.get('filename_prefix', '')
            if filename_prefix:
                title = FilenameManager.add_prefix(title, filename_prefix)
                
            # 清理檔名
            platform = video_info.get('platform', '')
            clean_title = FilenameManager.clean_filename_for_platform(title, platform)
            
            # 生成唯一檔名
            base_filename = f"{clean_title}.%(ext)s"
            
            # 設置 yt-dlp 選項
            ydl_opts = self._build_ydl_options(output_path, base_filename, options)
            ydl_opts['progress_hooks'] = [self._progress_hook]
            
            # 檢查 FFmpeg
            if options.get('auto_merge', True):
                ffmpeg_path = self.ffmpeg_manager.get_ffmpeg_path()
                if ffmpeg_path:
                    ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_path)
                    
            # 開始下載
            self._update_status(DownloadStatus.DOWNLOADING, "開始下載...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 定期檢查取消狀態
                def check_cancellation():
                    if cancellation_token and cancellation_token.is_cancelled():
                        raise OperationCancelledException("操作已取消")
                        
                # 下載
                ydl.download([url])
                
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
            logger.error(f"下載失敗: {error_msg}")
            self._update_status(DownloadStatus.FAILED, error_msg)
            raise Exception(f"下載失敗: {error_msg}")
            
        finally:
            if self.current_task and not self.current_task.end_time:
                self.current_task.end_time = time.time()
                
    def _build_ydl_options(self, output_path: str, filename_template: str, 
                          options: Dict[str, Any]) -> Dict[str, Any]:
        """構建 yt-dlp 選項"""
        
        # 基本選項
        ydl_opts = {
            'outtmpl': os.path.join(output_path, filename_template),
            'format': self._get_format_selector(options),
            'writesubtitles': options.get('download_subtitles', False),
            'writeautomaticsub': options.get('download_auto_subtitles', False),
            'ignoreerrors': False,
            'no_warnings': False,
        }
        
        # 品質選項
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
                
        # 重試選項
        ydl_opts.update({
            'retries': options.get('retry_attempts', 3),
            'fragment_retries': options.get('retry_attempts', 3),
            'socket_timeout': options.get('timeout', 300),
        })
        
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