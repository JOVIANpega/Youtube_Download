#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用工具函數模組
提供各種通用功能和工具函數
"""

import os
import re
import sys
import ssl
import time
import subprocess
from pathlib import Path

from logger import logger


def apply_ssl_fix():
    """應用SSL證書驗證修復，解決SSL相關錯誤"""
    logger.info("應用SSL證書驗證修復")
    try:
        # 創建不驗證證書的SSL上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 設置為默認HTTPS上下文
        ssl._create_default_https_context = lambda: ssl_context
        
        # 嘗試禁用urllib3警告
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except ImportError:
            pass  # 如果未安裝urllib3則忽略
        
        logger.info("SSL證書驗證已停用，這可以解決某些SSL錯誤")
        return True
    except Exception as e:
        logger.error(f"SSL修復套用失敗: {e}")
        return False


def format_size(bytes_value):
    """格式化文件大小為人類可讀格式"""
    if bytes_value < 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while bytes_value >= 1024 and i < len(size_names) - 1:
        bytes_value /= 1024.0
        i += 1
    
    return f"{bytes_value:.2f} {size_names[i]}"


def format_time(seconds):
    """格式化時間（秒數）為人類可讀格式"""
    if seconds is None or seconds < 0:
        return "--:--"
    
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def sanitize_filename(filename):
    """清理檔案名稱，移除不合法字元"""
    # 移除 Windows 不允許的檔案名稱字元
    illegal_chars = r'[<>:"/\\|?*]'
    safe_name = re.sub(illegal_chars, '_', filename)
    
    # 移除開頭和結尾的空格和點
    safe_name = safe_name.strip('. ')
    
    # 限制檔案名長度
    if len(safe_name) > 200:
        safe_name = safe_name[:197] + "..."
    
    return safe_name


def get_resource_path(relative_path):
    """獲取資源檔案的絕對路徑，支援PyInstaller打包"""
    if hasattr(sys, '_MEIPASS'):  # PyInstaller打包環境
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    
    return os.path.join(base_path, relative_path)


def create_error_log(error_info, url, format_option, resolution, output_path):
    """創建錯誤日誌檔案"""
    try:
        # 確保日誌目錄存在
        log_dir = os.path.join(Path(__file__).parent, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 創建錯誤日誌檔案名稱
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(log_dir, f"error_{timestamp}.log")
        
        # 寫入錯誤信息
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"=== 影片下載器錯誤報告 ===\n\n")
            f.write(f"時間: {timestamp}\n")
            f.write(f"URL: {url}\n")
            f.write(f"格式: {format_option}\n")
            f.write(f"解析度: {resolution}\n")
            f.write(f"輸出路徑: {output_path}\n\n")
            f.write(f"錯誤信息: {error_info}\n")
        
        logger.info(f"已創建錯誤日誌: {log_file}")
        return log_file
    
    except Exception as e:
        logger.error(f"創建錯誤日誌失敗: {e}")
        return None


def open_file(path):
    """用預設應用程式開啟檔案"""
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])
        
        logger.info(f"已開啟檔案: {path}")
        return True
    except Exception as e:
        logger.error(f"開啟檔案失敗: {e}")
        return False


def open_folder(path):
    """開啟資料夾"""
    try:
        if os.path.isfile(path):
            path = os.path.dirname(path)
        
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])
        
        logger.info(f"已開啟資料夾: {path}")
        return True
    except Exception as e:
        logger.error(f"開啟資料夾失敗: {e}")
        return False


def check_requirements():
    """檢查必要的依賴是否已安裝"""
    try:
        # 檢查 yt-dlp
        import yt_dlp
        logger.info(f"yt-dlp 版本: {yt_dlp.version.__version__}")
        
        # 檢查 PySide6
        import PySide6
        logger.info(f"PySide6 版本: {PySide6.__version__}")
        
        return True
    except ImportError as e:
        logger.error(f"缺少必要的依賴: {e}")
        return False 