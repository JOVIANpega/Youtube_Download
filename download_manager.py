#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
下載管理模組
負責管理下載任務的創建、執行、暫停、取消等操作
"""

import os
import time
import uuid
import threading
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal

from logger import logger
from config import config_manager
from download_thread import DownloadThread


class DownloadStatus(Enum):
    """下載狀態枚舉"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadTask:
    """下載任務數據類"""
    id: str
    url: str
    output_path: str
    format_option: str
    resolution: str
    prefix: str
    auto_merge: bool
    status: DownloadStatus = DownloadStatus.PENDING
    progress: int = 0
    speed: str = "--"
    eta: str = "--"
    title: str = ""
    error_message: str = ""
    file_path: str = ""
    platform_name: str = "未知"
    platform_icon: str = "❓"
    platform_color: str = "#999999"
    created_time: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    thread: Optional[DownloadThread] = None


class DownloadManager(QObject):
    """下載管理器類"""
    
    # 信號定義
    task_added = Signal(str)                       # 任務ID
    task_started = Signal(str)                     # 任務ID
    task_progress = Signal(str, int, str, str)     # 任務ID, 進度百分比, 速度, ETA
    task_paused = Signal(str)                      # 任務ID
    task_resumed = Signal(str)                     # 任務ID
    task_cancelled = Signal(str)                   # 任務ID
    task_completed = Signal(str, str)              # 任務ID, 檔案路徑
    task_failed = Signal(str, str)                 # 任務ID, 錯誤訊息
    platform_detected = Signal(str, str, str)      # 任務ID, 平台名稱, URL
    
    def __init__(self):
        """初始化下載管理器"""
        super().__init__()
        self.tasks: Dict[str, DownloadTask] = {}  # 任務ID -> 任務對象
        self.active_downloads: Dict[str, DownloadThread] = {}  # 任務ID -> 下載線程
        self.completed_urls: set = set()  # 已完成下載的URL集合
        self.max_concurrent = config_manager.get("max_concurrent_downloads", 5)
        self.lock = threading.Lock()  # 線程鎖，用於保護共享資源
    
    def add_task(self, url: str, output_path: str, format_option: str, 
                resolution: str, prefix: str = "", auto_merge: bool = True) -> str:
        """
        添加下載任務
        返回任務ID
        """
        with self.lock:
            # 檢查是否已經下載過相同URL
            if url in self.completed_urls:
                logger.warning(f"URL已經下載過: {url}")
                return ""
            
            # 生成唯一任務ID
            task_id = str(uuid.uuid4())
            
            # 創建任務對象
            task = DownloadTask(
                id=task_id,
                url=url,
                output_path=output_path,
                format_option=format_option,
                resolution=resolution,
                prefix=prefix,
                auto_merge=auto_merge
            )
            
            # 添加到任務字典
            self.tasks[task_id] = task
            logger.info(f"添加下載任務: {task_id} - {url}")
            
            # 發送信號
            self.task_added.emit(task_id)
            
        # 在鎖外嘗試立即開始下載
        self._start_pending_tasks()

        return task_id
    
    def _start_pending_tasks(self):
        """開始等待中的任務"""
        try:
            with self.lock:
                # 檢查是否達到最大同時下載數量
                if len(self.active_downloads) >= self.max_concurrent:
                    return

                # 獲取所有等待中的任務
                pending_tasks = [t for t in self.tasks.values()
                               if t.status == DownloadStatus.PENDING and t.id not in self.active_downloads]

                # 按創建時間排序
                pending_tasks.sort(key=lambda t: t.created_time)

                # 計算可以開始的任務數量
                available_slots = self.max_concurrent - len(self.active_downloads)
                tasks_to_start = pending_tasks[:available_slots]

                # 開始這些任務
                for task in tasks_to_start:
                    self._start_task_unlocked(task.id)
        except Exception as e:
            logger.error(f"_start_pending_tasks錯誤: {e}")
            return
    
    def _start_task(self, task_id: str) -> bool:
        """
        開始下載任務
        返回是否成功啟動
        """
        with self.lock:
            return self._start_task_unlocked(task_id)

    def _start_task_unlocked(self, task_id: str) -> bool:
        """
        開始下載任務（不使用鎖）
        返回是否成功啟動
        """
        if task_id not in self.tasks:
            logger.error(f"任務不存在: {task_id}")
            return False

        task = self.tasks[task_id]

        # 檢查是否已經在下載
        if task_id in self.active_downloads:
            logger.warning(f"任務已在下載中: {task_id}")
            return False

        # 創建下載線程
        thread = DownloadThread(
            task.url,
            task.output_path,
            task.format_option,
            task.resolution,
            task.prefix,
            task.auto_merge
        )

        # 連接信號（使用Qt.QueuedConnection避免阻塞）
        from PySide6.QtCore import Qt

        # 創建綁定的回調函數避免lambda閉包問題
        def make_progress_callback(tid):
            return lambda msg, percent, speed, eta: self._on_progress(tid, msg, percent, speed, eta)

        def make_finished_callback(tid):
            return lambda success, msg, file_path: self._on_finished(tid, success, msg, file_path)

        def make_platform_callback(tid):
            return lambda platform, url: self._on_platform_detected(tid, platform, url)

        thread.progress.connect(make_progress_callback(task_id), Qt.QueuedConnection)
        thread.finished.connect(make_finished_callback(task_id), Qt.QueuedConnection)
        thread.platform_detected.connect(make_platform_callback(task_id), Qt.QueuedConnection)

        # 更新任務狀態
        task.status = DownloadStatus.DOWNLOADING
        task.start_time = time.time()
        task.thread = thread

        # 添加到活動下載
        self.active_downloads[task_id] = thread

        # 啟動線程
        thread.start()

        logger.info(f"開始下載任務: {task_id}")
        self.task_started.emit(task_id)

        return True
    
    def pause_task(self, task_id: str) -> bool:
        """
        暫停下載任務
        返回是否成功暫停
        """
        with self.lock:
            if task_id not in self.active_downloads:
                logger.warning(f"無法暫停，任務不在下載中: {task_id}")
                return False
            
            thread = self.active_downloads[task_id]
            thread.pause()
            
            task = self.tasks[task_id]
            task.status = DownloadStatus.PAUSED
            
            logger.info(f"暫停下載任務: {task_id}")
            self.task_paused.emit(task_id)
            
            return True
    
    def resume_task(self, task_id: str) -> bool:
        """
        恢復下載任務
        返回是否成功恢復
        """
        with self.lock:
            if task_id not in self.active_downloads:
                logger.warning(f"無法恢復，任務不在下載中: {task_id}")
                return False
            
            thread = self.active_downloads[task_id]
            thread.resume()
            
            task = self.tasks[task_id]
            task.status = DownloadStatus.DOWNLOADING
            
            logger.info(f"恢復下載任務: {task_id}")
            self.task_resumed.emit(task_id)
            
            return True
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消下載任務
        返回是否成功取消
        """
        with self.lock:
            if task_id not in self.tasks:
                logger.warning(f"無法取消，任務不存在: {task_id}")
                return False
            
            task = self.tasks[task_id]
            
            # 如果正在下載，停止線程
            if task_id in self.active_downloads:
                thread = self.active_downloads[task_id]
                thread.cancel()
                
                # 從活動下載中移除
                del self.active_downloads[task_id]
            
            # 更新任務狀態
            task.status = DownloadStatus.CANCELLED
            task.end_time = time.time()
            
            logger.info(f"取消下載任務: {task_id}")
            self.task_cancelled.emit(task_id)
            
            # 啟動等待中的任務
            self._start_pending_tasks()
            
            return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        移除下載任務
        返回是否成功移除
        """
        with self.lock:
            if task_id not in self.tasks:
                logger.warning(f"無法移除，任務不存在: {task_id}")
                return False
            
            # 如果正在下載，先取消任務
            if task_id in self.active_downloads:
                self.cancel_task(task_id)
            
            # 移除任務
            task = self.tasks.pop(task_id)
            
            # 如果是已完成的任務，添加到已完成URL集合
            if task.status == DownloadStatus.COMPLETED:
                self.completed_urls.add(task.url)
            
            logger.info(f"移除下載任務: {task_id}")
            
            # 啟動等待中的任務
            self._start_pending_tasks()
            
            return True
    
    def pause_all_tasks(self):
        """暫停所有下載中的任務"""
        with self.lock:
            for task_id in list(self.active_downloads.keys()):
                self.pause_task(task_id)
    
    def resume_all_tasks(self):
        """恢復所有暫停的任務"""
        with self.lock:
            # 找出所有暫停的任務
            paused_tasks = [task_id for task_id, task in self.tasks.items()
                          if task.status == DownloadStatus.PAUSED and task_id in self.active_downloads]
            
            for task_id in paused_tasks:
                self.resume_task(task_id)
    
    def cancel_all_tasks(self):
        """取消所有下載中和等待中的任務"""
        with self.lock:
            # 複製一個任務ID列表，避免在迭代時修改字典
            active_task_ids = list(self.active_downloads.keys())
            
            for task_id in active_task_ids:
                self.cancel_task(task_id)
            
            # 取消所有等待中的任務
            for task_id, task in self.tasks.items():
                if task.status == DownloadStatus.PENDING:
                    task.status = DownloadStatus.CANCELLED
                    task.end_time = time.time()
                    self.task_cancelled.emit(task_id)
    
    def clear_completed_tasks(self):
        """清除已完成、失敗或已取消的任務"""
        with self.lock:
            # 找出所有完成、失敗或取消的任務
            completed_task_ids = [
                task_id for task_id, task in self.tasks.items()
                if task.status in [
                    DownloadStatus.COMPLETED,
                    DownloadStatus.FAILED,
                    DownloadStatus.CANCELLED
                ]
            ]
            
            # 添加已完成的URL到集合中
            for task_id in completed_task_ids:
                task = self.tasks[task_id]
                if task.status == DownloadStatus.COMPLETED:
                    self.completed_urls.add(task.url)
                    
                # 移除任務
                del self.tasks[task_id]
            
            logger.info(f"清除了 {len(completed_task_ids)} 個已完成的任務")
    
    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """獲取任務詳情"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[DownloadTask]:
        """獲取所有任務"""
        return list(self.tasks.values())
    
    def get_tasks_by_status(self, status: DownloadStatus) -> List[DownloadTask]:
        """根據狀態獲取任務"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_download_statistics(self) -> Tuple[int, int, int, int, int]:
        """
        獲取下載統計數據
        返回: (總數, 下載中, 暫停中, 已完成, 失敗)
        """
        total = len(self.tasks)
        downloading = len([t for t in self.tasks.values() if t.status == DownloadStatus.DOWNLOADING])
        paused = len([t for t in self.tasks.values() if t.status == DownloadStatus.PAUSED])
        completed = len([t for t in self.tasks.values() if t.status == DownloadStatus.COMPLETED])
        failed = len([t for t in self.tasks.values() if t.status == DownloadStatus.FAILED])
        
        return total, downloading, paused, completed, failed
    
    def set_max_concurrent(self, max_concurrent: int):
        """設置最大同時下載數量"""
        if max_concurrent < 1:
            max_concurrent = 1
        
        self.max_concurrent = max_concurrent
        config_manager.set("max_concurrent_downloads", max_concurrent)
        config_manager.save_settings()
        
        # 如果當前活動下載數量小於新的最大值，嘗試啟動等待中的任務
        if len(self.active_downloads) < max_concurrent:
            self._start_pending_tasks()
    
    def _on_progress(self, task_id: str, message: str, percent: int, speed: str, eta: str):
        """處理下載進度更新"""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]

        # 更新任務進度資訊
        task.progress = percent
        task.speed = speed
        task.eta = eta

        # 更新任務標題（如果訊息包含標題）
        if "開始下載:" in message and ":" in message:
            task.title = message.split(":", 1)[1].strip()

        # 調試信息（已移除）

        # 發送進度信號
        self.task_progress.emit(task_id, percent, speed, eta)
    
    def _on_finished(self, task_id: str, success: bool, message: str, file_path: str):
        """處理下載完成"""
        with self.lock:
            if task_id not in self.tasks:
                return
                
            task = self.tasks[task_id]
            task.end_time = time.time()
            
            # 從活動下載中移除
            if task_id in self.active_downloads:
                del self.active_downloads[task_id]
            
            if success:
                # 下載成功
                task.status = DownloadStatus.COMPLETED
                task.progress = 100
                task.file_path = file_path
                
                # 如果消息包含標題，更新任務標題
                if ":" in message:
                    title = message.split(":", 1)[1].strip()
                    if title:
                        task.title = title
                
                # 添加到已完成URL集合
                self.completed_urls.add(task.url)
                
                logger.info(f"下載完成: {task_id} - {file_path}")
                self.task_completed.emit(task_id, file_path)
            else:
                # 下載失敗
                task.status = DownloadStatus.FAILED
                task.error_message = message
                
                logger.error(f"下載失敗: {task_id} - {message}")
                self.task_failed.emit(task_id, message)
            
            # 啟動等待中的任務
            self._start_pending_tasks()
    
    def _on_platform_detected(self, task_id: str, platform: str, url: str):
        """處理平台識別"""
        if task_id not in self.tasks:
            return
            
        task = self.tasks[task_id]
        
        # 更新任務的平台信息
        task.platform_name = platform
        
        # 根據平台設置圖標和顏色
        if platform == "YouTube":
            task.platform_icon = "▶"
            task.platform_color = "#ff0000"
        elif platform in ["TikTok", "抖音"]:
            task.platform_icon = "🎵"
            task.platform_color = "#000000"
        elif platform == "Facebook":
            task.platform_icon = "📘"
            task.platform_color = "#1877f2"
        elif platform == "Instagram":
            task.platform_icon = "📷"
            task.platform_color = "#e4405f"
        elif platform == "X":
            task.platform_icon = "🐦"
            task.platform_color = "#1da1f2"
        elif platform == "Bilibili":
            task.platform_icon = "📺"
            task.platform_color = "#00a1d6"
        elif platform == "Threads":
            task.platform_icon = "🧵"
            task.platform_color = "#000000"
        else:
            task.platform_icon = "❓"
            task.platform_color = "#999999"
        
        # 發送平台識別信號
        logger.info(f"識別到平台: {task_id} - {platform}")
        self.platform_detected.emit(task_id, platform, url)


# 全局下載管理器實例
download_manager = DownloadManager() 