#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本資訊
版本常數＋打包用 version-file
"""

# 版本資訊
VERSION = "20260818"
VERSION_TUPLE = (20260818, 0, 0, 0)
AUTHOR = "YouTube Downloader Team"
DESCRIPTION = "多平台視頻下載器 - 支援多行狀態顯示與檔名前綴"
COPYRIGHT = "Copyright © 2024"

# PyInstaller 版本資訊
VERSION_INFO = {
    'version': VERSION_TUPLE,
    'description': DESCRIPTION,
    'copyright': COPYRIGHT,
    'product_name': 'YouTube Downloader',
    'file_description': '多平台視頻下載器',
    'internal_name': 'youtube_downloader',
    'original_filename': 'youtube_downloader.exe',
    'company_name': AUTHOR,
}

# 構建資訊
BUILD_DATE = "2026-08-18"
BUILD_TYPE = "Release"

def get_version_string():
    """獲取完整版本字串"""
    return f"{VERSION} ({BUILD_TYPE})"

def get_about_text():
    """獲取關於文字"""
    return f"""
{DESCRIPTION}
版本：{VERSION}
構建日期：{BUILD_DATE}
{COPYRIGHT}

支援平台：
• YouTube
• Bilibili  
• TikTok/抖音
• Instagram
• Facebook
• X (Twitter)
• 微博
• 快手
等多個平台

技術棧：
• Python + Tkinter
• yt-dlp
• FFmpeg
• 多執行緒下載
"""