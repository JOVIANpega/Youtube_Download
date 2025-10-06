#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理
設定 JSON 讀寫（即時保存/載入）
"""

import json
import os
from typing import Dict, Any, Optional
from constants import SETTINGS_FILE, CONFIG_DIR, DEFAULT_DOWNLOAD_PATH, DEFAULT_FONT_SIZE
from utils.path_utils import ensure_directory
from logging_config import get_logger

logger = get_logger(__name__)

class SettingsManager:
    """設定管理器"""
    
    def __init__(self):
        self.settings_file = SETTINGS_FILE
        self.default_settings = self._get_default_settings()
        self._ensure_config_dir()
        
    def _get_default_settings(self) -> Dict[str, Any]:
        """獲取預設設定"""
        return {
            'window_geometry': '500x400+100+100',
            'font_size': DEFAULT_FONT_SIZE,
            'download_path': os.path.abspath(DEFAULT_DOWNLOAD_PATH),
            'quality_preference': 'best',
            'filename_prefix': '',
            'settings_split_pos': 320,
            'auto_merge': True,
            'keep_video': True,
            'keep_audio': False,
            'max_concurrent_downloads': 3,
            'retry_attempts': 3,
            'download_timeout': 300,
            'show_advanced_options': False,
            'auto_open_download_folder': False,
            'check_for_updates': True,
            'language': 'zh_TW',
            'theme': 'default',
            'log_level': 'INFO',
            'ffmpeg_path': '',
            'recent_urls': [],
            'favorite_prefixes': ['', 'per- ', 'per best- ', 'per best2- ', 'per best3- ', 'per nice- '],
            'quality_options': {
                'video_format': 'mp4',
                'audio_format': 'mp3',
                'prefer_free_formats': True,
            },
            'ui_preferences': {
                'show_progress_details': True,
                'show_download_speed': True,
                'show_eta': True,
                'auto_clear_completed': False,
            }
        }
        
    def _ensure_config_dir(self):
        """確保配置目錄存在"""
        ensure_directory(CONFIG_DIR)
        
    def load_settings(self) -> Dict[str, Any]:
        """載入設定"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    
                # 合併預設設定和已保存的設定
                settings = self.default_settings.copy()
                settings.update(saved_settings)
                
                # 驗證設定
                settings = self._validate_settings(settings)
                
                logger.info("設定載入成功")
                return settings
            else:
                logger.info("設定檔不存在，使用預設設定")
                return self.default_settings.copy()
                
        except Exception as e:
            logger.error(f"載入設定失敗: {e}")
            return self.default_settings.copy()
            
    def save_settings(self, settings: Dict[str, Any]):
        """保存設定"""
        try:
            self._ensure_config_dir()
            
            # 驗證設定
            settings = self._validate_settings(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
            logger.info("設定保存成功")
            
        except Exception as e:
            logger.error(f"保存設定失敗: {e}")
            raise
            
    def get_setting(self, key: str, default: Any = None) -> Any:
        """獲取單個設定值"""
        settings = self.load_settings()
        return settings.get(key, default)
        
    def set_setting(self, key: str, value: Any):
        """設置單個設定值"""
        settings = self.load_settings()
        settings[key] = value
        self.save_settings(settings)
        
    def update_settings(self, updates: Dict[str, Any]):
        """批量更新設定"""
        settings = self.load_settings()
        settings.update(updates)
        self.save_settings(settings)
        
    def reset_settings(self):
        """重置為預設設定"""
        try:
            if os.path.exists(self.settings_file):
                os.remove(self.settings_file)
            logger.info("設定已重置")
        except Exception as e:
            logger.error(f"重置設定失敗: {e}")
            
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """驗證設定值"""
        validated = settings.copy()
        
        # 驗證字體大小
        font_size = validated.get('font_size', DEFAULT_FONT_SIZE)
        if not isinstance(font_size, int) or font_size < 8 or font_size > 20:
            validated['font_size'] = DEFAULT_FONT_SIZE
            
        # 驗證下載路徑
        download_path = validated.get('download_path', '')
        if not download_path or not isinstance(download_path, str):
            validated['download_path'] = os.path.abspath(DEFAULT_DOWNLOAD_PATH)
        else:
            # 確保路徑存在
            try:
                ensure_directory(download_path)
            except:
                validated['download_path'] = os.path.abspath(DEFAULT_DOWNLOAD_PATH)
                
        # 驗證並發下載數
        max_concurrent = validated.get('max_concurrent_downloads', 3)
        if not isinstance(max_concurrent, int) or max_concurrent < 1 or max_concurrent > 10:
            validated['max_concurrent_downloads'] = 3
            
        # 驗證重試次數
        retry_attempts = validated.get('retry_attempts', 3)
        if not isinstance(retry_attempts, int) or retry_attempts < 0 or retry_attempts > 10:
            validated['retry_attempts'] = 3
            
        # 驗證超時時間
        timeout = validated.get('download_timeout', 300)
        if not isinstance(timeout, int) or timeout < 30 or timeout > 3600:
            validated['download_timeout'] = 300
            
        # 驗證最近 URL 列表
        recent_urls = validated.get('recent_urls', [])
        if not isinstance(recent_urls, list):
            validated['recent_urls'] = []
        else:
            # 限制數量
            validated['recent_urls'] = recent_urls[:20]
            
        return validated
        
    def add_recent_url(self, url: str):
        """添加最近使用的 URL"""
        if not url:
            return
            
        settings = self.load_settings()
        recent_urls = settings.get('recent_urls', [])
        
        # 移除重複項
        if url in recent_urls:
            recent_urls.remove(url)
            
        # 添加到開頭
        recent_urls.insert(0, url)
        
        # 限制數量
        recent_urls = recent_urls[:20]
        
        settings['recent_urls'] = recent_urls
        self.save_settings(settings)
        
    def get_recent_urls(self) -> list:
        """獲取最近使用的 URL"""
        return self.get_setting('recent_urls', [])
        
    def clear_recent_urls(self):
        """清空最近使用的 URL"""
        self.set_setting('recent_urls', [])