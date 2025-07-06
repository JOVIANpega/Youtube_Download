#!/usr/bin/env python3
"""
YouTube 下載器 - 公用工具函數
"""

import sys
import os
import ssl
import traceback
import urllib.request
import subprocess
import datetime

def log(message):
    """輸出日誌"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # 保存到日誌檔案
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"downloader_{datetime.datetime.now().strftime('%Y-%m-%d')}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    except Exception as e:
        print(f"無法寫入日誌檔案: {str(e)}")

def get_system_info():
    """獲取系統信息"""
    try:
        info = {
            "platform": sys.platform,
            "python_version": sys.version,
            "os_name": os.name,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # 獲取 yt-dlp 版本
        try:
            import yt_dlp
            info["yt_dlp_version"] = getattr(yt_dlp.version, "__version__", "未知")
        except ImportError:
            info["yt_dlp_version"] = "未安裝"
        
        # 獲取更多詳細的系統信息
        if hasattr(sys, "getwindowsversion") and callable(sys.getwindowsversion):
            try:
                win_ver = sys.getwindowsversion()
                info["windows_version"] = f"{win_ver.major}.{win_ver.minor}.{win_ver.build}"
            except:
                pass
        
        # 獲取 CPU 和記憶體信息
        try:
            import psutil
            info["cpu_count"] = psutil.cpu_count(logical=False)
            info["cpu_logical_count"] = psutil.cpu_count(logical=True)
            mem = psutil.virtual_memory()
            info["total_memory_gb"] = round(mem.total / (1024**3), 2)
            info["available_memory_gb"] = round(mem.available / (1024**3), 2)
        except ImportError:
            # psutil 模組不可用
            pass
        
        return info
    except Exception as e:
        log(f"獲取系統信息失敗: {str(e)}")
        return {"error": str(e)}

def create_error_log(error_info, url, format_option, resolution, output_path):
    """創建錯誤日誌"""
    try:
        # 確保日誌目錄存在
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 創建錯誤報告
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        error_log_file = os.path.join(log_dir, f"error_log_{timestamp}.txt")
        
        # 系統信息
        system_info = get_system_info()
        
        # 下載設定
        download_settings = {
            "url": url,
            "format": format_option,
            "resolution": resolution,
            "output_path": output_path
        }
        
        # 寫入錯誤日誌
        with open(error_log_file, "w", encoding="utf-8") as f:
            f.write("=== YouTube 下載器錯誤報告 ===\n\n")
            f.write(f"時間: {timestamp}\n\n")
            
            f.write("=== 系統信息 ===\n")
            for key, value in system_info.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            f.write("=== 下載設定 ===\n")
            for key, value in download_settings.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            f.write("=== 錯誤信息 ===\n")
            f.write(f"{error_info}\n\n")
            
            f.write("=== 完整錯誤追蹤 ===\n")
            f.write(traceback.format_exc())
            
            # 附加診斷信息
            f.write("\n=== 網路診斷 ===\n")
            try:
                f.write("正在檢查網絡連接...\n")
                # 嘗試連接到 YouTube
                response = urllib.request.urlopen("https://www.youtube.com", timeout=5)
                f.write(f"YouTube 網站可訪問，狀態碼: {response.getcode()}\n")
            except Exception as e:
                f.write(f"無法連接到 YouTube: {str(e)}\n")
            
            f.write("\n=== FFmpeg 診斷 ===\n")
            try:
                ffmpeg_path = "ffmpeg"
                result = subprocess.run([ffmpeg_path, "-version"], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE, 
                                        text=True, 
                                        timeout=5)
                f.write(f"FFmpeg 版本: {result.stdout.splitlines()[0] if result.stdout else '未知'}\n")
            except Exception as e:
                f.write(f"FFmpeg 診斷失敗: {str(e)}\n")
            
        return error_log_file
    except Exception as e:
        print(f"創建錯誤日誌失敗: {str(e)}")
        return None

def apply_ssl_fix():
    """應用SSL修復（V1.55特色功能）"""
    log("自動套用SSL證書修復...")
    try:
        # 模擬SSL設定
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl._create_default_https_context = lambda: ssl_context
        log("SSL證書驗證已停用，這可以解決某些SSL錯誤")
        return True
    except Exception as e:
        log(f"SSL修復遇到問題: {e}")
        return False

def format_size(size_bytes):
    """格式化檔案大小"""
    if size_bytes is None or size_bytes < 0:
        return "未知"
    
    try:
        # 將浮點數轉換為整數以避免格式化錯誤
        size_bytes = int(size_bytes)
    except (ValueError, TypeError):
        return "未知"
    
    # 格式化大小
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            if unit == 'B':
                return f"{size_bytes} {unit}"
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} PB"

def format_time(seconds):
    """格式化時間（秒數轉為時分秒）"""
    if seconds is None or seconds < 0:
        return "--:--:--"
    
    try:
        # 將浮點數轉換為整數以避免格式化錯誤
        seconds = int(seconds)
    except (ValueError, TypeError):
        return "--:--:--"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def sanitize_filename(filename):
    """清理檔案名稱，移除不合法字符"""
    # 移除不合法字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # 移除前後空白
    filename = filename.strip()
    
    # 如果檔名為空，使用預設名稱
    if not filename:
        filename = "video"
    
    return filename 