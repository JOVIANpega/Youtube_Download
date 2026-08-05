#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證工具
URL/平台識別、輸入校驗、placeholder 管理
"""

import re
import urllib.parse
from constants import SUPPORTED_PLATFORMS
import tkinter

class URLValidator:
    """URL 驗證器"""
    
    @staticmethod
    def is_valid_url(url):
        """檢查是否為有效的 URL"""
        if not url or not isinstance(url, str):
            return False
            
        url = url.strip()
        if not url:
            return False
            
        # 基本 URL 格式檢查
        url_pattern = re.compile(
            r'^https?://'  # http:// 或 https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # 可選端口
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
        return bool(url_pattern.match(url))
    
    @staticmethod
    def detect_platform(url):
        """檢測視頻平台"""
        if not URLValidator.is_valid_url(url):
            return None
            
        try:
            parsed = urllib.parse.urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '').replace('m.', '')
            
            for platform_domain, platform_name in SUPPORTED_PLATFORMS.items():
                if platform_domain in domain:
                    return platform_name
                    
        except Exception:
            pass
            
        return None
    
    @staticmethod
    def normalize_url(url):
        """標準化 URL"""
        if not url:
            return ""
            
        url = url.strip()
        
        # 如果沒有協議，添加 https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # 針對 Douyin 抖音的特別規則：
        # 如果網址包含 douyin.com 並且有 modal_id=
        # 例如 https://www.douyin.com/jingxuan?modal_id=7656733164362124571
        # 我們將其轉換成 https://www.douyin.com/video/{modal_id}
        if 'douyin.com' in url and 'modal_id=' in url:
            try:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)
                modal_id = params.get('modal_id')
                if modal_id:
                    m_id = modal_id[0]
                    url = f"https://www.douyin.com/video/{m_id}"
            except Exception:
                pass
            
        return url
    
    @staticmethod
    def extract_video_id(url):
        """提取視頻 ID（針對常見平台）"""
        if not url:
            return None
            
        # YouTube
        youtube_patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in youtube_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Bilibili
        bilibili_pattern = r'bilibili\.com/video/([a-zA-Z0-9]+)'
        match = re.search(bilibili_pattern, url)
        if match:
            return match.group(1)
            
        # TikTok
        tiktok_pattern = r'tiktok\.com/@[^/]+/video/(\d+)'
        match = re.search(tiktok_pattern, url)
        if match:
            return match.group(1)
            
        return None

class InputValidator:
    """輸入驗證器"""
    
    @staticmethod
    def validate_download_path(path):
        """驗證下載路徑"""
        if not path or not isinstance(path, str):
            return False, "路徑不能為空"
            
        path = path.strip()
        if not path:
            return False, "路徑不能為空"
            
        # 檢查路徑格式
        try:
            import os
            if not os.path.isabs(path):
                return False, "請提供絕對路徑"
                
            # 檢查父目錄是否存在
            parent_dir = os.path.dirname(path)
            if not os.path.exists(parent_dir):
                return False, f"父目錄不存在: {parent_dir}"
                
            # 檢查寫入權限
            if not os.access(parent_dir, os.W_OK):
                return False, "沒有寫入權限"
                
        except Exception as e:
            return False, f"路徑無效: {str(e)}"
            
        return True, ""
    
    @staticmethod
    def validate_filename_prefix(prefix):
        """驗證檔名前綴"""
        if not prefix:
            return True, ""
            
        # 檢查非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        if re.search(illegal_chars, prefix):
            return False, "前綴包含非法字符"
            
        # 檢查長度
        if len(prefix) > 50:
            return False, "前綴過長（最多50字符）"
            
        return True, ""

class PlaceholderManager:
    """佔位符管理器"""
    
    def __init__(self, entry_widget, placeholder_text, placeholder_color='grey'):
        self.entry = entry_widget
        self.placeholder_text = placeholder_text
        self.placeholder_color = placeholder_color
        
        # 安全地獲取顏色值
        try:
            # 嘗試獲取前景色
            self.default_color = entry_widget.cget('foreground')
        except (tkinter.TclError, AttributeError):
            try:
                # 嘗試獲取 fg 屬性
                self.default_color = entry_widget.cget('fg')
            except (tkinter.TclError, AttributeError):
                # 如果都失敗，使用預設顏色
                self.default_color = 'black'
        
        self.has_placeholder = True
        
        self.setup_placeholder()
        
    def setup_placeholder(self):
        """設置佔位符"""
        self.entry.insert(0, self.placeholder_text)
        self.entry.config(foreground=self.placeholder_color)
        
        self.entry.bind('<FocusIn>', self.on_focus_in)
        self.entry.bind('<FocusOut>', self.on_focus_out)
        
    def on_focus_in(self, event):
        """獲得焦點時"""
        if self.has_placeholder:
            self.entry.delete(0, 'end')
            self.entry.config(foreground=self.default_color)
            self.has_placeholder = False
            
    def on_focus_out(self, event):
        """失去焦點時"""
        if not self.entry.get().strip():
            self.entry.insert(0, self.placeholder_text)
            self.entry.config(foreground=self.placeholder_color)
            self.has_placeholder = True
            
    def get_value(self):
        """獲取實際值（排除佔位符）"""
        if self.has_placeholder:
            return ""
        return self.entry.get().strip()
        
    def set_value(self, value):
        """設置值"""
        self.entry.delete(0, 'end')
        if value:
            self.entry.insert(0, value)
            self.entry.config(foreground=self.default_color)
            self.has_placeholder = False
        else:
            self.entry.insert(0, self.placeholder_text)
            self.entry.config(foreground=self.placeholder_color)
            self.has_placeholder = True
            
    def clear(self):
        """清空內容"""
        self.set_value("")