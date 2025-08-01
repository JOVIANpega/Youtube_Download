#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增強的設定管理器
處理所有GUI設定的保存和載入
"""

import json
import os
from pathlib import Path
from logger import logger

class EnhancedSetupManager:
    """增強的設定管理器"""
    
    def __init__(self, config_file="setup.json"):
        self.config_file = config_file
        self.settings = {}
        self.default_settings = {
            # 基本設定
            "download_path": "M:/TEMP",
            "filename_prefix": "",
            "auto_merge": True,
            "format_option": "最高品質",
            "resolution": "720P",
            
            # UI設定
            "font_size": 11,
            "window_geometry": {
                "width": 800,
                "height": 600,
                "x": 100,
                "y": 100
            },
            "window_maximized": False,
            
            # 網路設定
            "timeout": 30,
            "retry_count": 3,
            "max_concurrent_downloads": 5,
            
            # 平台設定
            "platform_settings": {
                "youtube_enabled": True,
                "bilibili_enabled": True,
                "tiktok_enabled": True,
                "douyin_enabled": False,
                "instagram_enabled": False,
                "facebook_enabled": False
            },
            
            # 平台URL設定
            "platform_urls": {
                "youtube": "https://www.y2mate.com/",
                "bilibili": "https://www.videodownloaderpro.net/bilibili-video-downloader.html",
                "tiktok": "https://ssstik.io/",
                "douyin": "https://www.douyin.com/",
                "instagram": "https://www.w3toys.com/",
                "facebook": "https://www.getfvid.com/"
            },
            
            # 進階設定
            "advanced_settings": {
                "keep_temp_files": False,
                "auto_open_folder": True,
                "auto_play_video": False,
                "show_download_complete_dialog": True,
                "auto_clear_completed": True,
                "download_subtitles": False,
                "prefer_mp4": True
            },
            
            # 最近使用
            "recent_downloads": [],
            "recent_paths": [],
            
            # 統計資訊
            "statistics": {
                "total_downloads": 0,
                "successful_downloads": 0,
                "failed_downloads": 0,
                "total_size_downloaded": 0
            }
        }
        
        self.load_settings()
    
    def load_settings(self):
        """載入設定"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # 合併設定，確保所有預設值都存在
                self.settings = self._merge_settings(self.default_settings, loaded_settings)
                logger.info(f"設定已從 {self.config_file} 載入")
            else:
                self.settings = self.default_settings.copy()
                self.save_settings()
                logger.info(f"使用預設設定並創建 {self.config_file}")
                
        except Exception as e:
            logger.error(f"載入設定失敗: {str(e)}")
            self.settings = self.default_settings.copy()
    
    def _merge_settings(self, default, loaded):
        """遞歸合併設定，確保所有預設值都存在"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_settings(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def save_settings(self):
        """保存設定"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info(f"設定已儲存到 {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存設定失敗: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """獲取設定值"""
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """設置設定值"""
        keys = key.split('.')
        setting = self.settings
        
        # 導航到最後一層
        for k in keys[:-1]:
            if k not in setting:
                setting[k] = {}
            setting = setting[k]
        
        # 設置值
        setting[keys[-1]] = value
        logger.debug(f"設定已更新: {key} = {value}")
    
    def get_window_geometry(self):
        """獲取視窗幾何資訊"""
        return self.get("window_geometry", self.default_settings["window_geometry"])
    
    def set_window_geometry(self, width, height, x, y):
        """設置視窗幾何資訊"""
        self.set("window_geometry.width", width)
        self.set("window_geometry.height", height)
        self.set("window_geometry.x", x)
        self.set("window_geometry.y", y)
    
    def is_window_maximized(self):
        """檢查視窗是否最大化"""
        return self.get("window_maximized", False)
    
    def set_window_maximized(self, maximized):
        """設置視窗最大化狀態"""
        self.set("window_maximized", maximized)
    
    def get_font_size(self):
        """獲取字體大小"""
        return self.get("font_size", 11)
    
    def set_font_size(self, size):
        """設置字體大小"""
        self.set("font_size", size)
    
    def add_recent_download(self, url, filename, file_path):
        """添加最近下載記錄"""
        recent = self.get("recent_downloads", [])
        
        # 移除重複項目
        recent = [item for item in recent if item.get("url") != url]
        
        # 添加新項目到開頭
        recent.insert(0, {
            "url": url,
            "filename": filename,
            "file_path": file_path,
            "timestamp": self._get_timestamp()
        })
        
        # 限制最多保存20個
        recent = recent[:20]
        
        self.set("recent_downloads", recent)
    
    def add_recent_path(self, path):
        """添加最近使用路徑"""
        recent_paths = self.get("recent_paths", [])
        
        # 移除重複項目
        if path in recent_paths:
            recent_paths.remove(path)
        
        # 添加到開頭
        recent_paths.insert(0, path)
        
        # 限制最多保存10個
        recent_paths = recent_paths[:10]
        
        self.set("recent_paths", recent_paths)
    
    def update_statistics(self, success, file_size=0):
        """更新統計資訊"""
        stats = self.get("statistics", self.default_settings["statistics"])
        
        stats["total_downloads"] += 1
        if success:
            stats["successful_downloads"] += 1
            stats["total_size_downloaded"] += file_size
        else:
            stats["failed_downloads"] += 1
        
        self.set("statistics", stats)
    
    def reset_to_defaults(self):
        """重置為預設設定"""
        # 保留統計資訊和最近記錄
        stats = self.get("statistics", {})
        recent_downloads = self.get("recent_downloads", [])
        recent_paths = self.get("recent_paths", [])
        
        self.settings = self.default_settings.copy()
        
        # 恢復統計資訊和最近記錄
        if stats:
            self.set("statistics", stats)
        if recent_downloads:
            self.set("recent_downloads", recent_downloads)
        if recent_paths:
            self.set("recent_paths", recent_paths)
        
        logger.info("設定已重置為預設值")
    
    def _get_timestamp(self):
        """獲取當前時間戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def export_settings(self, file_path):
        """匯出設定到指定文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info(f"設定已匯出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"匯出設定失敗: {str(e)}")
            return False
    
    def import_settings(self, file_path):
        """從指定文件匯入設定"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # 合併設定
            self.settings = self._merge_settings(self.default_settings, imported_settings)
            self.save_settings()
            
            logger.info(f"設定已從 {file_path} 匯入")
            return True
        except Exception as e:
            logger.error(f"匯入設定失敗: {str(e)}")
            return False

# 創建全局實例
enhanced_setup_manager = EnhancedSetupManager()
