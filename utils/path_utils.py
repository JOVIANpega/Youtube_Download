#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路徑工具
get_resource_path()、路徑合法化與容錯
"""

import os
import sys
import re
import unicodedata
from pathlib import Path

def get_resource_path(relative_path):
    """獲取資源檔案路徑，兼容 PyInstaller 打包"""
    try:
        # PyInstaller 創建的臨時資料夾
        base_path = sys._MEIPASS
    except AttributeError:
        # 開發環境
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def sanitize_filename(filename):
    """清理檔名，移除非法字符"""
    # 移除控制字符
    filename = ''.join(char for char in filename if unicodedata.category(char)[0] != 'C')
    
    # 替換 Windows 非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, '_', filename)
    
    # 移除前後空格和點
    filename = filename.strip(' .')
    
    # 限制長度
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    
    # 避免保留名稱
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        filename = f"_{filename}"
    
    return filename or "untitled"

def ensure_directory(path):
    """確保目錄存在"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"創建目錄失敗 {path}: {e}")
        return False

def get_safe_path(base_path, filename):
    """獲取安全的檔案路徑，處理重複檔名"""
    filename = sanitize_filename(filename)
    full_path = os.path.join(base_path, filename)
    
    if not os.path.exists(full_path):
        return full_path
    
    # 處理重複檔名
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name}-{counter}{ext}"
        new_path = os.path.join(base_path, new_filename)
        if not os.path.exists(new_path):
            return new_path
        counter += 1
        
        # 防止無限循環
        if counter > 9999:
            import time
            timestamp = int(time.time())
            new_filename = f"{name}-{timestamp}{ext}"
            return os.path.join(base_path, new_filename)

def is_valid_path(path):
    """檢查路徑是否有效"""
    try:
        # 檢查路徑格式
        Path(path)
        
        # 檢查是否為絕對路徑
        if not os.path.isabs(path):
            return False
            
        # 檢查父目錄是否存在或可創建
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            try:
                os.makedirs(parent, exist_ok=True)
            except:
                return False
                
        return True
    except:
        return False

def get_file_size_str(size_bytes):
    """將位元組大小轉換為可讀字串"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_available_space(path):
    """獲取指定路徑的可用空間（位元組）"""
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                ctypes.pointer(free_bytes),
                None,
                None
            )
            return free_bytes.value
        else:  # Unix/Linux/Mac
            statvfs = os.statvfs(path)
            return statvfs.f_frsize * statvfs.f_bavail
    except:
        return 0