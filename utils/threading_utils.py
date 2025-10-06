#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
執行緒工具
背景執行緒、事件旗標、安全停止
"""

import threading
import queue
import time
from typing import Callable, Any, Optional
from logging_config import get_logger

logger = get_logger(__name__)

class SafeThread(threading.Thread):
    """安全的執行緒類，支援異常處理和優雅停止"""
    
    def __init__(self, target=None, args=(), kwargs=None, name=None, daemon=True):
        super().__init__(target=target, args=args, kwargs=kwargs or {}, name=name, daemon=daemon)
        self._stop_event = threading.Event()
        self._exception = None
        self._result = None
        
    def run(self):
        """執行緒主函數"""
        try:
            if self._target:
                self._result = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self._exception = e
            logger.error(f"執行緒 {self.name} 發生異常: {e}", exc_info=True)
            
    def stop(self):
        """停止執行緒"""
        self._stop_event.set()
        
    def is_stopped(self):
        """檢查是否已停止"""
        return self._stop_event.is_set()
        
    def get_result(self):
        """獲取執行結果"""
        if self._exception:
            raise self._exception
        return self._result
        
    def get_exception(self):
        """獲取異常"""
        return self._exception

class ThreadPool:
    """簡單的執行緒池"""
    
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.workers = []
        self.task_queue = queue.Queue()
        self.shutdown = False
        
        # 啟動工作執行緒
        for i in range(max_workers):
            worker = SafeThread(target=self._worker, name=f"Worker-{i}")
            worker.start()
            self.workers.append(worker)
            
    def _worker(self):
        """工作執行緒函數"""
        while not self.shutdown:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:  # 停止信號
                    break
                    
                func, args, kwargs, callback = task
                try:
                    result = func(*args, **kwargs)
                    if callback:
                        callback(result, None)
                except Exception as e:
                    if callback:
                        callback(None, e)
                finally:
                    self.task_queue.task_done()
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"工作執行緒異常: {e}")
                
    def submit(self, func, *args, callback=None, **kwargs):
        """提交任務"""
        if not self.shutdown:
            self.task_queue.put((func, args, kwargs, callback))
            
    def shutdown_pool(self):
        """關閉執行緒池"""
        self.shutdown = True
        
        # 發送停止信號
        for _ in self.workers:
            self.task_queue.put(None)
            
        # 等待所有執行緒結束
        for worker in self.workers:
            worker.join(timeout=5)

class ProgressReporter:
    """進度報告器"""
    
    def __init__(self, callback: Callable[[float, str], None]):
        self.callback = callback
        self.last_update = 0
        self.update_interval = 0.1  # 100ms
        
    def report(self, progress: float, message: str = ""):
        """報告進度"""
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            try:
                self.callback(progress, message)
                self.last_update = current_time
            except Exception as e:
                logger.error(f"進度回調異常: {e}")

class CancellationToken:
    """取消令牌"""
    
    def __init__(self):
        self._cancelled = threading.Event()
        
    def cancel(self):
        """取消操作"""
        self._cancelled.set()
        
    def is_cancelled(self):
        """檢查是否已取消"""
        return self._cancelled.is_set()
        
    def throw_if_cancelled(self):
        """如果已取消則拋出異常"""
        if self.is_cancelled():
            raise OperationCancelledException("操作已取消")

class OperationCancelledException(Exception):
    """操作取消異常"""
    pass

class BackgroundTask:
    """背景任務管理器"""
    
    def __init__(self, target, args=(), kwargs=None, 
                 progress_callback=None, completion_callback=None):
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        
        self.thread = None
        self.cancellation_token = CancellationToken()
        self.progress_reporter = None
        
        if progress_callback:
            self.progress_reporter = ProgressReporter(progress_callback)
            
    def start(self):
        """啟動任務"""
        if self.thread and self.thread.is_alive():
            return False
            
        def wrapper():
            try:
                # 將取消令牌和進度報告器傳遞給目標函數
                kwargs = self.kwargs.copy()
                kwargs['cancellation_token'] = self.cancellation_token
                if self.progress_reporter:
                    kwargs['progress_reporter'] = self.progress_reporter
                    
                result = self.target(*self.args, **kwargs)
                
                if self.completion_callback:
                    self.completion_callback(result, None)
                    
            except OperationCancelledException:
                if self.completion_callback:
                    self.completion_callback(None, "已取消")
            except Exception as e:
                logger.error(f"背景任務異常: {e}", exc_info=True)
                if self.completion_callback:
                    self.completion_callback(None, str(e))
                    
        self.thread = SafeThread(target=wrapper, name="BackgroundTask")
        self.thread.start()
        return True
        
    def cancel(self):
        """取消任務"""
        self.cancellation_token.cancel()
        
    def is_running(self):
        """檢查是否正在運行"""
        return self.thread and self.thread.is_alive()
        
    def wait(self, timeout=None):
        """等待任務完成"""
        if self.thread:
            self.thread.join(timeout)
            return not self.thread.is_alive()
        return True

def run_in_background(func, *args, **kwargs):
    """在背景執行函數的裝飾器"""
    def decorator(callback=None):
        def wrapper():
            try:
                result = func(*args, **kwargs)
                if callback:
                    callback(result, None)
            except Exception as e:
                if callback:
                    callback(None, e)
                    
        thread = SafeThread(target=wrapper)
        thread.start()
        return thread
        
    return decorator