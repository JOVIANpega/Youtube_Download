#!/usr/bin/env python3
"""
使用者偏好管理
User Preferences Management
ユーザー設定管理
사용자 설정 관리
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class UserPreferences:
    def __init__(self, config_file: str = "user_preferences.json"):
        """初始化使用者偏好管理器"""
        self.config_file = config_file
        self.preferences = self.load_preferences()
    
    def load_preferences(self) -> Dict[str, Any]:
        """載入使用者偏好設定"""
        default_preferences = {
            # 下載設定
            "download_path": str(Path.home() / "Downloads"),
            "default_format": "影片",
            "default_resolution": "自動選擇最佳",
            "extract_audio_only": False,
            
            # 介面設定
            "window_width": 1000,
            "window_height": 800,
            "window_x": None,
            "window_y": None,
            "language": "zh_TW",
            
            # 下載歷史
            "recent_urls": [],
            "download_history": [],
            
            # 應用程式設定
            "auto_start_download": False,
            "show_progress_notifications": True,
            "minimize_to_tray": False,
            
            # 網路設定
            "max_retries": 3,
            "timeout": 30,
            "use_proxy": False,
            "proxy_url": "",
            
            # 檔案命名
            "filename_template": "%(title)s.%(ext)s",
            "add_timestamp": False,
            "sanitize_filename": True,
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_prefs = json.load(f)
                    # 合併載入的設定與預設設定
                    default_preferences.update(loaded_prefs)
        except Exception as e:
            print(f"載入偏好設定失敗: {e}")
        
        return default_preferences
    
    def save_preferences(self) -> bool:
        """儲存使用者偏好設定"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"儲存偏好設定失敗: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """獲取偏好設定值"""
        return self.preferences.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """設定偏好設定值"""
        self.preferences[key] = value
        return self.save_preferences()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """批量更新偏好設定"""
        self.preferences.update(updates)
        return self.save_preferences()
    
    # 下載路徑相關方法
    def get_download_path(self) -> str:
        """獲取下載路徑"""
        path = self.get("download_path", str(Path.home() / "Downloads"))
        # 確保路徑存在
        Path(path).mkdir(parents=True, exist_ok=True)
        return path
    
    def set_download_path(self, path: str) -> bool:
        """設定下載路徑"""
        return self.set("download_path", path)
    
    # 最近使用的 URL 相關方法
    def add_recent_url(self, url: str) -> bool:
        """添加最近使用的 URL"""
        recent_urls = self.get("recent_urls", [])
        # 移除重複的 URL
        if url in recent_urls:
            recent_urls.remove(url)
        # 添加到開頭
        recent_urls.insert(0, url)
        # 只保留最近 10 個
        recent_urls = recent_urls[:10]
        return self.set("recent_urls", recent_urls)
    
    def get_recent_urls(self) -> list:
        """獲取最近使用的 URL 列表"""
        return self.get("recent_urls", [])
    
    # 下載歷史相關方法
    def add_download_history(self, url: str, title: str, format: str, success: bool) -> bool:
        """添加下載歷史"""
        history = self.get("download_history", [])
        import datetime
        entry = {
            "url": url,
            "title": title,
            "format": format,
            "success": success,
            "timestamp": datetime.datetime.now().isoformat()
        }
        history.insert(0, entry)
        # 只保留最近 50 個記錄
        history = history[:50]
        return self.set("download_history", history)
    
    def get_download_history(self) -> list:
        """獲取下載歷史"""
        return self.get("download_history", [])
    
    # 視窗位置相關方法
    def save_window_geometry(self, x: int, y: int, width: int, height: int) -> bool:
        """儲存視窗幾何資訊"""
        return self.update({
            "window_x": x,
            "window_y": y,
            "window_width": width,
            "window_height": height
        })
    
    def get_window_geometry(self) -> tuple:
        """獲取視窗幾何資訊"""
        return (
            self.get("window_x"),
            self.get("window_y"),
            self.get("window_width", 1000),
            self.get("window_height", 800)
        )
    
    # 格式偏好相關方法
    def get_default_format(self) -> str:
        """獲取預設格式"""
        return self.get("default_format", "影片")
    
    def set_default_format(self, format: str) -> bool:
        """設定預設格式"""
        return self.set("default_format", format)
    
    def get_default_resolution(self) -> str:
        """獲取預設解析度"""
        return self.get("default_resolution", "自動選擇最佳")
    
    def set_default_resolution(self, resolution: str) -> bool:
        """設定預設解析度"""
        return self.set("default_resolution", resolution)
    
    # 下載完成提醒設定
    def get_show_completion_dialog(self) -> bool:
        """獲取下載完成後是否顯示提醒視窗"""
        return self.get("show_completion_dialog", True)
    
    def set_show_completion_dialog(self, show: bool) -> bool:
        """設定下載完成後是否顯示提醒視窗"""
        return self.set("show_completion_dialog", show)
    
    # 檔案名稱前綴設定
    def get_filename_prefix(self) -> str:
        """獲取檔案名稱前綴"""
        return self.get("filename_prefix", "TEST-")
    
    def set_filename_prefix(self, prefix: str) -> bool:
        """設定檔案名稱前綴"""
        # 同時添加到前綴歷史
        if prefix:
            self.add_prefix_history(prefix)
        return self.set("filename_prefix", prefix)
    
    def get_prefix_history(self) -> list:
        """獲取前綴歷史記錄"""
        return self.get("prefix_history", [])
    
    def add_prefix_history(self, prefix: str) -> bool:
        """添加前綴到歷史記錄"""
        if not prefix:
            return False
            
        prefix_history = self.get("prefix_history", [])
        # 移除重複的前綴
        if prefix in prefix_history:
            prefix_history.remove(prefix)
        # 添加到開頭
        prefix_history.insert(0, prefix)
        # 只保留最近 10 個
        prefix_history = prefix_history[:10]
        return self.set("prefix_history", prefix_history)
        
    def remove_prefix_history(self, prefix: str) -> bool:
        """從歷史記錄中移除前綴"""
        prefix_history = self.get("prefix_history", [])
        if prefix in prefix_history:
            prefix_history.remove(prefix)
            return self.set("prefix_history", prefix_history)
        return False
    
    # 統計資訊
    def get_statistics(self) -> Dict[str, Any]:
        """獲取使用統計"""
        history = self.get_download_history()
        total_downloads = len(history)
        successful_downloads = len([h for h in history if h.get("success", False)])
        failed_downloads = total_downloads - successful_downloads
        
        # 計算格式使用統計
        format_stats = {}
        for entry in history:
            format_type = entry.get("format", "未知")
            format_stats[format_type] = format_stats.get(format_type, 0) + 1
        
        return {
            "total_downloads": total_downloads,
            "successful_downloads": successful_downloads,
            "failed_downloads": failed_downloads,
            "success_rate": (successful_downloads / total_downloads * 100) if total_downloads > 0 else 0,
            "format_statistics": format_stats,
            "favorite_formats": sorted(format_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    # 重置設定
    def reset_to_defaults(self) -> bool:
        """重置為預設設定"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            self.preferences = self.load_preferences()
            return True
        except Exception as e:
            print(f"重置設定失敗: {e}")
            return False
    
    # 匯出/匯入設定
    def export_preferences(self, export_path: str) -> bool:
        """匯出偏好設定"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"匯出設定失敗: {e}")
            return False
    
    def import_preferences(self, import_path: str) -> bool:
        """匯入偏好設定"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_prefs = json.load(f)
            self.preferences.update(imported_prefs)
            return self.save_preferences()
        except Exception as e:
            print(f"匯入設定失敗: {e}")
            return False 