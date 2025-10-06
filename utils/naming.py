#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔名處理
檔名前綴與重複處理（自動 -2/-3，相似度比對）
"""

import os
import re
import difflib
from utils.path_utils import sanitize_filename

class FilenameManager:
    """檔名管理器"""
    
    @staticmethod
    def add_prefix(filename, prefix):
        """添加前綴到檔名"""
        if not prefix:
            return filename
            
        # 清理前綴
        prefix = prefix.strip()
        if not prefix:
            return filename
            
        # 確保前綴以空格結尾（如果不是以特殊字符結尾）
        if not prefix.endswith((' ', '-', '_', ']', ')', '}')):
            prefix += ' '
            
        return f"{prefix}{filename}"
    
    @staticmethod
    def generate_unique_filename(directory, base_filename, max_attempts=9999):
        """生成唯一檔名，避免重複"""
        base_filename = sanitize_filename(base_filename)
        full_path = os.path.join(directory, base_filename)
        
        if not os.path.exists(full_path):
            return base_filename
            
        # 分離檔名和副檔名
        name, ext = os.path.splitext(base_filename)
        
        # 檢查是否已經有數字後綴
        match = re.search(r'-(\d+)$', name)
        if match:
            base_name = name[:match.start()]
            start_num = int(match.group(1)) + 1
        else:
            base_name = name
            start_num = 2
            
        # 嘗試生成唯一檔名
        for i in range(start_num, start_num + max_attempts):
            new_filename = f"{base_name}-{i}{ext}"
            new_path = os.path.join(directory, new_filename)
            
            if not os.path.exists(new_path):
                return new_filename
                
        # 如果仍然無法生成唯一檔名，使用時間戳
        import time
        timestamp = int(time.time())
        return f"{base_name}-{timestamp}{ext}"
    
    @staticmethod
    def find_similar_files(directory, target_filename, similarity_threshold=0.8):
        """查找相似的檔案"""
        if not os.path.exists(directory):
            return []
            
        target_name = os.path.splitext(target_filename)[0].lower()
        similar_files = []
        
        try:
            for filename in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, filename)):
                    file_name = os.path.splitext(filename)[0].lower()
                    similarity = difflib.SequenceMatcher(None, target_name, file_name).ratio()
                    
                    if similarity >= similarity_threshold:
                        similar_files.append({
                            'filename': filename,
                            'similarity': similarity,
                            'path': os.path.join(directory, filename)
                        })
                        
        except Exception as e:
            print(f"查找相似檔案時發生錯誤: {e}")
            
        # 按相似度排序
        similar_files.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_files
    
    @staticmethod
    def clean_filename_for_platform(filename, platform=None):
        """根據平台清理檔名"""
        # 基本清理
        filename = sanitize_filename(filename)
        
        # 移除常見的無用字符
        filename = re.sub(r'\s+', ' ', filename)  # 多個空格變一個
        filename = re.sub(r'[【】\[\]（）()]', '', filename)  # 移除括號
        filename = re.sub(r'[_-]+', '-', filename)  # 多個連字符變一個
        
        # 平台特定處理
        if platform == 'YouTube':
            # 移除 YouTube 特有的標記
            filename = re.sub(r'(?i)(youtube|yt)\s*[-_]?\s*', '', filename)
            
        elif platform == 'Bilibili':
            # 移除 Bilibili 特有的標記
            filename = re.sub(r'(?i)(bilibili|b站|哔哩哔哩)\s*[-_]?\s*', '', filename)
            
        elif platform == 'TikTok':
            # 移除 TikTok 特有的標記
            filename = re.sub(r'(?i)(tiktok|抖音)\s*[-_]?\s*', '', filename)
            
        # 最終清理
        filename = filename.strip(' -_.')
        
        return filename or "untitled"
    
    @staticmethod
    def extract_title_from_url(url):
        """從 URL 嘗試提取標題"""
        try:
            from urllib.parse import urlparse, unquote
            parsed = urlparse(url)
            
            # YouTube
            if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
                # 嘗試從查詢參數獲取
                if 'v=' in url:
                    return None  # 讓 yt-dlp 處理
                    
            # 從路徑提取
            path_parts = [part for part in parsed.path.split('/') if part]
            if path_parts:
                title = unquote(path_parts[-1])
                # 移除檔案副檔名
                title = re.sub(r'\.[a-zA-Z0-9]+$', '', title)
                # 替換連字符和下劃線為空格
                title = re.sub(r'[-_]+', ' ', title)
                return title.strip()
                
        except Exception:
            pass
            
        return None
    
    @staticmethod
    def format_duration_in_filename(duration_seconds):
        """將持續時間格式化為檔名友好的格式"""
        if not duration_seconds or duration_seconds <= 0:
            return ""
            
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        if hours > 0:
            return f"[{hours:02d}h{minutes:02d}m{seconds:02d}s]"
        else:
            return f"[{minutes:02d}m{seconds:02d}s]"