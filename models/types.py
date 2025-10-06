#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料模型和類型定義
任務狀態列舉、資料模型
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import time

class TaskStatus(Enum):
    """任務狀態"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DownloadQuality(Enum):
    """下載品質"""
    BEST = "best"
    HD_1080P = "1080p"
    HD_720P = "720p"
    SD_480P = "480p"
    SD_360P = "360p"
    AUDIO_ONLY = "audio"

class Platform(Enum):
    """支援的平台"""
    YOUTUBE = "YouTube"
    BILIBILI = "Bilibili"
    TIKTOK = "TikTok"
    DOUYIN = "抖音"
    INSTAGRAM = "Instagram"
    FACEBOOK = "Facebook"
    TWITTER = "X (Twitter)"
    WEIBO = "微博"
    KUAISHOU = "快手"
    UNKNOWN = "未知"

@dataclass
class VideoInfo:
    """視頻資訊"""
    title: str = ""
    url: str = ""
    platform: str = ""
    duration: int = 0  # 秒
    uploader: str = ""
    upload_date: str = ""
    view_count: int = 0
    description: str = ""
    thumbnail_url: str = ""
    video_id: str = ""
    
    def get_duration_str(self) -> str:
        """獲取格式化的持續時間"""
        if self.duration <= 0:
            return "未知"
            
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
            
    def get_view_count_str(self) -> str:
        """獲取格式化的觀看次數"""
        if self.view_count <= 0:
            return "未知"
        elif self.view_count >= 1000000:
            return f"{self.view_count / 1000000:.1f}M"
        elif self.view_count >= 1000:
            return f"{self.view_count / 1000:.1f}K"
        else:
            return str(self.view_count)

@dataclass
class DownloadProgress:
    """下載進度"""
    percentage: float = 0.0
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0.0  # bytes/sec
    eta: int = 0  # seconds
    status: TaskStatus = TaskStatus.PENDING
    message: str = ""
    
    def get_speed_str(self) -> str:
        """獲取格式化的下載速度"""
        if self.speed <= 0:
            return "0 B/s"
            
        units = ['B/s', 'KB/s', 'MB/s', 'GB/s']
        size = self.speed
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        return f"{size:.1f} {units[unit_index]}"
        
    def get_eta_str(self) -> str:
        """獲取格式化的預估時間"""
        if self.eta <= 0:
            return "未知"
            
        if self.eta < 60:
            return f"{self.eta}秒"
        elif self.eta < 3600:
            minutes = self.eta // 60
            seconds = self.eta % 60
            return f"{minutes}分{seconds}秒"
        else:
            hours = self.eta // 3600
            minutes = (self.eta % 3600) // 60
            return f"{hours}小時{minutes}分"

@dataclass
class DownloadOptions:
    """下載選項"""
    quality: DownloadQuality = DownloadQuality.BEST
    output_path: str = ""
    filename_prefix: str = ""
    video_format: str = "mp4"
    audio_format: str = "mp3"
    download_subtitles: bool = False
    download_auto_subtitles: bool = False
    keep_video: bool = True
    keep_audio: bool = False
    auto_merge: bool = True
    retry_attempts: int = 3
    timeout: int = 300
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'quality': self.quality.value if isinstance(self.quality, DownloadQuality) else self.quality,
            'output_path': self.output_path,
            'filename_prefix': self.filename_prefix,
            'video_format': self.video_format,
            'audio_format': self.audio_format,
            'download_subtitles': self.download_subtitles,
            'download_auto_subtitles': self.download_auto_subtitles,
            'keep_video': self.keep_video,
            'keep_audio': self.keep_audio,
            'auto_merge': self.auto_merge,
            'retry_attempts': self.retry_attempts,
            'timeout': self.timeout,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadOptions':
        """從字典創建"""
        quality = data.get('quality', 'best')
        if isinstance(quality, str):
            try:
                quality = DownloadQuality(quality)
            except ValueError:
                quality = DownloadQuality.BEST
                
        return cls(
            quality=quality,
            output_path=data.get('output_path', ''),
            filename_prefix=data.get('filename_prefix', ''),
            video_format=data.get('video_format', 'mp4'),
            audio_format=data.get('audio_format', 'mp3'),
            download_subtitles=data.get('download_subtitles', False),
            download_auto_subtitles=data.get('download_auto_subtitles', False),
            keep_video=data.get('keep_video', True),
            keep_audio=data.get('keep_audio', False),
            auto_merge=data.get('auto_merge', True),
            retry_attempts=data.get('retry_attempts', 3),
            timeout=data.get('timeout', 300),
        )

@dataclass
class DownloadTask:
    """下載任務"""
    id: str
    url: str
    video_info: Optional[VideoInfo] = None
    options: Optional[DownloadOptions] = None
    progress: Optional[DownloadProgress] = None
    created_time: float = 0.0
    started_time: float = 0.0
    completed_time: float = 0.0
    output_filename: str = ""
    error_message: str = ""
    
    def __post_init__(self):
        if self.created_time == 0.0:
            self.created_time = time.time()
        if self.progress is None:
            self.progress = DownloadProgress()
        if self.options is None:
            self.options = DownloadOptions()
            
    def get_elapsed_time(self) -> float:
        """獲取已用時間"""
        if self.started_time == 0.0:
            return 0.0
        end_time = self.completed_time if self.completed_time > 0 else time.time()
        return end_time - self.started_time
        
    def get_elapsed_time_str(self) -> str:
        """獲取格式化的已用時間"""
        elapsed = self.get_elapsed_time()
        if elapsed <= 0:
            return "0秒"
            
        if elapsed < 60:
            return f"{elapsed:.0f}秒"
        elif elapsed < 3600:
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            return f"{minutes}分{seconds}秒"
        else:
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            return f"{hours}小時{minutes}分"
            
    def is_active(self) -> bool:
        """檢查任務是否活躍"""
        return self.progress.status in [TaskStatus.RUNNING, TaskStatus.PENDING]
        
    def is_completed(self) -> bool:
        """檢查任務是否完成"""
        return self.progress.status == TaskStatus.COMPLETED
        
    def is_failed(self) -> bool:
        """檢查任務是否失敗"""
        return self.progress.status == TaskStatus.FAILED

@dataclass
class AppSettings:
    """應用程式設定"""
    window_geometry: str = "500x400+100+100"
    font_size: int = 12
    download_path: str = ""
    quality_preference: str = "best"
    filename_prefix: str = ""
    auto_merge: bool = True
    keep_video: bool = True
    keep_audio: bool = False
    max_concurrent_downloads: int = 3
    retry_attempts: int = 3
    download_timeout: int = 300
    show_advanced_options: bool = False
    auto_open_download_folder: bool = False
    check_for_updates: bool = True
    language: str = "zh_TW"
    theme: str = "default"
    log_level: str = "INFO"
    ffmpeg_path: str = ""
    recent_urls: List[str] = None
    favorite_prefixes: List[str] = None
    
    def __post_init__(self):
        if self.recent_urls is None:
            self.recent_urls = []
        if self.favorite_prefixes is None:
            self.favorite_prefixes = ['', '[YouTube]', '[Bilibili]', '[TikTok]']