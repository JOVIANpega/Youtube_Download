#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
平台識別模組
用於識別URL所屬的平台，並提供平台特定的下載設定
"""

import re
from logger import logger


def identify_platform(url):
    """
    識別URL所屬的平台
    返回包含平台信息的字典
    """
    url_lower = url.lower().strip()
    
    # YouTube
    if any(domain in url_lower for domain in ["youtube.com", "youtu.be"]):
        logger.info(f"檢測到 YouTube 連結: {url}")
        return {
            "name": "YouTube",
            "icon": "▶",
            "color": "#ff0000",
            "needs_login": False,
            "download_options": {
                "format": "bestvideo+bestaudio/best",
                "prefer_mp4": True
            }
        }
    
    # TikTok/抖音
    elif any(domain in url_lower for domain in ["tiktok.com", "douyin.com", "vm.tiktok"]):
        if "douyin.com" in url_lower:
            platform_name = "抖音"
            needs_login = True  # 抖音需要cookies
        else:
            platform_name = "TikTok"
            needs_login = False

        logger.info(f"檢測到 {platform_name} 連結: {url}")
        return {
            "name": platform_name,
            "icon": "🎵",
            "color": "#000000",
            "needs_login": needs_login,
            "download_options": {
                "format": "bestvideo+bestaudio/best",
                "no_watermark": True
            }
        }
    
    # Facebook
    elif any(domain in url_lower for domain in ["facebook.com", "fb.com", "fb.watch"]):
        logger.info(f"檢測到 Facebook 連結: {url}")
        return {
            "name": "Facebook",
            "icon": "📘",
            "color": "#1877f2",
            "needs_login": True,
            "download_options": {
                "format": "best[height>=720][ext=mp4]/best[ext=mp4]/best"
            }
        }
    
    # Instagram
    elif "instagram.com" in url_lower:
        logger.info(f"檢測到 Instagram 連結: {url}")
        return {
            "name": "Instagram",
            "icon": "📷",
            "color": "#e4405f",
            "needs_login": True,
            "download_options": {
                "format": "best[ext=mp4]/best"
            }
        }
    
    # X/Twitter
    elif any(domain in url_lower for domain in ["twitter.com", "x.com"]):
        logger.info(f"檢測到 X/Twitter 連結: {url}")
        return {
            "name": "X",
            "icon": "🐦",
            "color": "#1da1f2",
            "needs_login": False,
            "download_options": {
                "format": "best[ext=mp4]/best"
            }
        }
    
    # Bilibili
    elif any(domain in url_lower for domain in ["bilibili.com", "b23.tv"]):
        logger.info(f"檢測到 Bilibili 連結: {url}")
        return {
            "name": "Bilibili",
            "icon": "📺",
            "color": "#00a1d6",
            "needs_login": False,
            "download_options": {
                "format": "bestvideo+bestaudio/best"
            }
        }
    
    # Threads
    elif "threads.net" in url_lower:
        logger.info(f"檢測到 Threads 連結: {url}")
        return {
            "name": "Threads",
            "icon": "🧵",
            "color": "#000000",
            "needs_login": True,
            "download_options": {
                "format": "best[ext=mp4]/best"
            }
        }
    
    # Threads
    elif "threads.com" in url_lower:
        logger.info(f"檢測到 Threads 連結: {url}")
        return {
            "name": "Threads",
            "icon": "🧵",
            "color": "#000000",
            "needs_login": True,
            "download_options": {
                "format": "best[ext=mp4]/best"
            }
        }

    # QQ影片
    elif "v.qq.com" in url_lower:
        logger.info(f"檢測到 QQ影片 連結: {url}")
        return {
            "name": "QQ影片",
            "icon": "🐧",
            "color": "#12b7f5",
            "needs_login": False,
            "download_options": {
                "format": "best[ext=mp4]/best"
            }
        }

    # 未知平台
    else:
        logger.warning(f"未知平台連結: {url}")
        return {
            "name": "未知",
            "icon": "❓",
            "color": "#999999",
            "needs_login": False,
            "download_options": {
                "format": "best"
            }
        }


def get_supported_platforms():
    """獲取支援的平台列表"""
    return [
        {
            "name": "YouTube",
            "icon": "▶",
            "color": "#ff0000",
            "url": "https://youtube.com"
        },
        {
            "name": "TikTok",
            "icon": "🎵",
            "color": "#000000",
            "url": "https://tiktok.com"
        },
        {
            "name": "抖音",
            "icon": "🎵",
            "color": "#000000",
            "url": "https://douyin.com"
        },
        {
            "name": "Facebook",
            "icon": "📘",
            "color": "#1877f2",
            "url": "https://facebook.com"
        },
        {
            "name": "Instagram",
            "icon": "📷",
            "color": "#e4405f",
            "url": "https://instagram.com"
        },
        {
            "name": "X",
            "icon": "🐦",
            "color": "#1da1f2",
            "url": "https://twitter.com"
        },
        {
            "name": "Bilibili",
            "icon": "📺",
            "color": "#00a1d6",
            "url": "https://bilibili.com"
        },
        {
            "name": "Threads",
            "icon": "🧵",
            "color": "#000000",
            "url": "https://threads.net"
        }
    ]


def validate_url(url):
    """驗證URL格式是否有效"""
    # 簡單的URL格式驗證
    url_pattern = re.compile(
        r'^(?:http|https)://'  # http:// 或 https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # 域名
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # 可選端口
        r'(?:/?|[/?]\S+)$', re.IGNORECASE  # 路徑和查詢參數
    )
    
    return bool(url_pattern.match(url)) 