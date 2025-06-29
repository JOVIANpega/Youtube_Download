#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSL 修復和 yt-dlp 問題修復模組
"""

import os
import sys
import ssl
import subprocess
import platform
import urllib.request
import json
import time

def apply_ssl_fix():
    """應用 SSL 證書修復"""
    try:
        # 方法 1: 使用不驗證的 SSL 上下文
        ssl._create_default_https_context = ssl._create_unverified_context
        print("已應用 SSL 修復 (不驗證 SSL 上下文)")
        
        # 方法 2: 設置環境變數
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        print("已設置環境變數 PYTHONHTTPSVERIFY=0")
        
        # 方法 3: 禁用 urllib 的 SSL 驗證
        import urllib3
        urllib3.disable_warnings()
        print("已禁用 urllib3 警告")
        
        return True
    except Exception as e:
        print(f"SSL 修復失敗: {str(e)}")
        return False

def check_ytdlp_version():
    """檢查 yt-dlp 版本"""
    try:
        import yt_dlp
        version = yt_dlp.version.__version__
        print(f"當前 yt-dlp 版本: {version}")
        return version
    except Exception as e:
        print(f"無法獲取 yt-dlp 版本: {str(e)}")
        return None

def update_ytdlp():
    """更新 yt-dlp"""
    try:
        import yt_dlp
        current_version = yt_dlp.version.__version__
        print(f"當前 yt-dlp 版本: {current_version}")
        
        # 使用 yt-dlp 內部更新機制
        try:
            yt_dlp.update.update_ytdlp()
            print("yt-dlp 已更新")
            return True
        except:
            # 如果內部更新失敗，嘗試使用 pip
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
                print("yt-dlp 已通過 pip 更新")
                return True
            except:
                print("無法更新 yt-dlp")
                return False
    except Exception as e:
        print(f"更新 yt-dlp 時出錯: {str(e)}")
        return False

def test_youtube_connection():
    """測試與 YouTube 的連接"""
    try:
        # 禁用證書驗證
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # 測試連接
        req = urllib.request.Request(
            "https://www.youtube.com/",
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
        )
        
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            data = response.read()
            if data:
                print("成功連接到 YouTube")
                return True
            else:
                print("連接到 YouTube 但無法獲取數據")
                return False
    except Exception as e:
        print(f"無法連接到 YouTube: {str(e)}")
        return False

def fix_all():
    """應用所有修復"""
    print("正在應用所有修復...")
    
    # 應用 SSL 修復
    ssl_fixed = apply_ssl_fix()
    print(f"SSL 修復: {'成功' if ssl_fixed else '失敗'}")
    
    # 檢查 yt-dlp 版本
    version = check_ytdlp_version()
    print(f"yt-dlp 版本檢查: {version if version else '失敗'}")
    
    # 測試 YouTube 連接
    youtube_ok = test_youtube_connection()
    print(f"YouTube 連接測試: {'成功' if youtube_ok else '失敗'}")
    
    return ssl_fixed and version and youtube_ok

if __name__ == "__main__":
    fix_all() 