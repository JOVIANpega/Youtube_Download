#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日誌配置
統一 logging（輸出 logs/app.log）
"""

import logging
import logging.handlers
import os
from constants import LOG_FORMAT, LOG_DATE_FORMAT, LOG_FILE, MAX_LOG_SIZE, LOG_BACKUP_COUNT, LOGS_DIR

def setup_logging():
    """設置日誌系統"""
    # 確保日誌目錄存在
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # 創建根日誌器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 清除現有處理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 創建格式器
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    
    # 文件處理器（輪轉日誌）
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, 
        maxBytes=MAX_LOG_SIZE, 
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name):
    """獲取指定名稱的日誌器"""
    return logging.getLogger(name)