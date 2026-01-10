#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歷史記錄存儲服務
負責歷史記錄的持久化讀寫與統計
"""

import json
import os
from datetime import datetime
from logging_config import get_logger
from constants import HISTORY_FILE

logger = get_logger(__name__)

class HistoryStore:
    """歷史記錄管理類"""
    
    def __init__(self, data_file=None):
        self.data_file = data_file or HISTORY_FILE
        self._ensure_data_dir()
        self.history = self._load()
        
    def _ensure_data_dir(self):
        """確保數據目錄存在"""
        data_dir = os.path.dirname(os.path.abspath(self.data_file))
        if data_dir and not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"無法建立數據目錄: {e}")
            
    def _load(self):
        """從 JSON 載入歷史記錄"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"載入歷史記錄失敗: {e}")
                return []
        return []
        
    def _save(self):
        """保存到 JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存歷史記錄失敗: {e}")
            
    def add_record(self, record):
        """添加一條歷史記錄"""
        # 確保記錄格式正確
        default_record = {
            'url': '',
            'title': '未知',
            'platform': '未知',
            'filename': '',
            'size': '未知',
            'quality': '未知',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': '成功'
        }
        default_record.update(record)
        self.history.insert(0, default_record)  # 最新在前面
        # 限制歷史記錄數量，防止檔案過大
        if len(self.history) > 500:
            self.history = self.history[:500]
        self._save()
        
    def get_history(self):
        """獲取所有歷史記錄"""
        return self.history
        
    def clear_history(self):
        """清空所有歷史記錄"""
        self.history = []
        self._save()
        
    def delete_record(self, index):
        """刪除指定索引的記錄"""
        if 0 <= index < len(self.history):
            self.history.pop(index)
            self._save()
            return True
        return False
        
    def get_stats(self):
        """獲取統計信息"""
        stats = {
            'total_count': len(self.history),
            'platform_counts': {},
            'successful_count': 0
        }
        
        for record in self.history:
            platform = record.get('platform', '未知')
            stats['platform_counts'][platform] = stats['platform_counts'].get(platform, 0) + 1
            if record.get('status') == '成功':
                stats['successful_count'] += 1
                
        return stats
