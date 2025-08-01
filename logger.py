#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日誌功能模組
負責實現日誌記錄和管理
"""

import os
import sys
import logging
import datetime
from pathlib import Path


class Logger:
    """日誌管理器類，處理應用程式的日誌記錄"""
    
    def __init__(self, log_level=logging.INFO, log_to_console=True, log_to_file=True):
        """初始化日誌管理器"""
        self.logger = logging.getLogger("YTDownloader")
        self.logger.setLevel(log_level)
        self.formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # 避免重複添加處理器
        if not self.logger.handlers:
            if log_to_console:
                self._setup_console_handler()
            
            if log_to_file:
                self._setup_file_handler()
    
    def _setup_console_handler(self):
        """設置控制台日誌處理器"""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """設置檔案日誌處理器"""
        # 確保日誌目錄存在
        log_dir = self._get_log_directory()
        os.makedirs(log_dir, exist_ok=True)
        
        # 創建日誌檔案名稱 (包含日期)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"ytdownloader_{date_str}.log")
        
        # 設置檔案處理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
    
    def _get_log_directory(self):
        """獲取日誌目錄路徑"""
        if hasattr(sys, '_MEIPASS'):  # PyInstaller打包環境
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).parent
        
        return os.path.join(base_dir, "logs")
    
    def debug(self, message):
        """記錄調試信息"""
        self.logger.debug(message)
    
    def info(self, message):
        """記錄一般信息"""
        self.logger.info(message)
    
    def warning(self, message):
        """記錄警告信息"""
        self.logger.warning(message)
    
    def error(self, message):
        """記錄錯誤信息"""
        self.logger.error(message)
    
    def critical(self, message):
        """記錄嚴重錯誤信息"""
        self.logger.critical(message)
    
    def exception(self, message):
        """記錄異常信息，包含堆疊追蹤"""
        self.logger.exception(message)


# 全局日誌管理器實例
logger = Logger() 